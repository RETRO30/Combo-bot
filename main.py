import config
from database.public import Admin, Executor, Task
import texts
import images
from telebot import TeleBot, types
from django.utils import timezone
from datetime import datetime

bot = TeleBot(config.token)


def move_menu(message, new_text, new_photo, keyboard):
    bot.delete_message(message.chat.id, message.id)
    if new_text:
        if new_photo:
            bot.send_photo(message.chat.id, types.InputFile(new_photo), new_text,
                           reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, new_text,
                             reply_markup=keyboard)
    else:
        bot.send_photo(message.chat.id, types.InputFile(new_photo),
                       reply_markup=keyboard)


status_to_emoji = {0: '❕',
                   1: '⏳',
                   2: '❔',
                   3: '✅',
                   4: '💸',
                   5: '❌',
                   6: '❎',
                   7: '⛔️'}


def str_time(time):
    format = '%d.%m.%Y %H:%M (по МСК)'
    return timezone.localtime(time).strftime(format)


def time_str(time):
    format = '%d.%m.%Y %H:%M'
    return datetime.strptime(time, format)


beautiful_name = {'Главное меню': '⚙️Главное меню',
                  'Задания': '💰Задания',
                  'Отзывы': '☎️Отзывы',
                  'Гайды': '📜 Гайды',
                  'Оплата': '💳Оплата',
                  'Тех-поддержка': '👨🏿‍🔧Тех-поддержка'}


def get_buttons(command, only_buttons=False):
    name_to_command = {'Главное меню': 'start',
                       'Задания': 'tasks_executor',
                       'Вернуться ко всем заданиям': 'tasks_executor',
                       'Вернуться ко всем заказам': 'tasks_for_admins',
                       'Вернуться ко всем неоплаченным заказам': 'unpaid_tasks_for_admins',
                       'Отзывы': 'https://t.me/+XIa54kP106AwZjgy',
                       'Гайды': 'https://t.me/+FLhhvT5ZNHM4MDky',
                       'Жалобы на исполнителей': 'https://t.me/+ZTkl2mi_B8I5ZGQ6',
                       'Оплата': 'payment',
                       'Тех-поддержка': 'support',
                       'Создать заказ': 'create_task',
                       'Информация для админов': 'https://t.me/+TmIUUWpRgPE1N2Uy',
                       'Заказы': 'tasks_for_admins',
                       'Неоплаченные заказы': 'unpaid_tasks_for_admins',
                       'Назад к панели администрирования': 'admin_menu',
                       'Добавить администратора': 'add_admin'}
    buttons_for_command = {'start': ['Задания', 'Отзывы', 'Гайды', 'Оплата', 'Тех-поддержка'],
                           'test': ['Главное меню'],
                           'payment': ['Главное меню'],
                           'task_': ['Вернуться ко всем заданиям'],
                           'admin_task_': ['Вернуться ко всем заказам'],
                           'admin_unpaid_task_': ['Вернуться ко всем неоплаченным заказам'],
                           'support': ['Главное меню'],
                           'admin_menu': ['Создать заказ', 'Заказы', 'Неоплаченные заказы', 'Жалобы на исполнителей',
                                          'Информация для админов', 'Главное меню'],
                           'tasks_for_admins': ['Назад к панели администрирования'],
                           'unpaid_tasks_for_admins': ['Назад к панели администрирования'],
                           'tasks_executor': ['Главное меню'],
                           'manage_admins': ['Добавить администратора', 'Назад к панели администрирования']}
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    res = []
    for button_name in buttons_for_command[command.replace('/', '')]:
        if name_to_command[button_name].startswith('https://t.me/'):
            if button_name in beautiful_name.keys():
                res.append(types.InlineKeyboardButton(beautiful_name[button_name], url=name_to_command[button_name]))
            else:
                res.append(types.InlineKeyboardButton(button_name, url=name_to_command[button_name]))
        else:
            if button_name in beautiful_name.keys():
                res.append(
                    types.InlineKeyboardButton(beautiful_name[button_name], callback_data=name_to_command[button_name]))
            else:
                res.append(
                    types.InlineKeyboardButton(button_name, callback_data=name_to_command[button_name]))
    if only_buttons:
        return res
    keyboard.add(*res)
    return keyboard


