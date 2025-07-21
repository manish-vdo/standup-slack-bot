# app/utils.py
from db import get_installation
from slack_sdk.web.async_client import AsyncWebClient


async def send_standup_dm_to_team(team_id):
    installation_info = get_installation(team_id)
    client = AsyncWebClient(installation_info.access_token)

    print('token found now lets fetch all users')
    # Get all users
    users_resp = await client.users_list()
    members = users_resp["members"]

    print('number of members identified is ', len(members))

    # DM each non-bot human user
    for user in members:
        if not user.get("is_bot") and not user.get("deleted"):
            uid = user["id"]
            im_resp = await client.conversations_open(users=[uid])
            channel_id = im_resp["channel"]["id"]

            await client.chat_postMessage(
                channel=channel_id,
                text="👋 Hey! Ready to fill your standup?",
                blocks=[
                     {
                         "type": "section",
                         "text": {
                             "type": "mrkdwn",
                             "text": "Hi! Ready to fill your standup?"
                         }
                     },
                    {
                         "type": "actions",
                         "elements": [
                             {
                                 "type": "button",
                                 "text": {
                                     "type": "plain_text",
                                     "text": "Start Standup"
                                 },
                                 "action_id": "start_standup"
                             }
                         ]
                     }
                ]
            )


async def render_control_panel(user_id, team_id):
    installation_info = get_installation(team_id)

