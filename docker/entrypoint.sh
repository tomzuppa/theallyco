#!/bin/bash

# entrypoint.sh – Executed by Docker to start the app properly
# Ensures all pending migrations are applied before running the server

echo "🛠️ Applying database migrations..."
python manage.py migrate

echo "🚀 Starting Django development server on 0.0.0.0:8000..."
python manage.py runserver 0.0.0.0:8000
