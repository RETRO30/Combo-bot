import config
#from Database.db.models import Admin, Executor, Task
import logging
from aiogram import Bot, Dispatcher, executor, types

bot = Bot(config.token)
dp = Dispatcher(bot)


def get_buttons(command):
    name_to_command = {'Главное меню': 'start',
                       'Задания': 'test',
                       'Отзывы': 'test',
                       'Баланс': 'test',
                       'Тех-поддержка': 'support',
                       'Создать заказ': 'create_task',
                       'Информация для админов': 'info_for_admins',
                       'Заказы': 'task_for_admins'}
    buttons_for_command = {'start': ['Заказы', 'Отзывы', 'Баланс', 'Тех-поддержка'],
                           'test': ['Главное меню'],
                           'support': ['Главное меню'],
                           'admin_menu': ['Создать заказ', 'Заказы', 'Главное меню', 'Информация для админов'],
                           'create_task': ['Главное меню'],
                           'info_for_admins': ['Главное меню'],
                           'task_for_admins': ['Главное меню']}
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
    keyboard.add(types.InlineKeyboardButton('Админская панель', callback_data='admin_menu'))
    await bot.send_photo(message.chat.id, types.InputFile('for_test.png'), config.text_menu,
                         reply_markup=keyboard)


@dp.callback_query_handler(lambda call: True)
async def callback_inline(call):
    if call.message:
        if call.data == 'test':
            keyboard = get_buttons(call.data)
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            await bot.send_photo(call.chat.id, types.InputFile('for_test.png'), 'Тест',
                                 reply_markup=keyboard)
        if call.data == 'start':
            keyboard = get_buttons(call.data)
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            await bot.send_photo(call.chat.id, types.InputFile('for_test.png'), config.text_menu,
                                 reply_markup=keyboard)
        if call.data == 'support':
            keyboard = get_buttons(call.data)
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            await bot.send_photo(call.chat.id, types.InputFile('for_test.png'), config.support_text,
                                 reply_markup=keyboard)
        if call.data == 'admin_menu':
            keyboard = get_buttons(call.data)
            keyboard.add(types.InlineKeyboardButton('Управление администрацией', callback_data='manage_admins'))
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            await bot.send_photo(call.chat.id, types.InputFile('for_test.png'), 'Админ панель',
                         reply_markup=keyboard)

        if call.data == 'create_task':
            keyboard = get_buttons(call.data)
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            await bot.send_photo(call.chat.id, types.InputFile('for_test.png'), 'Создание заказа',
                                 reply_markup=keyboard)
        if call.data == 'info_for_admins':
            keyboard = get_buttons(call.data)
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            await bot.send_photo(call.chat.id, types.InputFile('for_test.png'), 'Информация для администарции',
                                 reply_markup=keyboard)

        if call.data == 'task_for_admins':
            keyboard = get_buttons(call.data)
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            await bot.send_photo(call.chat.id, types.InputFile('for_test.png'), 'Все заказы администратора',
                                 reply_markup=keyboard)




@dp.message_handler(lambda message: True)
async def reply_message(message):
    if message.chat.type == 'private':
        await message.reply('Используйте кнопки или команды.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
