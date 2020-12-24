from conversation_config import storage, conversation, fallbacks, states, functions
from json_storage import User

import re


def handle_new_message(obj, api):
    from_id = obj['message']['from_id']
    message_text = obj["message"]["text"]
    user = User(from_id, storage)
    state = user["state"]

    message_handlers = conversation.get(state)
    for pattern, handler in message_handlers:
        if re.fullmatch(pattern, message_text):
            state = handler(obj, api, user)
            if state is not None:
                user["state"] = state
            break
    else:
        for pattern, fb in fallbacks:
            if re.fullmatch(pattern, message_text):
                state = fb(obj, api, user)
                if state is not None:
                    user["state"] = state
                break


def handle_authorization(vk_id, api):
    functions.authorized(vk_id, api)


def qr_found(vk_id, code, api, question):
    user = User(vk_id, storage)
    state = functions.qr(vk_id, code, api, user, question)
    if state is not None:
        user["state"] = state
