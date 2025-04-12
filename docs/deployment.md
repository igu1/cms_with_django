# Deployment Guide

This guide provides instructions for deploying the Customer Management System to various environments.

## Deployment Options

The application can be deployed in several ways:

1. **Docker Deployment**: Using Docker and Docker Compose
2. **Vercel Deployment**: Using Vercel for serverless deployment
3. **Traditional Deployment**: Using a traditional web server like Nginx or Apache

## Prerequisites

Before deploying, ensure you have:

- A PostgreSQL database
- Environment variables configured
- Static files collected
- Migrations applied

## Docker Deployment

### Prerequisites

- Docker and Docker Compose installed
- Git repository cloned

### Steps

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd customer-management
   ```

2. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

3. Update the environment variables in `.env`:
   ```
   DEBUG=False
   SECRET_KEY=your_secure_secret_key
   ALLOWED_HOSTS=your-domain.com,www.your-domain.com
   COMPANY_NAME=alims.co.in
   # The DATABASE_URL will be set by docker-compose.yml
   # Configure other database settings if needed
   DB_NAME=customer_management
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_HOST=db
   DB_PORT=5432
   ```

4. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

5. Run migrations:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

7. Collect static files:
   ```bash
   docker-compose exec web python manage.py collectstatic --noinput
   ```

8. Access the application at your domain or server IP.

### Docker Compose Configuration

The `docker-compose.yml` file includes:

- Web service running the Django application
- PostgreSQL database service
- Volume for persistent database storage

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

3. Run migrations:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

4. Collect static files:
   ```bash
   docker-compose exec web python manage.py collectstatic --noinput
   ```

## Vercel Deployment

### Prerequisites

- Vercel CLI installed
- Git repository cloned
- PostgreSQL database (can use services like Supabase, Neon, or AWS RDS)

### Steps

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Login to Vercel:
   ```bash
   vercel login
   ```

3. Configure environment variables in Vercel:
   - Go to your Vercel dashboard
   - Select your project
   - Go to Settings > Environment Variables
   - Add the following variables:
     - `SECRET_KEY`: Your Django secret key
     - `DEBUG`: Set to "False"
     - `ALLOWED_HOSTS`: Your Vercel domain
     - `DATABASE_URL`: Your PostgreSQL connection string
     - `COMPANY_NAME`: alims.co.in

4. Deploy the application:
   ```bash
   vercel
   ```

5. Run migrations (you'll need to set up a way to run migrations on your database):
   ```bash
   python manage.py migrate
   ```

### Vercel Configuration

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
