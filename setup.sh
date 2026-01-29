#!/bin/bash
set -e

VENV_PATH="$HOME/pyenv/wagtail-show-test"
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== Wagtail Project Setup ==="

# Check for required system packages (for Pillow)
echo "Checking system dependencies..."
if ! dpkg -l | grep -q libjpeg-dev; then
    echo "Warning: libjpeg-dev may be needed for Pillow. Install with:"
    echo "  sudo apt-get install libjpeg-dev zlib1g-dev libpng-dev"
fi

# Create virtual environment
echo "Creating virtual environment at $VENV_PATH..."
python3 -m venv "$VENV_PATH"

# Activate and upgrade pip
echo "Upgrading pip..."
"$VENV_PATH/bin/pip" install --upgrade pip

# Install requirements
echo "Installing requirements..."
"$VENV_PATH/bin/pip" install -r "$PROJECT_DIR/requirements.txt"

# Create and run migrations
echo "Creating migrations..."
"$VENV_PATH/bin/python" "$PROJECT_DIR/manage.py" makemigrations home

echo "Running migrations..."
"$VENV_PATH/bin/python" "$PROJECT_DIR/manage.py" migrate

# Create superuser (non-interactive)
echo "Creating superuser (admin/admin)..."
DJANGO_SUPERUSER_PASSWORD=admin "$VENV_PATH/bin/python" "$PROJECT_DIR/manage.py" createsuperuser \
    --username admin \
    --email admin@example.com \
    --noinput 2>/dev/null || echo "Superuser already exists or creation skipped."

# Create sample page
echo "Creating sample page..."
"$VENV_PATH/bin/python" "$PROJECT_DIR/manage.py" create_sample_page

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To run the development server:"
echo "  $VENV_PATH/bin/python $PROJECT_DIR/manage.py runserver"
echo ""
echo "Admin: http://localhost:8000/admin/"
echo "Login: admin / admin"
echo ""
