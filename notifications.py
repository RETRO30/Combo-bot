from telebot import TeleBot
import config


def send_notification(user_id, text):
    bot = TeleBot(config.token)
    bot.send_message(chat_id=user_id, text=text)
