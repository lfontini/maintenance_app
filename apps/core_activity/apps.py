# from django.apps import AppConfig


# class CoreActivityConfig(AppConfig):
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'core_activity'
# your_app/apps.py

from django.apps import AppConfig


class CoreAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core_activity'

    def ready(self):
        '''

        This function will start a core schedulement when initiated, it will schedule a test for the core activity who
        '''
        from datetime import datetime, timedelta
        from django_celery_beat.models import CrontabSchedule, PeriodicTask
        from .models import Core
        import json
        from . import signals

        core_objects = Core.objects.filter(status='Not Started')

        for core in core_objects:
            try:
                formatted_start_date = core.start_date.strftime(
                    "%Y-%m-%d %H:%M")
                formatted_end_date = core.end_date.strftime("%Y-%m-%d %H:%M")

                start_datetime = datetime.strptime(
                    formatted_start_date, "%Y-%m-%d %H:%M") - timedelta(minutes=15)
                end_datetime = datetime.strptime(
                    formatted_end_date, "%Y-%m-%d %H:%M") + timedelta(minutes=15)
                end_datetime_final_test = datetime.strptime(
                    formatted_end_date, "%Y-%m-%d %H:%M") + timedelta(minutes=20)
                print(core.id, " ", formatted_start_date,
                      " ", formatted_end_date)

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
                PeriodicTask.objects.create(
                    crontab=crontab_schedule_start_core,
                    name="schedule-core_id-start-{}".format(core.id),
                    task="apps.core_activity.tasks.test_services",
                    args=json.dumps([core.id]),
                    one_off=True
                )
                PeriodicTask.objects.create(
                    crontab=crontab_schedule_end_core,
                    name="schedule-core_id-end-{}".format(core.id),
                    task="apps.core_activity.tasks.test_services",
                    args=json.dumps([core.id]),
                    one_off=True
                )

                PeriodicTask.objects.create(
                    crontab=crontab_schedule_end_core_final_test,
                    name="schedule-core_id-final_test-{}".format(core.id),
                    task="apps.core_activity.tasks.valid_services",
                    args=json.dumps([core.id]),
                    one_off=True
                )
            except Exception as erro:
                print("Erro ao inserir:", erro)
