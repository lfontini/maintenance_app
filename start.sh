#!/bin/bash


#inicialize postgres and redis 
service postgresql start 
service redis-server start 

#make migration and add admin user
python3 manage.py migrate 

#create user 
echo "from django.contrib.auth.models import User; \ 
User.objects.create_superuser('admin','admin@test.com', 'admin')" | python3 manage.py shell 

#start celery beat e worker 
celery -A maintenance_django  beat -l INFO &
celery -A  maintenance_django  worker  --loglevel=info &

#start django server 
python3 manage.py runserver 0.0.0.0:8000 

