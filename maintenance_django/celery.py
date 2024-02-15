

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Configuração padrão do Django para o celery
from django.conf import settings

# Configuração do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'maintenance_django.settings')

# Crie uma instância do Celery
app = Celery('maintenance_django')

# Carregue as configurações do Django para o Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descubra e registre as tarefas do Django em todas as aplicações
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


# COMANDS FOR DEPLOY REDIST PS C:\Users\Lucas Fontini\Desktop\DJANGO_JANELA\maintenance_django> celery -A  maintenance_django  worker --pool=solo --loglevel=info