def add_payment_method_end(message):
    current_executor = Executor.objects.get(telegram_id=message.chat.id)
    current_executor.payment_method = message.text
    current_executor.save()
    bot.reply_to(message, 'Способ оплаты обновлён.')


def get_to_ready_task(message, executor, task):
    if not message.photo:
        bot.reply_to(message, 'Вы должны прислать скриншот выполненной работы')
        bot.register_next_step_handler(message, lambda msg: get_to_ready_task(msg, executor, task))
    task.mark_ready()
    if task.status == Task.READY_NOT_CHECKED:
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        keyboard.add(types.InlineKeyboardButton('Принять', callback_data=f'admin_accept_{task.id}'))
        keyboard.add(types.InlineKeyboardButton('На доработку', callback_data=f'admin_to_finalize_{task.id}'))
        keyboard.add(types.InlineKeyboardButton('Отклонить', callback_data=f'admin_cancel_{task.id}'))
        bot.send_message(executor.telegram_id, 'Отчёт принят')
        bot.send_photo(chat_id=task._admin.telegram_id, photo=message.photo[-1].file_id,
                       caption=f'Исполнитель прислал отчёт о выполненной работе, заказ: {task.short_name} #{task.id}. Исполнитель: @{executor.username}',
                       reply_markup=keyboard)
    elif task.status == Task.FUCKED_UP:
        bot.send_message(executor.telegram_id, 'Вы выполнили задание не вовремя')
        bot.send_photo(chat_id=task._admin.telegram_id, photo=message.photo[-1].file_id,
                       caption=f'Исполнитель просрал заказ: {task.short_name} #{task.id}. Исполнитель: @{executor.username}')


def create_task(message, admin_id):
    data = [_.strip() for _ in message.text[1:].split('-')]
    try:
        new_task = Task.objects.create(short_name=data[0],
                                       post_link=data[1],
                                       planned_time=time_str(data[2]),
                                       description=data[3],
                                       feedback_content=data[4],
                                       execution_price=data[6],
                                       _admin=Admin.objects.get(telegram_id=admin_id),
                                       _order_price=float(data[5]))
        new_task._note = data[7]
    except Exception as e:
        bot.send_message(message.chat.id, 'Возникла какая-то ошибка.')
    else:
        bot.send_message(message.chat.id, 'Заказ создан.')
        new_task.save()


def add_admin(message):
    data = [_.strip() for _ in message.text[1:].split('-')]
    try:
        admin = Admin.objects.create(telegram_id=data[0], username=data[1])
    except Exception as e:
        bot.send_message(message.chat.id, 'Возникла какая-то ошибка.')
    else:
        bot.send_message(message.chat.id, 'Администратор создан.')
        admin.save()


def edit_task(message, task):
    data = [_.strip() for _ in message.text[1:].split('-')]
    try:
        task.short_name = data[0],
        task.post_link = data[1],
        task.planned_time = time_str(data[2]),
        task.description = data[3],
        task.feedback_content = data[4],
        task.execution_price = data[6],
        _order_price = float(data[5])
        task._note = data[7]
    except Exception as e:
        bot.send_message(message.chat.id, 'Возникла какая-то ошибка.')
    else:
        bot.send_message(message.chat.id, 'Заказ изменён.')
        task.save()


def get_id_executor(message):
    bot.send_message(message.chat.id, f'ID: {Executor.objects.get(username=message.text).telegram_id}')


