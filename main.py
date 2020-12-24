from flask import Flask, request, make_response
import vk_api
import hashlib

from api_config import TOKEN, CONFIRMATION_CODE, SECRET
from accounts import Accounts
import bot

from qr import QR
qr = QR("qr_codes")


app = Flask(__name__)
vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()


@app.route('/')
@app.route('/index')
def index():
    user_id = request.cookies.get("user_id")
    if user_id:
        link = "/logout"
        text = "log out"
    else:
        link = "/login"
        text = "log in"
    html = f'Nothing to see here. Really. You only can <a href="{link}">{text}</a>'
    response = make_response(html)
    return response


@app.route('/login')
def login():
    code = request.args.get("code")
    vk_id = Accounts().check_code(code)
    if vk_id is not None:
        resp = make_response("Сработало. Можете вернуться к <a href='https://vk.com/lyceumtree2020'>боту</a>")
        resp.set_cookie("user_id", str(vk_id))
        token = hashlib.md5((str(vk_id)+"halolyouwillneverguessthissalt").encode("utf-8")).hexdigest()
        resp.set_cookie("token", token)
        bot.handle_authorization(vk_id, vk)
        return resp
    else:
        return "Кажется, вы ещё не общались с <a href='https://vk.com/lyceumtree2020'>ботом</a> " \
               "или код в ссылке неправильный"


@app.route('/logout')
def logout():
    user_id = request.cookies.get("user_id")
    if user_id:
        response = make_response("Вы успешно отвязали аккаунт")
        response.set_cookie("user_id", "", expires=0)
        response.set_cookie("token", "", expires=0)
        return response
    else:
        return "Устройство не было привязано"


@app.route('/callback_lol_whatever', methods=['POST'])
def callback():
    data = request.get_json(force=True, silent=True)
    if not data or 'type' not in data or data['secret'] != SECRET:
        return 'not ok'

    if data['type'] == 'confirmation':
        return CONFIRMATION_CODE
    elif data['type'] == 'message_new':
        bot.handle_new_message(data['object'], vk)
        return 'ok'

    return 'ok'


@app.route('/qr/<code>')
def check_qr(code):
    user_id = request.cookies.get("user_id")
    cookie_token = request.cookies.get("token")
    token = hashlib.md5((str(user_id)+"halolyouwillneverguessthissalt").encode("utf-8")).hexdigest()
    if not user_id or token != cookie_token:
        response = make_response("Сначала привяжите аккаунт через <a href='https://vk.com/lyceumtree2020'>бота</a>")
        return response
    elif qr.is_correct(code):
        bot.qr_found(user_id, code, vk, qr.get_question(code))
        return "ok"
    else:
        return "Такого кода нет в базе"
