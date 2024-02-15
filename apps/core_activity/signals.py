# core_activity/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime, timedelta
from django_celery_beat.models import CrontabSchedule, PeriodicTask
import json
from .models import Core


@receiver(post_save, sender=Core)
def criar_scheduler_para_novo_core(sender, instance, created, **kwargs):
    if created:
        formatted_start_date = instance.start_date.strftime("%Y-%m-%d %H:%M")
        formatted_end_date = instance.end_date.strftime("%Y-%m-%d %H:%M")

        start_datetime = datetime.strptime(
            formatted_start_date, "%Y-%m-%d %H:%M") - timedelta(minutes=15)

        end_datetime = datetime.strptime(
            formatted_end_date, "%Y-%m-%d %H:%M") + timedelta(minutes=15)

        end_datetime_final_test = datetime.strptime(
            formatted_end_date, "%Y-%m-%d %H:%M") + timedelta(minutes=20)

        crontab_schedule_start_core, _ = CrontabSchedule.objects.get_or_create(
            minute=start_datetime.minute,
            hour=start_datetime.hour,
            day_of_week=start_datetime.strftime("%a").lower(),
            day_of_month=start_datetime.day,
            month_of_year=start_datetime.month,
            timezone='America/Sao_Paulo'
        )

        crontab_schedule_end_core, _ = CrontabSchedule.objects.get_or_create(
            minute=end_datetime.minute,
            hour=end_datetime.hour,
            day_of_week=end_datetime.strftime("%a").lower(),
            day_of_month=end_datetime.day,
            month_of_year=end_datetime.month,
            timezone='America/Sao_Paulo'
        )

        crontab_schedule_end_core_final_test, _ = CrontabSchedule.objects.get_or_create(
            minute=end_datetime_final_test.minute,
            hour=end_datetime_final_test.hour,
            day_of_week=end_datetime_final_test.strftime("%a").lower(),
            day_of_month=end_datetime_final_test.day,
            month_of_year=end_datetime_final_test.month,
            timezone='America/Sao_Paulo'
        )
        # Criar tarefas agendadas para o novo core
        PeriodicTask.objects.create(
            crontab=crontab_schedule_start_core,
            name="schedule-core_id-start-{}".format(instance.id),
            task="apps.core_activity.tasks.test_services",
            args=json.dumps([instance.id]),
            one_off=True
        )

        PeriodicTask.objects.create(
            crontab=crontab_schedule_end_core,
            name="schedule-core_id-end-{}".format(instance.id),
            task="apps.core_activity.tasks.test_services",
            args=json.dumps([instance.id]),
            one_off=True
        )
        PeriodicTask.objects.create(
            crontab=crontab_schedule_end_core_final_test,
            name="schedule-core_id-final_test-{}".format(instance.id),
            task="apps.core_activity.tasks.valid_services",
            args=json.dumps([instance.id]),
            one_off=True
        )
        print("executou a criacao de nova core no sistema de agendamento")
