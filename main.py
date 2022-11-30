import config
from database.public import Admin, Executor, Task
import logging
import texts
import images
from aiogram import Bot, Dispatcher, executor, types

bot = Bot(config.token)
dp = Dispatcher(bot)


def get_buttons(command, only_buttons=False):
    name_to_command = {'Главное меню': 'start',
                       'Задания': 'tasks_executor',
                       'Отзывы': 'test',
                       'Баланс': 'test',
                       'Тех-поддержка': 'support',
                       'Создать заказ': 'create_task',
                       'Информация для админов': 'info_for_admins',
                       'Заказы': 'task_for_admins'}
    buttons_for_command = {'start': ['Задания', 'Отзывы', 'Баланс', 'Тех-поддержка'],
                           'test': ['Главное меню'],
                           'support': ['Главное меню'],
                           'admin_menu': ['Создать заказ', 'Заказы', 'Главное меню', 'Информация для админов'],
                           'create_task': ['Главное меню'],
                           'info_for_admins': ['Главное меню'],
                           'task_for_admins': ['Главное меню'],
                           'tasks_executor': ['Главное меню']}
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    res = []
    for button_name in buttons_for_command[command.replace('/', '')]:
        res.append(types.InlineKeyboardButton(button_name, callback_data=name_to_command[button_name]))
    if only_buttons:
        return res
    keyboard.add(*res)
    return keyboard


@dp.message_handler(commands=['start'])
async def menu(message):
    await bot.delete_message(message.chat.id, message.message_id)
    keyboard = get_buttons(message.text)
    if message['from'].id not in [executor.telegram_id for executor in Executor.objects.all()]:
        new_executor = Executor.objects.create(telegram_id=message['from'].id, username=message['from'].username)
    if message['from'].id in [admin.telegram_id for admin in Admin.objects.all()]:
        keyboard.add(types.InlineKeyboardButton('Панель администрирования', callback_data='admin_menu'))
    await bot.send_photo(message.chat.id, images.image_executor_menu, texts.text_menu,
                         reply_markup=keyboard)


@dp.callback_query_handler(lambda call: True)
async def callback_inline(call):
    if call.message:
        if call.data == 'test':
            keyboard = get_buttons(call.data)
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            await bot.send_photo(call.message.chat.id, images.image_executor_menu, 'Тест',
                                 reply_markup=keyboard)
        if call.data == 'tasks_executor':
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            for task in Task.get_current_tasks():
                pass
            buttons = get_buttons(call.data, only_buttons=True)
            keyboard.add(buttons)
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            await bot.send_photo(call.message.chat.id, images.image_executor_menu, 'Тест',
                                 reply_markup=keyboard)
        if call.data == 'start':
            keyboard = get_buttons(call.data)
            keyboard.add(types.InlineKeyboardButton('Панель администрирования', callback_data='admin_menu'))
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            await bot.send_photo(call.message.chat.id, images.image_executor_menu, texts.text_menu,
                                 reply_markup=keyboard)
        if call.data == 'support':
            keyboard = get_buttons(call.data)
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            await bot.send_photo(call.message.chat.id, images.image_support_menu, texts.support_text,
                                 reply_markup=keyboard)
        if call.data == 'admin_menu':
            keyboard = get_buttons(call.data)
            keyboard.add(types.InlineKeyboardButton('Управление администрацией', callback_data='manage_admins'))
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            await bot.send_photo(call.message.chat.id, images.image_admin_menu, 'Админ панель',
                         reply_markup=keyboard)

        if call.data == 'create_task':
            keyboard = get_buttons(call.data)
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            await bot.send_photo(call.message.chat.id, images.image_admin_menu, 'Создание заказа',
                                 reply_markup=keyboard)
        if call.data == 'info_for_admins':
            keyboard = get_buttons(call.data)
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            await bot.send_photo(call.message.chat.id, images.image_admin_menu, 'Информация для администарции',
                                 reply_markup=keyboard)

        if call.data == 'task_for_admins':
            keyboard = get_buttons(call.data)
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            await bot.send_photo(call.message.chat.id, images.image_admin_menu, 'Все заказы администратора',
                                 reply_markup=keyboard)


@dp.message_handler(lambda message: True)
async def reply_message(message):
    if message.chat.type == 'private':
        await message.reply('Используйте кнопки или команды.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
