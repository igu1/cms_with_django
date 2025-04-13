# Deployment Guide

This guide provides instructions for deploying the Customer Management System to production environments.

## Deployment Options

The application can be deployed in several ways:

1. **Docker Deployment**: Using Docker, Docker Compose, and Nginx (recommended for production)
2. **Vercel Deployment**: Using Vercel for serverless deployment
3. **Traditional Deployment**: Using a traditional web server like Nginx with Gunicorn

## Prerequisites

Before deploying to production, ensure you have:

- A PostgreSQL database
- Environment variables properly configured for production
- SSL certificates for secure HTTPS connections
- A domain name pointing to your server
- Regular backup strategy in place

## Docker Deployment (Recommended for Production)

### Prerequisites

- Docker and Docker Compose installed on your server
- Git repository cloned
- Domain name with DNS configured
- SSL certificates (Let's Encrypt recommended)

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/igu1/alims.co.in.git
   cd alims.co.in
   ```

2. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

3. Generate a secure secret key:
   ```bash
   python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
   ```

4. Update the environment variables in `.env` for production:
   ```
   DEBUG=False
   SECRET_KEY=your_generated_secure_key
   ALLOWED_HOSTS=your-domain.com,www.your-domain.com
   COMPANY_NAME=alims.co.in
   DATABASE_URL=postgres://postgres:postgres@db:5432/customer_management

   # Email settings (important for production)
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=your-smtp-server.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@example.com
   EMAIL_HOST_PASSWORD=your-secure-password
   DEFAULT_FROM_EMAIL=your-email@example.com

   # Security settings
   CSRF_COOKIE_SECURE=True
   SESSION_COOKIE_SECURE=True
   ```

5. Set up SSL certificates for your domain:
   ```bash
   mkdir -p nginx/ssl

   # For production, use Let's Encrypt:
   # certbot certonly --webroot -w /path/to/webroot -d your-domain.com -d www.your-domain.com
   # cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
   # cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem

   # For development/testing, generate self-signed certificates:
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem
   ```

6. Create logs directory for application logs:
   ```bash
   mkdir -p logs
   ```

7. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

8. Run migrations:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

9. Create a superuser:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

10. Your application should now be running securely at https://your-domain.com

### Docker Compose Configuration

The updated `docker-compose.yml` file includes:

- Web service running the Django application with optimized Gunicorn settings
- PostgreSQL database service with health checks
- Nginx service for SSL termination and static file serving
- Volumes for persistent database, static files, and media storage
- Health checks for all services

### Updating the Deployment

To update the deployment:

1. Pull the latest changes:
   ```bash
   git pull
   ```

2. Rebuild and restart the containers:
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

3. Run migrations if needed:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

### Monitoring and Maintenance

1. Check application logs:
   ```bash
   docker-compose logs -f web
   ```

2. Check the health endpoint:
   ```bash
   curl https://your-domain.com/health/
   ```

3. Set up automated database backups:
   ```bash
   # Create a backup script
   mkdir -p scripts

   cat > scripts/backup.sh << 'EOF'
   #!/bin/bash
   BACKUP_DIR="/path/to/backups"
   DATETIME=$(date +%Y-%m-%d_%H-%M-%S)
   FILENAME="${BACKUP_DIR}/backup_${DATETIME}.sql"

   mkdir -p "${BACKUP_DIR}"
   docker-compose exec -T db pg_dump -U postgres customer_management > "${FILENAME}"
   gzip "${FILENAME}"

   # Delete backups older than 30 days
   find "${BACKUP_DIR}" -name "backup_*.sql.gz" -type f -mtime +30 -delete
   EOF

   chmod +x scripts/backup.sh

   # Add to crontab to run daily
   (crontab -l 2>/dev/null; echo "0 2 * * * /path/to/alims.co.in/scripts/backup.sh") | crontab -
   ```

## Vercel Deployment

### Prerequisites

- Vercel account and Vercel CLI installed
- Git repository cloned or forked
- PostgreSQL database (can use services like Supabase, Neon, or AWS RDS)
- Proper `vercel.json` configuration file (included in the repository)

### Steps

1. Fork the repository on GitHub or clone it locally:
   ```bash
   git clone https://github.com/igu1/alims.co.in.git
   cd alims.co.in
   ```

2. Install Vercel CLI if you haven't already:
   ```bash
   npm install -g vercel
   ```

3. Login to Vercel:
   ```bash
   vercel login
   ```

4. Generate a secure Django secret key:
   ```bash
   python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
   ```

5. Configure environment variables in Vercel:
   - Go to your Vercel dashboard
   - Select your project
   - Go to Settings > Environment Variables
   - Add the following variables:
     - `SECRET_KEY`: Your generated Django secret key
     - `DEBUG`: Set to "False"
     - `ALLOWED_HOSTS`: Your Vercel domain (e.g., `your-app.vercel.app,vercel.app`)
     - `DATABASE_URL`: Your PostgreSQL connection string
     - `COMPANY_NAME`: alims.co.in
     - `CSRF_COOKIE_SECURE`: "True"
     - `SESSION_COOKIE_SECURE`: "True"
     - Email configuration variables if needed

6. Deploy the application:
   ```bash
   vercel
   ```

7. After deployment, run migrations using the Vercel CLI:
   ```bash
   vercel env pull .env.local
   vercel run python manage.py migrate
   vercel run python manage.py createsuperuser
   ```

### Vercel Configuration

The `vercel.json` file is configured to:

- Use Python 3.9 runtime
- Set up proper routing for static files
- Run the build script to collect static files
- Configure environment variables

### Limitations of Vercel Deployment

1. **Serverless Architecture**: Vercel uses a serverless architecture, which means:
   - Cold starts may occur if the application is not frequently accessed
   - Long-running processes are not supported
   - File system operations are limited

2. **Database Considerations**:
   - You must use an external PostgreSQL database
   - Database connections may need to be optimized for serverless environments

3. **Static and Media Files**:
   - Static files are handled by Vercel's CDN
   - Media files should be stored in an external service like AWS S3

The `vercel.json` file includes:

- Build configuration
- Routes for static files and the Django application
- Environment variables

```json
{
  "version": 2,
  "builds": [
    {
      "src": "core/wsgi.py",
      "use": "@vercel/python",
      "config": { "maxLambdaSize": "15mb", "runtime": "python3.9" }
    },
    {
      "src": "build_files.sh",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "staticfiles"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/media/(.*)",
      "dest": "/media/$1"
    },
    {
      "src": "/(.*)",
      "dest": "core/wsgi.py"
    }
  ],
  "env": {
    "COMPANY_NAME": "alims.co.in",
    "ALLOWED_HOSTS": ".vercel.app,now.sh,127.0.0.1,localhost",
    "DEBUG": "False"
  }
}
```

### Updating the Vercel Deployment

To update the deployment:

1. Push changes to your repository
2. Redeploy using Vercel CLI:
   ```bash
   vercel --prod
   ```

## Traditional Deployment

### Prerequisites

- A server with Python installed
- Nginx or Apache web server
- PostgreSQL database
- Git repository cloned

### Steps

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd customer-management
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file:
   ```bash
   cp .env.example .env
   ```

5. Update environment variables in `.env`:
   ```
   DEBUG=False
   SECRET_KEY=your_secure_secret_key
   ALLOWED_HOSTS=your-domain.com,www.your-domain.com
   COMPANY_NAME=alims.co.in
   DATABASE_URL=postgres://username:password@localhost:5432/customer_management
   ```

6. Run migrations:
   ```bash
   python manage.py migrate
   ```

7. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

8. Collect static files:
   ```bash
   python manage.py collectstatic --noinput
   ```

9. Set up Gunicorn:
   ```bash
   pip install gunicorn
   ```

10. Create a systemd service file:
    ```
    [Unit]
    Description=gunicorn daemon
    After=network.target

    [Service]
    User=www-data
    Group=www-data
    WorkingDirectory=/path/to/customer-management
    ExecStart=/path/to/customer-management/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/path/to/customer-management/customer_management.sock core.wsgi:application

    [Install]
    WantedBy=multi-user.target
    ```

11. Set up Nginx:
    ```
    server {
        listen 80;
        server_name your-domain.com www.your-domain.com;

        location = /favicon.ico { access_log off; log_not_found off; }

        location /static/ {
            root /path/to/customer-management;
        }

        location /media/ {
            root /path/to/customer-management;
        }

        location / {
            include proxy_params;
            proxy_pass http://unix:/path/to/customer-management/customer_management.sock;
        }
    }
    ```

12. Start and enable the services:
    ```bash
    sudo systemctl start gunicorn
    sudo systemctl enable gunicorn
    sudo systemctl restart nginx
    ```

### Updating the Traditional Deployment

To update the deployment:

1. Pull the latest changes:
   ```bash
   git pull
   ```

2. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

3. Install any new dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Collect static files:
   ```bash
   python manage.py collectstatic --noinput
   ```

6. Restart Gunicorn:
   ```bash
   sudo systemctl restart gunicorn
   ```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `False` |
| `SECRET_KEY` | Django secret key | `your_secure_secret_key` |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | `your-domain.com,www.your-domain.com` |
| `COMPANY_NAME` | Company name displayed in the UI | `alims.co.in` |
| `DATABASE_URL` | Database connection string | `postgres://username:password@host:5432/database_name` |
| `STATIC_URL` | URL for static files | `/static/` |
| `STATIC_ROOT` | Directory for collected static files | `staticfiles/` |
| `MEDIA_URL` | URL for media files | `/media/` |
| `MEDIA_ROOT` | Directory for media files | `media/` |
| `EMAIL_BACKEND` | Email backend | `django.core.mail.backends.smtp.EmailBackend` |
| `EMAIL_HOST` | SMTP host | `smtp.example.com` |
| `EMAIL_PORT` | SMTP port | `587` |
| `EMAIL_USE_TLS` | Use TLS for email | `True` |
| `EMAIL_HOST_USER` | SMTP username | `your_email@example.com` |
| `EMAIL_HOST_PASSWORD` | SMTP password | `your_email_password` |
| `DEFAULT_FROM_EMAIL` | Default sender email | `your_email@example.com` |
| `CSRF_COOKIE_SECURE` | Use secure cookies for CSRF | `True` |
| `SESSION_COOKIE_SECURE` | Use secure cookies for sessions | `True` |

## Security Considerations

1. **HTTPS**: Always use HTTPS in production. Set up SSL certificates using Let's Encrypt.

2. **Secret Key**: Use a strong, unique secret key and keep it secret.

3. **Debug Mode**: Always set `DEBUG=False` in production.

4. **Database Security**: Use strong passwords and restrict database access.

5. **File Permissions**: Ensure proper file permissions for sensitive files.

6. **Regular Updates**: Keep Django and all dependencies updated.

7. **Backups**: Regularly backup your database and media files.

## Monitoring and Maintenance

1. **Logging**: Set up logging to monitor application errors.

2. **Backups**: Schedule regular database backups.

3. **Updates**: Regularly update Django and dependencies.

4. **Performance Monitoring**: Use tools like New Relic or Datadog to monitor performance.

5. **Security Scanning**: Regularly scan for security vulnerabilities.

## Troubleshooting

### Static Files Not Loading

1. Check `STATIC_URL` and `STATIC_ROOT` settings
2. Verify that `collectstatic` was run
3. Check web server configuration for static files

### Database Connection Issues

1. Verify database credentials
2. Check database server status
3. Ensure database user has proper permissions

### 500 Server Errors

1. Check application logs
2. Verify environment variables
3. Check for recent code changes
4. Ensure migrations are applied

### 404 Not Found Errors

1. Check URL configuration
2. Verify that the resource exists
3. Check for typos in URLs

## Backup and Restore

### Database Backup

```bash
pg_dump -U username -h hostname -d database_name > backup.sql
```

### Database Restore

```bash
psql -U username -h hostname -d database_name < backup.sql
```

### Media Files Backup

```bash
tar -czvf media_backup.tar.gz media/
```

### Media Files Restore

```bash
tar -xzvf media_backup.tar.gz
```
