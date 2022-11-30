from django.contrib import admin
from django.db.models import Count, Q, Sum
from django.urls import reverse
from django.utils.safestring import mark_safe

from . import models


@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['status','planned_time', 'executor']

@admin.register(models.Executor)
class ExecutorAdmin(admin.ModelAdmin):
    pass
@admin.register(models.Admin)
class AdminAdmin(admin.ModelAdmin):
    pass