def ban_executor(message):
    data = [_.strip() for _ in message.text[1:].split('-')]
    executor = Executor.objects.get(telegram_id=int(data[0]))
    executor.time_unbanned = time_str(data[1])
    bot.send_message(message.chat.id, 'Вы забанили исполнителя')


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
        if call.data == 'cancel':
            bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
            bot.delete_message(call.message.chat.id, call.message.id)

        if call.data == 'edit_payment_method':
            current_executor = Executor.objects.get(telegram_id=call.message.chat.id)
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton('Назад', callback_data='cancel'))
            bot.send_message(call.message.chat.id,
                             f'Текущий способ оплаты: {current_executor.payment_method}\nВведите новый способ оплаты:',
                             reply_markup=keyboard)
            bot.register_next_step_handler(call.message, add_payment_method_end)

        if call.data == 'add_payment_method':
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton('Назад', callback_data='cancel'))
            bot.send_message(call.message.chat.id,
                             f'Введите новый способ оплаты:', reply_markup=keyboard)
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
            move_menu(call.message, texts.text_payment, images.image_executor_payment, keyboard)

        if call.data.startswith('accept_task_'):
            task = Task.objects.get(id=int(call.data.replace('accept_task_', '')))
            current_executor = Executor.objects.get(telegram_id=call.message.chat.id)
            keyboard = get_buttons('task_')
            if task.status == Task.PENDING:
                task.mark_accepted(current_executor)
                move_menu(call.message, texts.text_accept_task, images.image_accept_task, keyboard)
            else:
                move_menu(call.message, texts.text_accept_task_error, images.image_error, keyboard)

        if call.data.startswith('to_ready_task_'):
            task = Task.objects.get(id=int(call.data.replace('to_ready_task_', '')))
            current_executor = Executor.objects.get(telegram_id=call.message.chat.id)
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton('Назад', callback_data='cancel'))
            bot.send_message(call.message.chat.id,
                             'Отправьте скриншот выполненой работы',
                             reply_markup=keyboard)
            bot.register_next_step_handler(call.message, lambda msg: get_to_ready_task(msg, current_executor, task))

        if call.data.startswith('task_'):
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            task = Task.objects.get(id=int(call.data.replace('task_', '')))
            text_for_task = f'❗{task.short_name}\n❗{task.description}' \
                            f'\n❗{task.post_link}\n❗{task.execution_price} рублей' \
                            f'\n❗{task.feedback_content}' \
                            f'\n❗{str_time(task.planned_time)}'
            if task.status == Task.PENDING:
                keyboard.add(types.InlineKeyboardButton('Принять задание', callback_data=f'accept_task_{task.id}'))
            if task.status == Task.IN_WORK:
                keyboard.add(types.InlineKeyboardButton('Готово', callback_data=f'to_ready_task_{task.id}'))

            buttons = get_buttons('task_', only_buttons=True)
            keyboard.add(*buttons)
            move_menu(call.message, text_for_task, images.image_executor_task, keyboard)

        if call.data == 'tasks_executor':
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            current_executor = Executor.objects.get(telegram_id=call.message.chat.id)
            res = []
            for task in current_executor.get_current_tasks():
                res.append(
                    types.InlineKeyboardButton(
                        f'{str_time(task.planned_time)} - {task.short_name} #{str(task.id)} {status_to_emoji[task.status]}',
                        callback_data='task_' + str(task.id)))
            for task in current_executor.get_done_tasks():
                res.append(
                    types.InlineKeyboardButton(f'{task.short_name} #{str(task.id)} {status_to_emoji[task.status]}',
                                               callback_data='task_' + str(task.id)))
            for task in current_executor.get_available_tasks():
                res.append(
                    types.InlineKeyboardButton(
                        f'{str_time(task.planned_time)} - {task.short_name} #{str(task.id)} {status_to_emoji[task.status]}',
                        callback_data='task_' + str(task.id)))
            keyboard.add(*res)

            buttons = get_buttons(call.data, only_buttons=True)

            keyboard.add(*buttons)
            move_menu(call.message, texts.text_tasks, images.image_executor_tasks, keyboard)

        if call.data == 'start':
            keyboard = get_buttons(call.data)
            if call.message.chat.id in [admin for admin in Admin.objects.values_list('telegram_id', flat=True)]:
                keyboard.add(types.InlineKeyboardButton('Панель администрирования', callback_data='admin_menu'))
            move_menu(call.message, texts.text_menu, images.image_executor_menu, keyboard)

        if call.data == 'support':
            keyboard = get_buttons(call.data)
            move_menu(call.message, texts.text_support, images.image_support_menu, keyboard)

        if call.data.startswith('admin_accept_'):
            task = Task.objects.get(id=int(call.data.replace('admin_accept_', '')))
            task.mark_checked()
            bot.send_message(chat_id=call.message.chat.id, text='Вы приняли отчёт исполнителя')

        if call.data.startswith('admin_to_finalize_'):
            task = Task.objects.get(id=int(call.data.replace('admin_to_finalize_', '')))
            task.mark_accepted(task.executor)
            bot.send_message(chat_id=call.message.chat.id, text='Вы отправили заказ на доработку')

        if call.data.startswith('admin_cancel_'):
            task = Task.objects.get(id=int(call.data.replace('admin_cancel_', '')))
            task.mark_fuckedup(task.executor)
            bot.send_message(chat_id=call.message.chat.id, text='Вы отклонили отчёт')

        if call.data == 'admin_menu':
            keyboard = get_buttons(call.data)
            if call.message.chat.id in [admin[0] for admin in Admin.objects.values_list('telegram_id', 'role') if
                                        admin[1] == 'super-admin']:
                keyboard.add(types.InlineKeyboardButton('Управление администрацией', callback_data='manage_admins'))
                keyboard.add(types.InlineKeyboardButton('Узнать id исполнителя', callback_data='get_id_executor'))
                keyboard.add(types.InlineKeyboardButton('Заблокировать исполнителя', callback_data='ban_executor'))
            move_menu(call.message, '', images.image_admin_menu, keyboard)

        if call.data.startswith('admin_task_'):
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            task = Task.objects.get(id=int(call.data.replace('admin_task_', '')))
            text_for_task = f'❗Название: {task.short_name}\n❗Описание: {task.description}' \
                            f'\n❗Ссылка: {task.post_link}\n❗Цена для исполнителя: {task.execution_price} рублей' \
                            f'\n❗Цена заказа: {task._order_price}  рублей' \
                            f'\n❗Отзыв: {task.feedback_content}' \
                            f'\n❗Время: {str_time(task.planned_time)}' \
                            f'\n❗Статус: {task.STATUSES[task.status][1]}'
            if task.status != Task.PENDING:
                text_for_task += f'\n❗Исполнитель: @{task.executor.username}' \
                                 f'\n❗Метод оплаты: {task.executor.payment_method}'
            keyboard.add(types.InlineKeyboardButton('Изменить', callback_data='edit_task_' + str(task.id)))
            keyboard.add(types.InlineKeyboardButton('Удалить', callback_data='delete_task_' + str(task.id)))
            buttons = get_buttons('admin_task_', only_buttons=True)
            keyboard.add(*buttons)
            move_menu(call.message, text_for_task, images.image_admin_menu, keyboard)

        if call.data.startswith('edit_task_'):
            task = Task.objects.get(id=int(call.data.replace('edit_task_', '')))
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton('Назад', callback_data='cancel'))
            bot.send_message(call.message.chat.id,
                             f'Изменить заказ.\nЗаполните следующие пункты\n{texts.text_create_task}',
                             reply_markup=keyboard)
            bot.register_next_step_handler(call.message, lambda msg: edit_task(msg, task))

        if call.data.startswith('delete_task_'):
            task = Task.objects.get(id=int(call.data.replace('delete_task_', '')))
            task.delete()
            bot.send_message(call.message.chat.id,
                             'Заказ удалён')

        if call.data.startswith('admin_unpaid_task_'):
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            task = Task.objects.get(id=int(call.data.replace('admin_unpaid_task_', '')))
            text_for_task = f'❗Название: {task.short_name}\n❗Описание: {task.description}' \
                            f'\n❗Ссылка: {task.post_link}\n❗Цена для исполнителя: {task.execution_price} рублей' \
                            f'\n❗Цена заказа: {task._order_price}' \
                            f'\n❗Отзыв: {task.feedback_content}' \
                            f'\n❗Время: {str_time(task.planned_time)}' \
                            f'\n❗Статус: {task.STATUSES[task.status][1]}'
            if task.status != Task.PENDING:
                text_for_task += f'\n❗Исполнитель: @{task.executor.username}' \
                                 f'\n❗Метод оплаты: {task.executor.payment_method}'

            keyboard.add(types.InlineKeyboardButton('Оплачено', callback_data='mark_paid_' + str(task.id)))
            buttons = get_buttons('admin_unpaid_task_', only_buttons=True)
            keyboard.add(*buttons)
            move_menu(call.message, text_for_task, images.image_executor_menu, keyboard)

        if call.data.startswith('mark_paid_'):
            task = Task.objects.get(id=int(call.data.replace('mark_paid_', '')))
            task.mark_paid()
            bot.send_message(chat_id=call.message.chat.id, text='Заказ помечен оплаченным')

        if call.data == 'create_task':
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton('Назад', callback_data='cancel'))
            bot.send_message(call.message.chat.id,
                             f'Создать заказ.\nЗаполните следующие пункты\n{texts.text_create_task}',
                             reply_markup=keyboard)
            bot.register_next_step_handler(call.message, lambda msg: create_task(msg, call.message.chat.id))

        if call.data == 'tasks_for_admins':
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            admin = Admin.objects.get(telegram_id=call.message.chat.id)
            for task in admin.get_tasks():
                keyboard.add(types.InlineKeyboardButton(
                    f'{str_time(task.planned_time)} - {task.short_name} #{str(task.id)} {status_to_emoji[task.status]}',
                    callback_data='admin_task_' + str(task.id)))
            buttons = get_buttons(call.data, only_buttons=True)
            keyboard.add(*buttons)
            move_menu(call.message, texts.text_tasks_for_admins, images.image_admin_menu, keyboard)

        if call.data == 'unpaid_tasks_for_admins':
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            admin = Admin.objects.get(telegram_id=call.message.chat.id)
            for task in admin.get_tasks_by_status(Task.READY_CHECKED):
                keyboard.add(types.InlineKeyboardButton(
                    f'{str_time(task.planned_time)} - {task.short_name} #{str(task.id)} {status_to_emoji[task.status]}',
                    callback_data='admin_unpaid_task_' + str(task.id)))
            buttons = get_buttons(call.data, only_buttons=True)
            keyboard.add(*buttons)
            move_menu(call.message, texts.text_unpaid_tasks_for_admins, images.image_admin_menu, keyboard)

        if call.data == 'manage_admins':
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            for admin in [admin for admin in Admin.objects.values_list('telegram_id', 'username')]:
                keyboard.add(types.InlineKeyboardButton(f'{admin[1]}', callback_data=f'info_admin_{admin[0]}'))
            buttons = get_buttons(call.data, only_buttons=True)
            keyboard.add(*buttons)
            move_menu(call.message, texts.text_manage_admins, images.image_admin_menu, keyboard)

        if call.data.startswith('info_admin_'):
            admin = Admin.objects.get(telegram_id=call.data.replace('info_admin_', ''))
            text_admin = f'{admin.telegram_id}\n@{admin.username}\n{admin.role}'
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(types.InlineKeyboardButton('Удалить', callback_data=f'delete_admin_{admin.telegram_id}'))
            keyboard.add(types.InlineKeyboardButton('Вернутся к списку администраторов', callback_data='manage_admins'))
            move_menu(call.message, text_admin, images.image_admin_menu, keyboard)

        if call.data.startswith('delete_admin_'):
            admin = Admin.objects.get(telegram_id=call.data.replace('delete_admin_', ''))
            admin.delete()
            bot.send_message(chat_id=call.message.chat.id, text='Администратор удалён.')

        if call.data == 'add_admin':
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton('Назад', callback_data='cancel'))
            bot.send_message(call.message.chat.id,
                             f'Добавить администратора.\nЗаполните следующие пункты\n{texts.text_add_admin}',
                             reply_markup=keyboard)
            bot.register_next_step_handler(call.message, lambda msg: add_admin(msg))

        if call.data == 'get_id_executor':
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton('Назад', callback_data='cancel'))
            bot.send_message(call.message.chat.id,
                             f'Получить id пользователя.\nВведите username:',
                             reply_markup=keyboard)
            bot.register_next_step_handler(call.message, lambda msg: get_id_executor(msg))

        if call.data == 'ban_executor':
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton('Назад', callback_data='cancel'))
            bot.send_message(call.message.chat.id,
                             f'Заблокировать пользователя.\nВведите\n-id\n-дд.мм.гггг чч:мм (время разбана)',
                             reply_markup=keyboard)
            bot.register_next_step_handler(call.message, lambda msg: ban_executor(msg))


@bot.message_handler(func=lambda message: True)
async def reply_message(message):
    if message.chat.type == 'private':
        bot.reply_to(message, 'Используйте кнопки или команды.')


if __name__ == '__main__':
    bot.infinity_polling()
