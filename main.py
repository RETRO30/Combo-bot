import config
import database
import logging
from aiogram import Bot, Dispatcher, executor, types

bot = Bot(config.token)
dp = Dispatcher(bot)


def get_buttons(command):
    name_to_command = {'Главное меню': 'start',
                       'Заказы': 'test',
                       'Отзывы': 'test',
                       'Баланс': 'test',
                       'Тех-поддержка': 'support'}
    buttons_for_command = {'start': ['Заказы', 'Отзывы', 'Баланс', 'Тех-поддержка'],
                           'test': ['Главное меню'],
                           'support': ['Главное меню']}
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    res = []
    for button_name in buttons_for_command[command.replace('/', '')]:
        res.append(types.InlineKeyboardButton(button_name, callback_data=name_to_command[button_name]))
    keyboard.add(*res)
    return keyboard


@dp.message_handler(commands=['start'])
async def menu(message):
    await bot.delete_message(message.chat.id, message.message_id)
    keyboard = get_buttons(message.text)
    await bot.send_photo(message.chat.id, types.InputFile('for_test.png'), config.text_menu,
                         reply_markup=keyboard)


@dp.callback_query_handler(lambda call: True)
async def callback_inline(call):
    if call.message:
        if call.data == 'test':
            keyboard = get_buttons(call.data)
            await bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                           caption="Тест",
                                           reply_markup=keyboard)
        if call.data == 'start':
            keyboard = get_buttons(call.data)
            await bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                           caption=config.text_menu, reply_markup=keyboard)
        if call.data == 'support':
            keyboard = get_buttons(call.data)
            await bot.edit_message_caption(chat_id=cal.message.chat.id, message_id=call.message.message_id,
                                           caption=config.support_text, reply_markup=keyboard)


@dp.message_handler(lambda message: True)
async def reply_message(message):
    if message.chat.type == 'private':
        await message.reply('Используйте кнопки или команды.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
