import telebot
import config
import database

bot = telebot.TeleBot(config.token)

@bot.message_handler()
def reply_message(message):
    bot.reply_to(message, 'Используйте кнопки или команды.')

@bot.message_handler(commands=['start'])
def menu(message):
    bot.delete_message(message.chat.id, message.message_id)
    bot.send_photo(message.chat.id, 'for_test.png', config.text_menu)




bot.infinity_polling()