#!/bin/bash

# Script to collect static files for production

echo "Collecting static files for production..."

# Check if running in Docker
if [ -f docker-compose.yml ]; then
    echo "Docker environment detected."
    
    # Check if Docker containers are running
    if docker-compose ps | grep -q "web"; then
        echo "Using Docker container to collect static files..."
        docker-compose exec web python manage.py collectstatic --noinput
    else
        echo "Starting Docker containers..."
        docker-compose up -d
        echo "Collecting static files..."
        docker-compose exec web python manage.py collectstatic --noinput
    fi
else
    # Check if virtual environment exists
    if [ -d "venv" ]; then
        echo "Using virtual environment to collect static files..."
        source venv/bin/activate
        python manage.py collectstatic --noinput
        deactivate
    else
        echo "No virtual environment found. Using system Python..."
        python manage.py collectstatic --noinput
    fi
fi

# Check if static files were collected
if [ -d "staticfiles" ]; then
    echo "✅ Static files collected successfully!"
    echo "Static files directory: $(pwd)/staticfiles"
    echo "Total files: $(find staticfiles -type f | wc -l)"
else
    echo "❌ Failed to collect static files!"
fi
