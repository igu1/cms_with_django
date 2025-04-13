# Customer Management System (Django)

## Overview

A web-based software application designed to import, read, and manage preformatted XLSX and CSV files containing customer data. The application provides an elegant user interface, enabling managers to oversee sales assistants while restricting data access based on user roles. Sales staff can update customer status while managers can monitor overall activity, making customer management efficient and organized.

## Features

- **User Authentication**: Secure sign-up and login for managers and sales users with role-based access control
- **File Importing**: Simple and effective functionality for uploading preformatted XLSX and CSV files to the database
- **Dashboard Interface**: Intuitive dashboards for managers and sales staff displaying relevant metrics and statuses
- **Dynamic Data Access**: Role-based access allows users to view only the data assigned to them
- **Status Management**: Student Counsellors can set customer status from predefined options (INVALID, VALID, CALL_NOT_ATTENDED, PLAN_PRESENTED, INTERESTED, NOT_INTERESTED, FOLLOW_UP, SHORTLISTED, CAMPUS_VISIT, REGISTRATION, ADMISSION)

## Technical Stack

- **Frontend**: Django Templates with Tailwind CSS
- **Backend**: Django 4.2
- **Database**: SQLite (development), PostgreSQL (production)
- **Deployment**: Docker with Nginx (recommended), Vercel (serverless)
- **Security**: HTTPS, HSTS, secure cookies, content security policies

## Installation and Setup

### Prerequisites

- Python 3.8+
- pip

### Local Development Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd customer-management
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser (admin):
   ```bash
   python manage.py createsuperuser
   ```

6. (Optional) Create sample data for testing:
   ```bash
   python manage.py create_sample_data
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

8. Access the application at http://127.0.0.1:8000/

### Docker Setup

1. Build and run the containers:
   ```bash
   docker-compose up -d --build
   ```

2. Run migrations:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. Create a superuser:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

4. (Optional) Create sample data:
   ```bash
   docker-compose exec web python manage.py create_sample_data
   ```

5. Access the application at http://localhost:8000/

## User Roles

### Sales Manager
- Can import customer data via CSV/XLSX files
- Can view all customers in the system
- Can assign customers to Student Counsellors
- Can view performance metrics of Student Counsellors

### Student Counsellor
- Can view only assigned customers
- Can update customer status
- Can add notes to customer records

## File Import Format

The system accepts CSV and XLSX files with the following columns:
- `name` (required): Customer's full name
- `phone_number` (required): Customer's phone number
- `area` (optional): Customer's area/location
- `date` (optional): Date in YYYY-MM-DD format
- `remark` (optional): Additional remarks

## Management Commands

The system includes several useful management commands:

1. `import_sample_csv`: Imports sample customer data from CSV
   ```bash
   python manage.py import_sample_csv sample_indian_customers.csv
   ```

2. `create_sample_data`: Generates random sample customer data
   ```bash
   python manage.py create_sample_data 100  # Creates 100 sample customers
   ```

3. `assign_random_customers`: Randomly assigns customers to sales users
   ```bash
   python manage.py assign_random_customers
   ```

## Configuration

Key configuration options in `core/settings.py`:

- `LOGIN_REDIRECT_URL`: Where users are redirected after login
- `LOGOUT_REDIRECT_URL`: Where users are redirected after logout
- `MEDIA_ROOT`: Location for uploaded files
- `STATIC_ROOT`: Location for collected static files

## Production Deployment

For detailed production deployment instructions, see [docs/deployment.md](docs/deployment.md).

### Docker Production Deployment (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/igu1/alims.co.in.git
   cd alims.co.in
   ```

2. Create production environment file:
   ```bash
   cp .env.production .env
   ```

3. Generate a secure secret key:
   ```bash
   python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
   ```

4. Update the environment variables in `.env` with your production values.

5. Generate SSL certificates (or use Let's Encrypt):
   ```bash
   ./scripts/generate_ssl_cert.sh
   ```

6. Build and start the containers:
   ```bash
   docker-compose up -d --build
   ```

7. Run migrations and create a superuser:
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

8. Set up automated database backups:
   ```bash
   ./scripts/backup_db.sh
   ```

### Vercel Deployment (Serverless)

1. Fork the repository on GitHub.

2. Connect your GitHub repository to Vercel.

3. Configure environment variables in the Vercel dashboard:
   - `SECRET_KEY`: Your Django secret key
   - `DEBUG`: Set to "False"
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `ALLOWED_HOSTS`: Your Vercel domain
   - `COMPANY_NAME`: alims.co.in
   - `CSRF_COOKIE_SECURE`: "True"
   - `SESSION_COOKIE_SECURE`: "True"

4. Deploy the application from the Vercel dashboard.

## API Documentation

The system provides REST API endpoints (via Django views):

- `/api/customers/`: List all customers (manager only)
- `/api/customers/<id>/`: Get customer details
- `/api/customers/import/`: Import customer data (POST)
- `/api/customers/status/`: Update customer status (POST)

## Testing

To run tests:
```bash
python manage.py test customer
```

Key test cases:
- User authentication and authorization
- Customer import functionality
- Status update workflow
- Role-based access control

## Screenshots

![Login Page](screenshots/login.png)
![Manager Dashboard](screenshots/manager_dashboard.png)
![Sales Dashboard](screenshots/sales_dashboard.png)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request
