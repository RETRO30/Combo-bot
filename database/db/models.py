import datetime

from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone

from config import REVIEWS_PER_A_DAY


class Admin(models.Model):
    ADMIN = "admin"
    SUPER_ADMIN = "super-admin"
    DISABLED = 'disabled'

    ROLES = [
        (ADMIN, 'администратор'),
        (SUPER_ADMIN, 'супер-администратор'),
        (DISABLED, 'заблокированный'),
    ]

    telegram_id = models.BigIntegerField(primary_key=True)
    username = models.CharField(max_length=32)
    role = models.CharField(max_length=20, choices=ROLES, default=ADMIN)


class Executor(models.Model):
    """Описывает модель исполнителя."""
    # TODO: add timezone info

    telegram_id = models.BigIntegerField(primary_key=True)
    username = models.CharField(max_length=32)
    card_number = models.CharField(max_length=16, validators=[
                                   RegexValidator(r"\d{16}")])  # with no hyphens
    time_unbanned = models.DateTimeField(null=True, blank=True, default=None)
    accounts_num = models.SmallIntegerField(
        verbose_name="количество аккаунтов в Авито", default=1)

    @property
    def is_banned(self):
        return timezone.now() >= self.time_unbanned

    def get_tasks(self) -> models.query.QuerySet:
        """Возвращает все задачи исполнителя за всё время."""

        return self.tasks.all()

    def get_tasks_num(self) -> int:
        """Возвращает количество всех задач исполнителя за всё время."""
        return self.get_tasks().count()

    def get_today_tasks(self) -> models.query.QuerySet:
        """Возвращает все задачи исполнителя за прошедшие 24 часа (запланированные или исполненные).
        """
        delta = datetime.timedelta(hours=24)

        now = timezone.now()

        return self.tasks.filter(
            Q(planned_time__range=(now - delta, now))
            | Q(executed_time__range=(now - delta, now))
        )

    def get_today_tasks_num(self) -> int:
        """Возвращает количество задач исполнителя за последние  24 часа"""
        return self.get_today_tasks().count()

    def get_available_tasks(self) -> list:
        """Возвращает список доступных работ для Исполнителя.

        Возвращает список доступных работ, учитывая, что Исполнитель
        с одним аккаунтом не может оставлять больше, чем
        config.REVIEWS_PER_A_DAY в день.
        """

        daily_limit = self.accounts_num*REVIEWS_PER_A_DAY
        result = []
        delta = datetime.timedelta(hours=24)

        for new_task in Task.objects.filter(status=Task.PENDING):
            new_time = new_task.planned_time

            tasks_before_num = self.tasks.filter(planned_time__range=(
                new_time-delta, new_time
            )).count()

            tasks_after_num = self.tasks.filter(planned_time__range=(
                new_time, new_time+delta
            )).count()

            if tasks_before_num >= daily_limit or tasks_after_num >= daily_limit:
                continue
            else:
                result.append(new_task)

        return result

    def get_current_tasks(self) -> models.query.QuerySet:
        """Возращает текущие задачи Исполнителя"""

        return self.tasks.filter(status__in=(
            Task.IN_WORK, Task.READY_NOT_CHECKED))

    def get_done_tasks(self) -> models.query.QuerySet:
        """Возращает завершённые задачи Исполнителя"""
        return self.tasks.filter(status__in=(Task.READY_CHECKED, Task.PAID))


class Task(models.Model):
    """Описывает модель задания для исполнителя."""

    PENDING = 0
    IN_WORK = 1
    READY_NOT_CHECKED = 2
    READY_CHECKED = 3
    PAID = 4
    FUCKED_UP = 5
    MISSED = 6

    STATUSES = [
        (PENDING, "ожидает исполнителя"),
        (IN_WORK, "в работе"),
        (READY_NOT_CHECKED, "готова, но НЕ проверена"),
        (READY_CHECKED, "проверена, но не оплачена"),
        (PAID, "оплачена"),
        (FUCKED_UP, "исполнитель просрал время"),
        (MISSED, "никто не взял задание в срок"),
    ]

    # Common fields
    status = models.SmallIntegerField(verbose_name="статус",
                                      choices=STATUSES, default=PENDING)
    post_link = models.CharField(
        verbose_name="ссылка на пост",
        max_length=2000,
    )
    planned_time = models.DateTimeField(
        verbose_name="время, когда должно быть исполнено",
    )
    description = models.TextField(
        verbose_name="описание",
        blank=True, default=''
    )
    feedback_content = models.TextField(
        verbose_name="содержимое отзыва",
        blank=True, default=''
    )

    # Executor related fields
    executor = models.ForeignKey(
        Executor, models.CASCADE, null=True, blank=True, related_name="tasks")
    accepted_time = models.DateTimeField(null=True, blank=True)
    execution_price = models.DecimalField(
        verbose_name="плата исполнителю",
        max_digits=5, decimal_places=2
    )
    executed_time = models.DateTimeField(
        verbose_name="время, когда было исполнено",
        null=True, blank=True
    )

    # Admin fields (all marked with _)
    _order_price = models.DecimalField(
        verbose_name="цена заказа",
        max_digits=5, decimal_places=2, default=0
    )
    _admin = models.ForeignKey(Admin, models.CASCADE)
    _creation_time = models.DateTimeField(
        verbose_name="время создания задания",
        auto_now_add=True
    )
    _note = models.TextField(
        verbose_name="примечание", blank=True
    )
