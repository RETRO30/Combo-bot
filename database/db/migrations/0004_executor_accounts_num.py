# Generated by Django 4.1.3 on 2022-11-27 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0003_task_executed_time_alter_executor_card_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='executor',
            name='accounts_num',
            field=models.SmallIntegerField(default=1, verbose_name='количество аккаунтов в Авито'),
        ),
    ]