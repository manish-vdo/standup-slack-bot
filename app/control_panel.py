
def build_control_panel_modal():   
    return {
        "type": "modal",
        "callback_id": "control_panel_modal",
        "title": {"type": "plain_text", "text": "PulseBot Control Panel"},
        "close": {"type": "plain_text", "text": "Close"},
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*Welcome to your standup configuration panel!*"},
            },
            {
                "type": "actions",
                "block_id": "panel_actions",
                "elements": [
                    {
                        "type": "button",
                        "action_id": "trigger_standup",
                        "text": {"type": "plain_text", "text": "📢 Trigger Standup"},
                        "style": "primary"
                    },
                    {
                        "type": "button",
                        "action_id": "configure_trigger_time",
                        "text": {"type": "plain_text", "text": "⏰ Set Trigger Time"}
                    },
                    {
                        "type": "button",
                        "action_id": "configure_trigger_days",
                        "text": {"type": "plain_text", "text": "📅 Set Trigger Days"}
                    },
                    {
                        "type": "button",
                        "action_id": "set_response_channel",
                        "text": {"type": "plain_text", "text": "📺 Set Response Channel"}
                    },
                    {
                        "type": "button",
                        "action_id": "set_response_window",
                        "text": {"type": "plain_text", "text": "⏳ Response Window"}
                    },
                ]
            }
        ]
    }


def trigger_time_modal():
    return {
        "type": "modal",
        "callback_id": "submit_trigger_time",
        "title": {"type": "plain_text", "text": "Set Trigger Time"},
        "submit": {"type": "plain_text", "text": "Save"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": [
            {
                "type": "input",
                "block_id": "trigger_time_block",
                "label": {"type": "plain_text", "text": "Select Time"},
                "element": {"type": "timepicker", "action_id": "time_select"}
            }
        ]
    }


def trigger_days_modal(saved_days_arr):
    initial_options = [
          {"text": {"type": "plain_text", "text": day}, "value": day}
            for day in saved_days_arr
    ]

    options = [{"text": {"type": "plain_text", "text": day}, "value": day} for day in
               ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]]

    return {
        "type": "modal",
        "callback_id": "submit_trigger_days",
        "title": {"type": "plain_text", "text": "Set Trigger Days"},
        "submit": {"type": "plain_text", "text": "Save"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": [
            {
                "type": "input",
                "block_id": "trigger_days_block",
                "label": {"type": "plain_text", "text": "Select Days"},
                "element": {
                    "type": "multi_static_select",
                    "action_id": "day_select",
                    "placeholder": {"type": "plain_text", "text": "Choose days"},
                    "options": options,
                    "initial_options": initial_options,
                }
            }
        ]
    }


def select_channel_modal():
    return {
        "type": "modal",
        "callback_id": "submit_channel_select",
        "title": {"type": "plain_text", "text": "Select Channel"},
        "submit": {"type": "plain_text", "text": "Save"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": [
            {
                "type": "input",
                "block_id": "channel_block",
                "label": {"type": "plain_text", "text": "Select a channel"},
                "element": {
                    "type": "conversations_select",
                    "action_id": "channel_select",
                    "default_to_current_conversation": True
                }
            }
        ]
    }


def response_window_modal():
    return {
        "type": "modal",
        "callback_id": "submit_response_window",
        "title": {"type": "plain_text", "text": "Response Window"},
        "submit": {"type": "plain_text", "text": "Save"},
        "close": {"type": "plain_text", "text": "Cancel"},
        "blocks": [
            {
                "type": "input",
                "block_id": "response_window_block",
                "label": {"type": "plain_text", "text": "How much time do the users have to submit after a standup trigger (in minutes)"},
                "element": {
                    "type": "plain_text_input",
                    "action_id": "window_input"
                }
            }
        ]
    }
