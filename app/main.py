# app/main.py
import os
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from slack_bolt.adapter.fastapi import SlackRequestHandler
from slack_sdk import WebClient
from slack_sdk.oauth import AuthorizeUrlGenerator
from app.slack_events import app as bolt_app
from app.scheduler import start_scheduler
from dotenv import load_dotenv
import json
from uuid import uuid4
from db import save_installation, get_installation, save_response, update_installation
from slack_sdk.web.async_client import AsyncWebClient

from app.utils import send_standup_dm_to_team
from app.control_panel import build_control_panel_modal, trigger_days_modal, trigger_time_modal, select_channel_modal, response_window_modal

from standup_submission import standup_submission_modal


load_dotenv()
app = FastAPI()
handler = SlackRequestHandler(bolt_app)

CLIENT_ID = os.getenv("SLACK_CLIENT_ID")
CLIENT_SECRET = os.getenv("SLACK_CLIENT_SECRET")
SCOPES = ["commands", "chat:write", "im:write", "users:read", "channels:read"]
PUBLIC_URL = os.getenv("PUBLIC_URL")
REDIRECT_URI = f"{PUBLIC_URL}/slack/oauth_redirect"


@app.post("/slack/command")
async def slack_command(request: Request):
    form = await request.form()
    command = form.get("command")
    user_id = form.get("user_id")
    team_id = form.get("team_id")
    trigger_id = form.get("trigger_id")
    print('*********** received command ', command,
          ' from userid ', user_id, ' with team id ', team_id)
    if command == '/pulsecheck':
        print('Handling pulsecheck command')
        installation_info = get_installation(team_id)
        client = AsyncWebClient(installation_info.access_token)

        # Get all users
        users_resp = await client.users_list()
        this_user = next(
            (user for user in users_resp["members"] if user["id"] == user_id), None)
        print('user id ', user_id, ' this user ', this_user,
              ' installed by ', installation_info.installed_by)
        if not this_user.get("is_admin") and user_id != installation_info.installed_by:
            return {"response_type": "ephemeral", "text": "You are not authorized to access this command."}

        print('rendering control panel modal')
        modal = build_control_panel_modal()
        await client.views_open(trigger_id=trigger_id, view=modal)
        return {}

    if command == "/trigger-standup":
        print('now lets ping dms of each members')
        await send_standup_dm_to_team(team_id)
        return {"response_type": "ephemeral", "text": "📣 Standup triggered manually."}
    print('command not identified')
    return {"text": "Unknown command."}


@app.post("/slack/interactivity")
async def interactivity(req: Request):
    payload = await req.form()
    data = json.loads(payload["payload"])

    # Check if it’s a block_actions event and the correct action_id
    if data["type"] == "block_actions":
        action_id = data["actions"][0]["action_id"]
        trigger_id = data["trigger_id"]
        user_id = data["user"]["id"]
        team_id = data["team"]["id"]
        view_id = data["view"]["id"]
        print('view id', view_id)
        installation = get_installation(team_id)
        print('block action id ', action_id, ' userId ', user_id, ' teamId ', team_id)
        if not installation:
            return Response(status_code=200)

        client = AsyncWebClient(token=installation.access_token)

        if action_id == "start_standup":
            modal_view = standup_submission_modal()

            await client.views_open(trigger_id=trigger_id, view=modal_view)
            return {}

        elif action_id == "trigger_standup":
            print("**** manual trigger, send message to everyone")

        elif action_id == "configure_trigger_time":
            await client.views_update(view_id=view_id, view=trigger_time_modal())

        elif action_id == "configure_trigger_days":
            await client.views_update(view_id=view_id, view=trigger_days_modal())

        elif action_id == "set_response_channel":
            print('opening channel modal')
            await client.views_update(view_id=view_id, view=select_channel_modal())
            return {}

        elif action_id == "set_response_window":
            await client.views_update(view_id=view_id, view=response_window_modal())

    elif data["type"] == "view_submission":
        user_id = data["user"]["id"]
        team_id = data["team"]["id"]
        view = data["view"]
        callback_id = view["callback_id"]

        if callback_id == "standup_submission":
            values = data["view"]["state"]["values"]
            yesterday_answer = values["yesterday_block"]["yesterday_input"]["value"]
            today_answer = values["today_block"]["today_input"]["value"]
            blockers_answer = values["blockers_block"]["blockers_input"]["value"]

            # Save the responses in DB (pseudo-code)
            save_response(user_id, "What did you do yesterday?",
                          yesterday_answer)
            save_response(user_id, "What will you do today?", today_answer)
            save_response(user_id, "Any blockers?", blockers_answer)

            # Optionally, send a confirmation DM
            installation = get_installation(team_id)
            if installation:
                client = AsyncWebClient(token=installation.access_token)
                im_resp = await client.conversations_open(users=[user_id])
                channel_id = im_resp["channel"]["id"]
                await client.chat_postMessage(
                    channel=channel_id,
                    text="Thanks for submitting your standup! :tada:"
                )

            # empty body acknowledges submission
            return {}

        elif callback_id == "submit_trigger_time":
            time_val = view["state"]["values"]["trigger_time_block"]["time_select"]["selected_time"]
            update_installation(team_id, trigger_time=str(time_val))

        elif callback_id == "submit_trigger_days":
            selected = view["state"]["values"]["trigger_days_block"]["day_select"]["selected_options"]
            days = [opt["value"] for opt in selected]
            print('selected days now ', ",".join(days))
            update_installation(team_id, trigger_days=",".join(days))

        elif callback_id == "submit_channel_select":
            channel_id = view["state"]["values"]["channel_block"]["channel_select"]["selected_conversation"]
            print('channel id selected', channel_id)
            update_installation(team_id, submit_to_channel=channel_id)

        elif callback_id == "submit_response_window":
            minutes = view["state"]["values"]["response_window_block"]["window_input"]["value"]
            print('minutes to be now', minutes)
            update_installation(team_id, submit_after_mins= int(minutes))

    return {}


@app.get("/slack/install")
def install():
    state = str(uuid4())  # for MVP, this is fine
    url = AuthorizeUrlGenerator(
        client_id=CLIENT_ID,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    ).generate(state=state)
    return RedirectResponse(url)


@app.get("/slack/oauth_redirect")
async def oauth_redirect(req: Request):
    code = req.query_params.get("code")
    client = WebClient()
    resp = client.oauth_v2_access(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        code=code,
        redirect_uri=REDIRECT_URI
    )
    print('resp', resp)
    save_installation(
        team_id=resp["team"]["id"],
        team_name=resp["team"]["name"],
        bot_user_id=resp.get("bot_user_id", ""),
        access_token=resp["access_token"],
        installed_by=resp["authed_user"]["id"],
    )
    print('saved info to db')
    return {"message": "Installed to workspace ✅", "team": resp["team"]["id"]}


@app.post("/slack/events")
async def slack_events(req: Request):
    return await handler.handle(req)


@app.get("/")
def health():
    return {"status": "OK"}


if __name__ == "__main__":
    start_scheduler()
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
