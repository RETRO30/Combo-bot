import telebot
import config
import database

bot = telebot.TeleBot(config.token)


def get_buttons(command):
    name_to_command = {'Главное меню': 'start',
                       'Заказы': 'test',
                       'Отзывы': 'test',
                       'Баланс': 'test',
                       'Тех-поддержка': 'support'}
    buttons_for_command = {'start': ['Заказы', 'Отзывы', 'Баланс', 'Тех-поддержка'],
                           'test': ['Главное меню'],
                           'support': ['Главное меню']}
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    res = []
    for button_name in buttons_for_command[command.replace('/', '')]:
        res.append(telebot.types.InlineKeyboardButton(button_name, callback_data=name_to_command[button_name]))
    keyboard.add(*res)
    return keyboard


@bot.message_handler(commands=['start'])
def menu(message):
    bot.delete_message(message.chat.id, message.message_id)
    keyboard = get_buttons(message.text)
    bot.send_photo(message.chat.id, telebot.types.InputFile('for_test.png'), config.text_menu, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data == 'test':
            keyboard = get_buttons(call.data)
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption="Тест",
                                     reply_markup=keyboard)
        if call.data == 'start':
            keyboard = get_buttons(call.data)
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                     caption=config.text_menu, reply_markup=keyboard)
        if call.data == 'support':
            keyboard = get_buttons(call.data)
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                     caption=config.support_text, reply_markup=keyboard)


@bot.message_handler(func=lambda message: True)
def reply_message(message):
    if message.chat.type == 'private':
        bot.reply_to(message, 'Используйте кнопки или команды.')


bot.infinity_polling()
