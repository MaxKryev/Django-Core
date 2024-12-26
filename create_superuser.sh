#!/bin/sh

python manage.py makemigrations
python manage.py migrate

if ! python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists()"; then
    echo "Создание суперпользователя..."
    python manage.py createsuperuser --noinput --username "$DJANGO_SUPERUSER_USERNAME" --email "$DJANGO_SUPERUSER_EMAIL"
else
    echo "Суперпользователь уже существует"
fi

python manage.py shell -c "
from django.contrib.auth import get_user_model;
User  = get_user_model();
user = User.objects.get(username='$DJANGO_SUPERUSER_USERNAME');
user.set_password('$DJANGO_SUPERUSER_PASSWORD');
user.save();
"

python manage.py runserver 0.0.0.0:8001
