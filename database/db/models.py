import sys

try:
    from django.db import models
except Exception:
    print('Exception: Django Not Found, please install it with "pip install django".')
    sys.exit()

from django.utils import timezone

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
    #TODO: add timezone info

    telegram_id = models.BigIntegerField(primary_key=True)
    username = models.CharField(max_length=32)
    card_number = models.CharField(max_length=16)  # with no hyphens
    time_unbanned = models.DateTimeField(default=None)

    @property
    def is_banned(self):
        return timezone.now() >= self.time_unbanned

    def get_tasks(self):
        return self.tasks

    def get_today_tasks(self):
        raise NotImplemented()

    def get_available_tasks(self):
        raise NotImplemented()

    def get_current_tasks(self):
        raise NotImplemented()


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
    executor = models.ForeignKey(Executor, models.CASCADE, null=True)
    accepted_time = models.DateTimeField(null=True)
    execution_price = models.DecimalField(
        verbose_name="плата исполнителю",
        max_digits=5, decimal_places=2
    )

    # Admin fields (all marked with _)
    _order_price = models.DecimalField(
        verbose_name="цена заказа",
        max_digits=5, decimal_places=2
    )
    _admin = models.ForeignKey(Admin, models.CASCADE)
    _creation_time = models.DateTimeField(
        verbose_name="время создания задания",
        auto_now_add=True
    )
    _note = models.TextField(
        verbose_name="примечание"
    )
