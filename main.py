# -*- coding: utf-8 -*-
import os
import logging
import random

import requests
from flask import Flask, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

JOKES = [
    "— Рабинович, почему вы такой грустный?\n— Таки я оптимист.\n— И что?\n— Я уверен, что хуже ещё будет.",
    "— Сёма, ты где был два дня?\n— В запое.\n— И как там?\n— Как дома, только без жены.",
    "Молодой человек спрашивает у Розы Марковны:\n— Можно ли вам позвонить завтра вечером?\n— Можно. Только я не отвечу. Я буду занята.",
    "Сарочка кричит:\n— Моня! У нас в квартире вор!\n— Пусть берёт, что хочет. Лишь бы не нашёл заначку!",
    "— Сонечка, вы выйдете за меня?\n— Изя, вы же меня совсем не знаете!\n— Сонечка, я вас умоляю… А что там знать?",
    "Учительница:\n— Додик, почему ты не сделал домашнее задание?\n— Я пытался, но мама сказала, что так решать неправильно.",
    "— Рабинович, вы были у врача?\n— Был.\n— И что сказал врач?\n— Сказал: “Вы должны меньше нервничать”.\n— Так я и не нервничаю.\n— Он сказал, что он должен меньше нервничать.",
    "— Фима, почему ты пришёл в аптеку с чемоданом?\n— Я за каплями. Вдруг очередь!",
    "В одесском трамвае:\n— Передайте, пожалуйста, за проезд.\n— Мужчина, вы уже платили.\n— А шо, нельзя повторить?",
    "— Израиль Моисеевич, вы всё время жалуетесь на здоровье, но выглядите отлично!\n— Я вас умоляю, вы бы видели меня без таблеток.",
    "— Рая, ты слышала? Абрам купил себе новый “Мерседес”.\n— Ничего, пусть ребёнок порадуется.\n— Ему 76!\n— Тем более!",
    "Супруги спорят:\n— Фира, я хочу тишины!\n— Молчи.",
    "— Рабинович, вы почему опоздали на работу?\n— Так вы же сами сказали приходить вовремя.\n— И?\n— Я пришёл вовремя. Но не сегодня.",
    "— Моня, ты веришь в счастливую любовь?\n— Верю. Но предпочитаю деньги.",
    "— Папа, кто умнее — мужчина или женщина?\n— Конечно женщина, но мужчине об этом знать ни к чему.",
    "В Одессе:\n— Циля, где ты была три часа?\n— В парикмахерской.\n— А шо, работал один мастер?",
    "— Боря, почему ты никогда не споришь с женой?\n— А смысл? Она же потом всё равно всё объяснит.",
    "— Рабинович, вы любите свою жену?\n— А шо, есть выбор?",
    "— Яша, почему ты такой печальный?\n— Вчера меня никто не обидел.\n— Так это же хорошо!\n— Таки да, но какой смысл жить, если обо мне никто не вспоминает?",
    "В поезде:\n— Молодой человек, вы на моей полке лежите!\n— Я могу и на вашей сумке, если вы настаиваете."
]

RESPONSE_PREFIX = "Вот твоё анекдот-предсказание на сегодня..."

def get_random_joke():
    return random.choice(JOKES)

def should_reply_to_message(text: str) -> bool:
    if not text:
        return False
    lowered = text.lower()
    # Строго реагируем только на эти фразы, чтобы не флудить лишний раз.
    return ("предсказание" in lowered) or ("хочу предсказание" in lowered)

def send_telegram_message(chat_id: int, text: str) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("Environment variable TELEGRAM_BOT_TOKEN is not set")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }

    try:
        resp = requests.post(url, json=payload, timeout=5)
        if not resp.ok:
            logger.error("Failed to send message to Telegram: %s", resp.text)
    except Exception as e:
        logger.exception("Error while sending message to Telegram: %s", e)

@app.route("/", methods=["GET"])
def index():
    return "Telegram Jewish Joke Bot is running."

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json(force=True, silent=True)
    if not update:
        return "no update", 400

    logger.info("Incoming update: %s", update)

    # Обрабатываем только обычные сообщения (message).
    message = update.get("message")
    if not message:
        return "ok"

    # Не отвечаем на сообщения от ботов (включая самого себя).
    from_user = message.get("from", {})
    if from_user.get("is_bot"):
        return "ok"

    chat = message.get("chat", {})
    chat_id = chat.get("id")
    text = message.get("text", "")

    if chat_id is None:
        return "ok"

    if should_reply_to_message(text):
        joke = get_random_joke()
        reply_text = f"{RESPONSE_PREFIX}\n\n{joke}"
        send_telegram_message(chat_id, reply_text)

    return "ok"

if __name__ == "__main__":
    # Локальный запуск для отладки (например, на Mac)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
