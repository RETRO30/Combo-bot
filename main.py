import config
from database.public import Admin, Executor, Task
import texts
import images
from telebot import TeleBot, types
from django.utils import timezone

bot = TeleBot(config.token)


def move_menu(message, new_text, new_photo, keyboard):
    bot.delete_message(message.chat.id, message.id)
    bot.send_photo(message.chat.id, types.InputFile(new_photo), new_text,
                   reply_markup=keyboard)


def str_time(time):
    format = '%d.%m.%Y %H:%M'
    return timezone.localtime(time).strftime(format)


def get_buttons(command, only_buttons=False):
    name_to_command = {'Главное меню': 'start',
                       'Задания': 'tasks_executor',
                       'Вернуться ко всем заданиям': 'tasks_executor',
                       'Отзывы': 'https://t.me/+XIa54kP106AwZjgy',
                       'Оплата': 'payment',
                       'Тех-поддержка': 'support',
                       'Создать заказ': 'create_task',
                       'Информация для админов': 'info_for_admins',
                       'Заказы': 'task_for_admins'}
    buttons_for_command = {'start': ['Задания', 'Отзывы', 'Оплата', 'Тех-поддержка'],
                           'test': ['Главное меню'],
                           'payment': ['Главное меню'],
                           'task_': ['Вернуться ко всем заданиям'],
                           'support': ['Главное меню'],
                           'admin_menu': ['Создать заказ', 'Заказы', 'Главное меню', 'Информация для админов'],
                           'create_task': ['Главное меню'],
                           'info_for_admins': ['Главное меню'],
                           'task_for_admins': ['Главное меню'],
                           'tasks_executor': ['Главное меню']}
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    res = []
    for button_name in buttons_for_command[command.replace('/', '')]:
        if name_to_command[button_name].startswith('https://t.me/'):
            res.append(types.InlineKeyboardButton(button_name, url=name_to_command[button_name]))
        else:
            res.append(types.InlineKeyboardButton(button_name, callback_data=name_to_command[button_name]))
    if only_buttons:
        return res
    keyboard.add(*res)
    return keyboard


def add_payment_method_end(message):
    current_executor = Executor.objects.get(telegram_id=message.chat.id)
    current_executor.payment_method = message.text
    current_executor.save()
    bot.reply_to(message, 'Способ оплаты обновлён.')


