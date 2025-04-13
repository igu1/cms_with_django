#!/bin/bash

# Script to deploy the application to production

echo "=== Production Deployment Script ==="
echo "This script will deploy the application to production."
echo

# Check if running as root
if [ "$(id -u)" -eq 0 ]; then
    echo "⚠️ Warning: Running as root. It's recommended to run as a non-root user."
    read -p "Continue anyway? (y/n): " continue_as_root
    if [ "$continue_as_root" != "y" ] && [ "$continue_as_root" != "Y" ]; then
        echo "Deployment aborted."
        exit 1
    fi
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Creating .env file from .env.production..."
    cp .env.production .env
    
    if [ ! -f .env ]; then
        echo "❌ Error: Failed to create .env file!"
        exit 1
    fi
    
    echo "✅ .env file created from .env.production"
fi

# Generate a secure secret key
echo "Generating a secure secret key..."
if [ -f scripts/generate_secret_key.py ]; then
    python3 scripts/generate_secret_key.py
else
    echo "❌ Error: generate_secret_key.py script not found!"
    echo "Generating a secret key manually..."
    SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    echo "Generated SECRET_KEY: $SECRET_KEY"
    echo "Please update your .env file manually."
fi

# Update ALLOWED_HOSTS
echo
echo "Updating ALLOWED_HOSTS..."
read -p "Enter your domain name (e.g., example.com): " domain_name
if [ -n "$domain_name" ]; then
    sed -i "s/ALLOWED_HOSTS=.*/ALLOWED_HOSTS=localhost,127.0.0.1,$domain_name,www.$domain_name/g" .env
    echo "✅ ALLOWED_HOSTS updated to include $domain_name"
else
    echo "❌ No domain provided. ALLOWED_HOSTS not updated."
fi

# Set up SSL certificates
echo
echo "Setting up SSL certificates..."
if [ ! -d "nginx/ssl" ]; then
    mkdir -p nginx/ssl
    echo "✅ Created nginx/ssl directory"
fi

read -p "Do you want to generate self-signed certificates for development? (y/n): " generate_ssl
if [ "$generate_ssl" == "y" ] || [ "$generate_ssl" == "Y" ]; then
    if [ -f scripts/generate_ssl_cert.sh ]; then
        ./scripts/generate_ssl_cert.sh
    else
        echo "❌ Error: generate_ssl_cert.sh script not found!"
        echo "Generating self-signed certificates manually..."
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout nginx/ssl/key.pem \
            -out nginx/ssl/cert.pem \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=$domain_name"
        echo "✅ Self-signed certificates generated"
    fi
else
    echo "Skipping self-signed certificate generation."
    echo "For production, you should use Let's Encrypt or another certificate provider."
    echo "Place your certificates in nginx/ssl/cert.pem and nginx/ssl/key.pem"
fi

# Create necessary directories
echo
echo "Creating necessary directories..."
mkdir -p logs
mkdir -p backups
mkdir -p media
echo "✅ Created logs, backups, and media directories"

# Build and start Docker containers
echo
echo "Building and starting Docker containers..."
if [ -f docker-compose.yml ]; then
    docker-compose down
    docker-compose up -d --build
    echo "✅ Docker containers built and started"
    
    # Run migrations
    echo
    echo "Running database migrations..."
    docker-compose exec web python manage.py migrate
    echo "✅ Database migrations applied"
    
    # Collect static files
    echo
    echo "Collecting static files..."
    docker-compose exec web python manage.py collectstatic --noinput
    echo "✅ Static files collected"
    
    # Create superuser if needed
    echo
    read -p "Do you want to create a superuser? (y/n): " create_superuser
    if [ "$create_superuser" == "y" ] || [ "$create_superuser" == "Y" ]; then
        docker-compose exec web python manage.py createsuperuser
    fi
else
    echo "❌ Error: docker-compose.yml not found!"
    echo "Please make sure you have Docker and Docker Compose installed and configured."
    exit 1
fi

# Set up backup cron job
echo
echo "Setting up database backup cron job..."
read -p "Do you want to set up automated daily backups? (y/n): " setup_backups
if [ "$setup_backups" == "y" ] || [ "$setup_backups" == "Y" ]; then
    if [ -f scripts/backup_db.sh ]; then
        chmod +x scripts/backup_db.sh
        
        # Add cron job
        (crontab -l 2>/dev/null; echo "0 2 * * * $(pwd)/scripts/backup_db.sh") | crontab -
        echo "✅ Backup cron job added to run daily at 2 AM"
    else
        echo "❌ Error: backup_db.sh script not found!"
    fi
fi

# Final checks
echo
echo "Running final production readiness checks..."
if [ -f scripts/check_production_readiness.sh ]; then
    ./scripts/check_production_readiness.sh
else
    echo "❌ Error: check_production_readiness.sh script not found!"
fi

echo
echo "=== Deployment Complete ==="
echo "Your application should now be running at:"
echo "  - http://$domain_name"
echo "  - https://$domain_name (if SSL is configured)"
echo
echo "If you encounter any issues, check the logs with:"
echo "  docker-compose logs -f web"
echo
echo "For more information, see docs/deployment.md"
