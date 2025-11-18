#!/bin/bash

# Install dependencies
# pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Optional: Create superuser (only if not exists)
# echo "from django.contrib.auth import get_user_model; \
# User = get_user_model(); \
# User.objects.filter(username='admin').exists() or \
# User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')" \
# | python manage.py shell

# Collect static files
python manage.py collectstatic --noinput

# Prepare static output for Vercel
mkdir -p .vercel/output/static
