#!/bin/bash
echo "🔄 Resetting Lost & Found app..."

# 1. Delete database
echo "🗑️  Deleting database..."
rm -f db.sqlite3

# 2. Delete all migration files
echo "🗑️  Deleting migration files..."
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# 3. Recreate __init__.py files
echo "📁 Creating fresh migration directories..."
for app in accounts marketplace lostfound housing food; do
    if [ -d "$app" ]; then
        mkdir -p "$app/migrations"
        touch "$app/migrations/__init__.py"
        echo "  ✅ $app/migrations/__init__.py"
    fi
done

# 4. Make fresh migrations
echo "📦 Creating migrations..."
python manage.py makemigrations

# 5. Apply migrations
echo "🔄 Applying migrations..."
python manage.py migrate

# 6. Create superuser
echo ""
echo "🎯 Creating superuser..."
python manage.py createsuperuser --username=admin --email=admin@campus.edu --noinput
echo "from django.contrib.auth import get_user_model; User = get_user_model(); user = User.objects.get(username='admin'); user.set_password('admin123'); user.save(); print('Superuser created: admin/admin123')" | python manage.py shell

echo ""
echo "✅ Reset complete!"
echo "🔗 Admin: http://localhost:8000/admin/"
echo "🔗 Lost & Found: http://localhost:8000/lostfound/"