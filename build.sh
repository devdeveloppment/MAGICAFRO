#!/usr/bin/env bash
# exit on error - only for critical steps
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Load initial data only if the database is empty (no categories exist)
# The || true ensures the build never fails even if loaddata has an issue
python manage.py shell -c "
from products.models import Category
from django.core.management import call_command
if not Category.objects.exists():
    print('DB vide - chargement des donnees initiales...')
    call_command('loaddata', 'data_dump.json')
    print('Donnees chargees avec succes!')
else:
    print('Donnees deja presentes - pas besoin de loaddata.')
" || true

# Create superuser if it doesn't exist
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@magicafro.com').exists():
    User.objects.create_superuser('admin@magicafro.com', 'admin12345', first_name='Admin', last_name='MagicAfro')
    print('Superuser cree.')
else:
    print('Superuser deja existant.')
" || true
