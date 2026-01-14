# apps/core_activity/init_tasks.py
from datetime import datetime, timedelta
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from django.apps import apps
from django.db import connection
import json


def table_exists(table_name):
    """Verifica se a tabela existe no banco de dados."""
    return table_name in connection.introspection.table_names()


@receiver(post_migrate)
def criar_tasks_para_cores_existentes(sender, **kwargs):
    # Garante que a tabela exista antes de executar
    if not table_exists("core_activity_core"):
        print("Tabela core_activity_core ainda não existe. Pulando criação de tasks.")
        return

    Core = apps.get_model('core_activity', 'Core')

    core_objects = Core.objects.filter(status='Not Started')

    for core in core_objects:
        try:
            formatted_start_date = core.start_date.strftime("%Y-%m-%d %H:%M")
            formatted_end_date = core.end_date.strftime("%Y-%m-%d %H:%M")

            start_datetime = datetime.strptime(
                formatted_start_date, "%Y-%m-%d %H:%M"
            ) - timedelta(minutes=15)

            end_datetime = datetime.strptime(
                formatted_end_date, "%Y-%m-%d %H:%M"
            ) + timedelta(minutes=15)

            end_datetime_final_test = datetime.strptime(
                formatted_end_date, "%Y-%m-%d %H:%M"
            ) + timedelta(minutes=20)

            # Cria schedules de start e end
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

            # Cria periodic tasks de start, end e final_test
            PeriodicTask.objects.get_or_create(
                name=f"schedule-core_id-start-{core.id}",
                defaults={
                    "crontab": crontab_schedule_start_core,
                    "task": "apps.core_activity.tasks.test_services",
                    "args": json.dumps([core.id]),
                    "one_off": True
                }
            )

            PeriodicTask.objects.get_or_create(
                name=f"schedule-core_id-end-{core.id}",
                defaults={
                    "crontab": crontab_schedule_end_core,
                    "task": "apps.core_activity.tasks.test_services",
                    "args": json.dumps([core.id]),
                    "one_off": True
                }
            )

            PeriodicTask.objects.get_or_create(
                name=f"schedule-core_id-final_test-{core.id}",
                defaults={
                    "crontab": crontab_schedule_end_core_final_test,
                    "task": "apps.core_activity.tasks.valid_services",
                    "args": json.dumps([core.id]),
                    "one_off": True
                }
            )

            print(f"✅ Tasks criadas para Core {core.id}")

        except Exception as e:
            print(f"⚠️ Erro ao criar scheduler do core {core.id}: {e}")