@bot.message_handler(commands=['start'])
def menu(message):
    keyboard = get_buttons(message.text)
    if message.chat.id not in [executor for executor in Executor.objects.values_list('telegram_id', flat=True)]:
        Executor.objects.create(telegram_id=message.chat.id, username=message.chat.username)
    if message.chat.id in [admin for admin in Admin.objects.values_list('telegram_id', flat=True)]:
        keyboard.add(types.InlineKeyboardButton('Панель администрирования', callback_data='admin_menu'))
    move_menu(message, texts.text_menu, images.image_executor_menu, keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data == 'edit_payment_method':
            current_executor = Executor.objects.get(telegram_id=call.message.chat.id)
            bot.send_message(call.message.chat.id,
                             f'Текущий способ оплаты: {current_executor.payment_method}\nВведите новый способ оплаты:')
            bot.register_next_step_handler(call.message, add_payment_method_end)

        if call.data == 'edit_payment_method':
            bot.send_message(call.message.chat.id,
                             f'Введите новый способ оплаты:')
            bot.register_next_step_handler(call.message, add_payment_method_end)

        if call.data == 'payment':
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            buttons = get_buttons(call.data, only_buttons=True)
            current_executor = Executor.objects.get(telegram_id=call.message.chat.id)
            if current_executor.payment_method:
                keyboard.add(types.InlineKeyboardButton('Изменить способ оплаты', callback_data='edit_payment_method'))
            else:
                keyboard.add(types.InlineKeyboardButton('Добавить способ оплаты', callback_data='add_payment_method'))
            keyboard.add(*buttons)
            move_menu(call.message, texts.text_payment, images.image_executor_menu, keyboard)

        if call.data.startswith('accept_task_'):
            task = Task.objects.get(id=int(call.data.replace('accept_task_', '')))
            current_executor = Executor.objects.get(telegram_id=call.message.chat.id)
            keyboard = get_buttons('task_')
            if task.status == 0 and \
                    current_executor.get_today_tasks_num() < current_executor.accounts_num * config.REVIEWS_PER_A_DAY:
                task.status = 1
                task.executor = current_executor
                task.save()
                move_menu(call.message, texts.text_accept_task, images.image_executor_menu, keyboard)
            else:
                move_menu(call.message, texts.text_accept_task_error, images.image_executor_menu, keyboard)

        if call.data.startswith('task_'):
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            task = Task.objects.get(id=int(call.data.replace('task_', '')))
            text_for_task = f'{task.short_name}\n{task.description}' \
                            f'\n{task.post_link}\n{task.execution_price} рублей' \
                            f'\n{str_time(task.planned_time)}'
            if task.status == 0:
                keyboard.add(types.InlineKeyboardButton('Принять задание', callback_data=f'accept_task_{task.id}'))

            buttons = get_buttons('task_', only_buttons=True)
            keyboard.add(*buttons)
            move_menu(call.message, text_for_task, images.image_executor_menu, keyboard)

        if call.data == 'tasks_executor':
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            current_executor = Executor.objects.get(telegram_id=call.message.chat.id)
            res = []
            for task in current_executor.get_current_tasks():
                res.append(types.InlineKeyboardButton(f'{task.short_name} #{str(task.id)} - В работе',
                                                      callback_data='task_' + str(task.id)))
            for task in current_executor.get_done_tasks():
                res.append(types.InlineKeyboardButton(f'{task.short_name} #{str(task.id)} - Завершено',
                                                      callback_data='task_' + str(task.id)))
            for task in current_executor.get_available_tasks():
                res.append(types.InlineKeyboardButton(f'{task.short_name} #{str(task.id)} - Доступно',
                                                      callback_data='task_' + str(task.id)))
            keyboard.add(*res)

            buttons = get_buttons(call.data, only_buttons=True)

            keyboard.add(*buttons)
            move_menu(call.message, texts.text_menu, images.image_executor_menu, keyboard)

        if call.data == 'start':
            keyboard = get_buttons(call.data)
            if call.message.chat.id in [admin for admin in Admin.objects.values_list('telegram_id', flat=True)]:
                keyboard.add(types.InlineKeyboardButton('Панель администрирования', callback_data='admin_menu'))
            move_menu(call.message, texts.text_menu, images.image_executor_menu, keyboard)

        if call.data == 'support':
            keyboard = get_buttons(call.data)
            move_menu(call.message, texts.text_support, images.image_executor_menu, keyboard)

        if call.data == 'admin_menu':
            keyboard = get_buttons(call.data)
            if call.message.chat.id in [admin[0] for admin in Admin.objects.values_list('telegram_id', 'role') if
                                        admin[1] == 'super-admin']:
                keyboard.add(types.InlineKeyboardButton('Управление администрацией', callback_data='manage_admins'))
            move_menu(call.message, texts.text_menu, images.image_admin_menu, keyboard)

        if call.data == 'create_task':
            keyboard = get_buttons(call.data)
            move_menu(call.message, texts.text_menu, images.image_executor_menu, keyboard)

        if call.data == 'info_for_admins':
            keyboard = get_buttons(call.data)
            move_menu(call.message, texts.text_menu, images.image_executor_menu, keyboard)

        if call.data == 'task_for_admins':
            keyboard = get_buttons(call.data)
            move_menu(call.message, texts.text_menu, images.image_executor_menu, keyboard)


@bot.message_handler(func=lambda message: True)
async def reply_message(message):
    if message.chat.type == 'private':
        bot.reply_to(message, 'Используйте кнопки или команды.')


if __name__ == '__main__':
    bot.infinity_polling()
