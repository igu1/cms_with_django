#!/bin/bash

# Script to check if the application is ready for production deployment

echo "=== Production Readiness Check ==="
echo "Checking if the application is ready for production deployment..."
echo

# Check if .env file exists
echo "Checking environment configuration..."
if [ -f .env ]; then
    echo "✅ .env file exists"
    
    # Check for DEBUG setting
    if grep -q "DEBUG=False" .env; then
        echo "✅ DEBUG is set to False"
    else
        echo "❌ WARNING: DEBUG is not set to False in .env file"
    fi
    
    # Check for SECRET_KEY
    if grep -q "SECRET_KEY=django-insecure" .env; then
        echo "❌ WARNING: Default insecure SECRET_KEY detected in .env file"
    else
        echo "✅ SECRET_KEY appears to be customized"
    fi
    
    # Check for ALLOWED_HOSTS
    if grep -q "ALLOWED_HOSTS=localhost,127.0.0.1" .env && ! grep -q "your-domain.com" .env; then
        echo "❌ WARNING: ALLOWED_HOSTS may not be configured for production"
    else
        echo "✅ ALLOWED_HOSTS appears to be configured"
    fi
    
    # Check for DATABASE_URL
    if grep -q "DATABASE_URL=" .env; then
        echo "✅ DATABASE_URL is configured"
    else
        echo "❌ WARNING: DATABASE_URL is not configured in .env file"
    fi
    
    # Check for email configuration
    if grep -q "EMAIL_HOST_USER=" .env && grep -q "EMAIL_HOST_PASSWORD=" .env; then
        if grep -q "EMAIL_HOST_USER=your_email@example.com" .env; then
            echo "❌ WARNING: Email settings appear to be default values"
        else
            echo "✅ Email settings appear to be configured"
        fi
    else
        echo "❌ WARNING: Email settings may not be configured"
    fi
    
    # Check for security settings
    if grep -q "CSRF_COOKIE_SECURE=True" .env && grep -q "SESSION_COOKIE_SECURE=True" .env; then
        echo "✅ Security cookie settings are enabled"
    else
        echo "❌ WARNING: Secure cookie settings may not be enabled"
    fi
else
    echo "❌ ERROR: .env file not found. Create one from .env.example or .env.production"
fi

echo

# Check for SSL certificates
echo "Checking SSL configuration..."
if [ -f nginx/ssl/cert.pem ] && [ -f nginx/ssl/key.pem ]; then
    echo "✅ SSL certificates exist"
    
    # Check if they are self-signed (for development only)
    if openssl x509 -in nginx/ssl/cert.pem -text -noout | grep -q "Self-Signed"; then
        echo "❌ WARNING: Self-signed SSL certificate detected. Use proper certificates for production."
    else
        echo "✅ SSL certificates appear to be properly configured"
    fi
else
    echo "❌ WARNING: SSL certificates not found in nginx/ssl/"
    echo "   Run ./scripts/generate_ssl_cert.sh for development or configure Let's Encrypt for production"
fi

echo

# Check for static files
echo "Checking static files..."
if [ -d staticfiles ]; then
    echo "✅ Static files directory exists"
    
    # Check if collectstatic has been run
    if [ "$(find staticfiles -type f | wc -l)" -gt 0 ]; then
        echo "✅ Static files appear to be collected"
    else
        echo "❌ WARNING: Static files directory is empty. Run 'python manage.py collectstatic'"
    fi
else
    echo "❌ WARNING: Static files directory not found. Run 'python manage.py collectstatic'"
fi

echo

# Check for database migrations
echo "Checking database migrations..."
if python manage.py showmigrations --list | grep -q "\[ \]"; then
    echo "❌ WARNING: There are unapplied migrations. Run 'python manage.py migrate'"
else
    echo "✅ All migrations appear to be applied"
fi

echo

# Check for Docker configuration
echo "Checking Docker configuration..."
if [ -f docker-compose.yml ]; then
    echo "✅ docker-compose.yml exists"
    
    # Check for production settings
    if grep -q "restart: always" docker-compose.yml; then
        echo "✅ Container restart policy is configured"
    else
        echo "❌ WARNING: Container restart policy may not be configured"
    fi
    
    # Check for volumes
    if grep -q "volumes:" docker-compose.yml; then
        echo "✅ Docker volumes are configured"
    else
        echo "❌ WARNING: Docker volumes may not be configured"
    fi
    
    # Check for nginx service
    if grep -q "nginx:" docker-compose.yml; then
        echo "✅ Nginx service is configured"
    else
        echo "❌ WARNING: Nginx service may not be configured"
    fi
else
    echo "❌ ERROR: docker-compose.yml not found"
fi

echo

# Check for backup script
echo "Checking backup configuration..."
if [ -f scripts/backup_db.sh ]; then
    echo "✅ Database backup script exists"
    
    # Check if it's executable
    if [ -x scripts/backup_db.sh ]; then
        echo "✅ Backup script is executable"
    else
        echo "❌ WARNING: Backup script is not executable. Run 'chmod +x scripts/backup_db.sh'"
    fi
    
    # Check for backup directory
    if [ -d backups ]; then
        echo "✅ Backup directory exists"
    else
        echo "❌ WARNING: Backup directory not found. Create it with 'mkdir -p backups'"
    fi
else
    echo "❌ WARNING: Database backup script not found"
fi

echo

# Check for security files
echo "Checking security files..."
if [ -f static/robots.txt ]; then
    echo "✅ robots.txt exists"
else
    echo "❌ WARNING: robots.txt not found"
fi

if [ -f static/sitemap.xml ]; then
    echo "✅ sitemap.xml exists"
else
    echo "❌ WARNING: sitemap.xml not found"
fi

if [ -f static/.well-known/security.txt ]; then
    echo "✅ security.txt exists"
else
    echo "❌ WARNING: security.txt not found"
fi

echo

# Final summary
echo "=== Production Readiness Summary ==="
echo "The application has been checked for production readiness."
echo "Review any warnings or errors above before deploying to production."
echo "For detailed deployment instructions, see docs/deployment.md"
echo
