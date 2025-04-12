# Getting Started

This guide will help you set up and run the Customer Management System for alims.co.in.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8 or higher
- pip (Python package manager)
- Git
- Docker and Docker Compose (optional, for containerized setup)
- PostgreSQL (optional, for local database setup)

## Installation

### Local Development Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd customer-management
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Update the values as needed

6. Run migrations:
   ```bash
   python manage.py migrate
   ```

7. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

8. Run the development server:
   ```bash
   python manage.py runserver
   ```

9. Access the application at http://127.0.0.1:8000/

### Docker Setup

1. Build and start the containers:
   ```bash
   docker-compose up -d
   ```

2. Run migrations:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. Create a superuser:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

4. Access the application at http://localhost:8000/

## Configuration

### Environment Variables

The application uses environment variables for configuration. Here are the key variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `False` |
| `SECRET_KEY` | Django secret key | Generated |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | `localhost,127.0.0.1` |
| `COMPANY_NAME` | Company name displayed in the UI | `alims.co.in` |
| `DATABASE_URL` | Database connection string | SQLite |

For a complete list of environment variables, see the [Deployment Guide](deployment.md).

### Database Configuration

By default, the application uses SQLite for local development. To use PostgreSQL:

1. Uncomment the `DATABASE_URL` line in your `.env` file:
   ```
   DATABASE_URL=postgres://username:password@host:port/database_name
   ```

2. If using Docker, PostgreSQL is already configured in the docker-compose.yml file.

## Next Steps

- [Explore the architecture](architecture.md)
- [Learn about user roles and features](user-guide.md)
- [Set up for development](developer-guide.md)
