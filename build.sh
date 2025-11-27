# #!/bin/bash

# # Install dependencies
# pip install -r requirements.txt

# # Run migrations
# echo "Applying database migrations1432..."
# python manage.py makemigrations
# python manage.py migrate

# echo "Applying migrations for 'main' app..."
# python manage.py migrate main

# echo "Database migrations applied."


# # Optional: Create superuser (only if not exists)
# echo "from django.contrib.auth import get_user_model; \
# User = get_user_model(); \
# User.objects.filter(username='admin').exists() or \
# User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')" \
# | python manage.py shell

# # Collect static files
# python manage.py collectstatic --noinput

# # Prepare static output for Vercel
# mkdir -p .vercel/output/static





#!/bin/bash

# --- 1. Install Dependencies ---
pip install -r requirements.txt

# --- 2. Apply Database Migrations ---
# NOTE: This step requires the production database URL to be configured
# as an environment variable in Vercel and read by your Django settings.
echo "Applying database migrations..."
# Only run the general migrate command (which covers all apps)
# The --noinput flag prevents any interactive prompts.
python manage.py migrate --noinput
python manage.py migrate main 0011 --fake
echo "Database migrations applied."

# --- 3. Optional: Create superuser (only if not exists) ---
echo "Creating/verifying admin user..."
echo "from django.contrib.auth import get_user_model; \
User = get_user_model(); \
User.objects.filter(username='admin').exists() or \
User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')" \
| python manage.py shell

# --- 4. Collect static files ---
python manage.py collectstatic --noinput

# --- 5. Prepare static output for Vercel ---
# Note: The collectstatic command above should output to a directory 
# defined in settings.py (usually STATIC_ROOT). Vercel is looking for 
# a static output directory in the build output.
mkdir -p .vercel/output/static

# Assuming collectstatic output is configured correctly in Django settings,
# we need to copy it to Vercel's expected static location.
# If STATIC_ROOT is 'staticfiles' in your settings, use:
# cp -R staticfiles/* .vercel/output/static/

# --- END OF BUILD SCRIPT ---