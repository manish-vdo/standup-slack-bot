
def standup_submission_modal():
    return {
                "type": "modal",
                "callback_id": "standup_submission",
                "title": {
                    "type": "plain_text",
                    "text": "Daily Standup"
                },
                "submit": {
                    "type": "plain_text",
                    "text": "Submit"
                },
                "close": {
                    "type": "plain_text",
                    "text": "Cancel"
                },
                "blocks": [
                    {
                        "type": "input",
                        "block_id": "yesterday_block",
                        "element": {
                            "type": "plain_text_input",
                            "multiline": True,
                            "action_id": "yesterday_input"
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "What did you do yesterday?"
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "today_block",
                        "element": {
                            "type": "plain_text_input",
                            "multiline": True,
                            "action_id": "today_input"
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "What will you do today?"
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "blockers_block",
                        "element": {
                            "type": "plain_text_input",
                            "multiline": True,
                            "action_id": "blockers_input"
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Any blockers?"
                        }
                    }
                ]
            }