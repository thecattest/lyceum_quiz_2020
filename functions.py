from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from accounts import Accounts
import states
import re


def get_main_keyboard(vk_id):
    code = Accounts().get_code(vk_id)
    log_in = f"https://lycquiz2020.pythonanywhere.com/login?code={code}"
    log_out = "https://lycquiz2020.pythonanywhere.com/logout"

    keyboard = VkKeyboard()
    keyboard.add_openlink_button("Привязать устройство", log_in, payload=[])
    keyboard.add_line()
    keyboard.add_openlink_button("Отвязать устройство", log_out, payload=[])
    keyboard.add_line()
    keyboard.add_button("Статистика", VkKeyboardColor.POSITIVE)
    # keyboard.add_line()
    keyboard.add_button("Помощь", VkKeyboardColor.PRIMARY)
    keyboard.add_button("Связь", VkKeyboardColor.NEGATIVE)

    return keyboard


def send_message(api, text, obj=None, to_id=None, keyboard=None):
    if to_id is None:
        to_id = obj["message"]["from_id"]
    if keyboard == -1:
        api.messages.send(
            message=text,
            random_id=get_random_id(),
            peer_id=to_id,
            keyboard=VkKeyboard.get_empty_keyboard()
        )
    elif keyboard == 2:
        keyboard = VkKeyboard()
        keyboard.add_button("Связь", VkKeyboardColor.NEGATIVE)
        api.messages.send(
            message=text,
            random_id=get_random_id(),
            peer_id=to_id,
            keyboard=keyboard.get_keyboard()
        )
    elif keyboard is not None:
        api.messages.send(
            message=text,
            random_id=get_random_id(),
            peer_id=to_id,
            keyboard=keyboard.get_keyboard()
        )
    else:
        api.messages.send(
            message=text,
            random_id=get_random_id(),
            peer_id=to_id
        )


def greet(obj, api, user):
    msg = "Привет!\n" \
          "Чтобы участвовать в викторине, сканируйте QR коды и отвечайте на вопросы.\n" \
          "Сначала привяжите устройство к аккаунту VK, нажав соответствующую кнопку внизу."
    vk_id = obj["message"]["from_id"]

    send_message(api, msg, obj, keyboard=get_main_keyboard(vk_id))
    return states.MAIN


def authorized(vk_id, api):
    msg = "Вы успешно привязали устройство. " \
          "Сканируйте коды и ждите моих вопросов ;)"
    send_message(api, msg, to_id=vk_id, keyboard=get_main_keyboard(vk_id))


def qr(vk_id, code, api, user, question):
    print(question)
    if "codes" in user.keys() and code in user["codes"]:
        send_message(api, "Вы уже сканировали такой код!", to_id=vk_id, keyboard=get_main_keyboard(vk_id))
    else:
        if "codes" not in user.keys():
            user["codes"] = []
        user["codes"] = user["codes"] + [code]
        send_message(api, code + " найден.", to_id=498417215)
        ask(api, user, question)
        return states.ASKED


def ask(api, user, question):
    user["current_type"] = question["type"]
    if question["type"] == 0:
        keyboard = VkKeyboard(one_time=True)
        for line in question["options"]:
            for lbl, correct in line:
                keyboard.add_button(lbl, VkKeyboardColor.PRIMARY)
                if correct:
                    user["current_correct"] = lbl
            if line != question["options"][-1]:
                keyboard.add_line()
        user["wrong_reply"], user["correct_reply"] = question["reply"]
        send_message(api, question["text"], to_id=user.vk_id, keyboard=keyboard)
    elif question["type"] == 1:
        user["current_correct"] = question["options"]
        user["wrong_reply"], user["correct_reply"] = question["reply"]
        send_message(api, question["text"], to_id=user.vk_id, keyboard=-1)


def check_answer(obj, api, user):
    answer = obj["message"]["text"]
    if user["current_type"] == 0:
        is_correct = answer == user["current_correct"]
    else:
        for option in user["current_correct"]:
            if re.fullmatch(option, answer):
                is_correct = True
                break
        else:
            is_correct = False
    if is_correct:
        user["correct_count"] = (1 if "correct_count" not in user.keys() else user["correct_count"] + 1)
        send_message(api, user["correct_reply"], obj, keyboard=get_main_keyboard(user.vk_id))
    else:
        if "correct_count" not in user.keys():
            user["correct_count"] = 0
        send_message(api, user["wrong_reply"], obj, keyboard=get_main_keyboard(user.vk_id))
    state = stats(obj, api, user)
    if state is not None:
        return state
    return states.MAIN


def stats(obj, api, user):
    try:
        count = len(user["codes"])
        points = user["correct_count"]
    except TypeError:
        count = 0
        points = 0
    msg = f"Найдено кодов: {count}\n" \
          f"Баллов: {points}"
    send_message(api, msg, obj, keyboard=get_main_keyboard(user.vk_id))

    if count >= 16 and "finished" not in user.keys():
        msg = "Итак, вопросы закончились, так что вы можете спокойно дожидаться результатов. \n" \
              "Спасибо за участие!"
        send_message(api, msg, obj, keyboard=2)
        user["finished"] = 1
        user["read"] = 1
        return states.FINISHED


def help(obj, api, user):
    if "read" not in user.keys():
        user["read"] = 1
    help_msg = "Чтобы участвовать: \n" \
               "1. Привяжите устройство, нажав на кнопку \"Привязать устройство\". \n" \
               "2. Отсканируйте QR код и перейдите по ссылке. " \
               "Чтобы всё работало, открывайте ссылки из QR кодов в том же браузере, " \
               "в котором открыли ссылку из кнопки авторизации \n" \
               "3. Правильно отвечайте на вопросы, набирайте баллы и получите подарок! \n\n" \
               "Имейте в виду: один QR - одна попытка. " \
               "Не сканируйте новый код до того как ответили на вопрос предыдущего, иначе вы потеряете балл\n\n" \
               'Если у вас есть вопросы, вы можете связаться с поддержкой нажав кнопку "Связь"'
    send_message(api, help_msg, obj, keyboard=get_main_keyboard(user.vk_id))


def support(obj, api, user):
    if "read" not in user.keys():
        send_message(api, "Сначала прочтите справку. Если у вас останутся вопросы - пишите", obj)
        help(obj, api, user)
        user["read"] = 1
        return

    vk_id = obj["message"]["from_id"]
    text = f"@id{vk_id} нужна помощь"
    send_message(api, text, to_id=498417215)

    msg = "Уведомление отправлено, ожидайте ответа"
    if "finished" in user.keys():
        keyboard = None
    else:
        keyboard = get_main_keyboard(vk_id)
    send_message(api, msg, obj, keyboard=keyboard)


def support_only(obj, api, user):
    send_message(api, 'Вопросов больше нет, ожидайте результатов. \n'
                      'Если вы хотите связаться с создателем, нажмите "Связь"', obj)


def fallback(obj, api, user):
    send_message(api, 'Это всё конечно хорошо, но такая команда не поддерживается...'
                      'Отправьте "Помощь" для справки', obj)
