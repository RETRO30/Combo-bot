import config
from database.public import Admin, Executor, Task
import logging
import texts
import images
from telebot import TeleBot, types

bot = TeleBot(config.token)


def send_notification(user_id, message):
    bot.send_message(chat_id=user_id, text=message)


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
                           'task_': ['Задания'],
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


@bot.message_handler(commands=['start'])
def menu(message):
    bot.delete_message(message.chat.id, message.message_id)
    keyboard = get_buttons(message.text)
    if message.from_user.id not in [executor for executor in Executor.objects.values_list('telegram_id', flat=True)]:
        new_executor = Executor.objects.create(telegram_id=message.from_user.id, username=message.from_user.username)
    if message.from_user.id in [admin for admin in Admin.objects.values_list('telegram_id', flat=True)]:
        keyboard.add(types.InlineKeyboardButton('Панель администрирования', callback_data='admin_menu'))
    bot.send_photo(message.chat.id, types.InputFile(images.image_executor_menu), texts.text_menu,
                   reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data == 'test':
            keyboard = get_buttons(call.data)
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.send_photo(call.message.chat.id, types.InputFile(images.image_executor_menu), texts.text_menu,
                           reply_markup=keyboard)
        if call.data[:5] == 'task_':
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            task = Task.objects.get(id=int(call.data.replace('task_', '')))
            text_for_task = f'Название: {task.short_name}\nОписание:{task.description}\nСсылка:{task.post_link}'
            if task.status == 0:
                keyboard.add(types.InlineKeyboardButton('Принять задание', callback_data=f'accept_task_{task.id}'))

            buttons = get_buttons('task_', only_buttons=True)
            keyboard.add(*buttons)
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.send_photo(
                bot.send_photo(call.message.chat.id, types.InputFile(images.image_executor_menu), text_for_task,
                               reply_markup=keyboard))

        if call.data == 'tasks_executor':
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            current_executor = Executor.objects.get(telegram_id=call.message.chat.id)
            res = []
            for task in current_executor.get_current_tasks():
                res.append(types.InlineKeyboardButton(f'"{task.short_name} #{str(task.id)}" - В работе',
                                                      callback_data='task_' + str(task.id)))
            for task in current_executor.get_done_tasks():
                res.append(types.InlineKeyboardButton(f'"{task.short_name} #{str(task.id)}" - Завершено',
                                                      callback_data='task_' + str(task.id)))
            for task in current_executor.get_available_tasks():
                res.append(types.InlineKeyboardButton(f'"{task.short_name} #{str(task.id)}" - Доступно',
                                                      callback_data='task_' + str(task.id)))
            keyboard.add(*res)

            buttons = get_buttons(call.data, only_buttons=True)

            keyboard.add(*buttons)
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.send_photo(call.message.chat.id, types.InputFile(images.image_executor_menu), texts.text_menu,
                           reply_markup=keyboard)
        if call.data == 'start':
            keyboard = get_buttons(call.data)
            if call.message.from_user.id in [admin for admin in Admin.objects.values_list('telegram_id', flat=True)]:
                keyboard.add(types.InlineKeyboardButton('Панель администрирования', callback_data='admin_menu'))
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_photo(call.message.chat.id, types.InputFile(images.image_executor_menu), texts.text_menu,
                           reply_markup=keyboard)
        if call.data == 'support':
            keyboard = get_buttons(call.data)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_photo(call.message.chat.id, types.InputFile(images.image_support_menu), texts.support_text,
                           reply_markup=keyboard)
        if call.data == 'admin_menu':
            keyboard = get_buttons(call.data)
            keyboard.add(types.InlineKeyboardButton('Управление администрацией', callback_data='manage_admins'))
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_photo(call.message.chat.id, types.InputFile(images.image_admin_menu), 'Админ панель',
                           reply_markup=keyboard)

        if call.data == 'create_task':
            keyboard = get_buttons(call.data)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_photo(call.message.chat.id, types.InputFile(images.image_admin_menu), 'Создание заказа',
                           reply_markup=keyboard)
        if call.data == 'info_for_admins':
            keyboard = get_buttons(call.data)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_photo(call.message.chat.id, types.InputFile(images.image_admin_menu),
                           'Информация для администарции',
                           reply_markup=keyboard)

        if call.data == 'task_for_admins':
            keyboard = get_buttons(call.data)
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_photo(call.message.chat.id, types.InputFile(images.image_admin_menu), 'Все заказы администратора',
                           reply_markup=keyboard)


@bot.message_handler(func=lambda message: True)
async def reply_message(message):
    if message.chat.type == 'private':
        bot.reply_to(message, 'Используйте кнопки или команды.')


if __name__ == '__main__':
    bot.infinity_polling()
