#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Load initial data only if the database is empty (no categories exist)
echo "from products.models import Category; from django.core.management import call_command; Category.objects.exists() or call_command('loaddata', 'data_dump.json')" | python manage.py shell

# Create superuser if it doesn't exist
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(email='admin@magicafro.com').exists() or User.objects.create_superuser('admin@magicafro.com', 'admin12345', first_name='Admin', last_name='MagicAfro')" | python manage.py shell || true
