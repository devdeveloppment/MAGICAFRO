#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
# Seed data only on first deploy or manually
# python seed_db.py || true
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(email='admin@magicafro.com').exists() or User.objects.create_superuser('admin@magicafro.com', 'admin12345', first_name='Admin', last_name='MagicAfro')" | python manage.py shell || true
