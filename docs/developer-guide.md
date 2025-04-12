# Developer Guide

This guide provides information for developers working on the Customer Management System for alims.co.in.

## Project Structure

```
customer-management/
├── core/                   # Django project settings
│   ├── settings.py         # Main settings file
│   ├── urls.py             # Main URL configuration
│   └── wsgi.py             # WSGI configuration for deployment
├── customer/               # Main application
│   ├── admin.py            # Admin interface configuration
│   ├── forms.py            # Form definitions
│   ├── migrations/         # Database migrations
│   ├── models.py           # Data models
│   ├── templatetags/       # Custom template tags
│   ├── tests.py            # Unit tests
│   ├── urls.py             # URL routing for the app
│   └── views.py            # View functions
├── templates/              # HTML templates
│   ├── base.html           # Base template with common elements
│   └── customer/           # App-specific templates
├── static/                 # Static files (CSS, JS, images)
│   ├── css/                # CSS files
│   ├── js/                 # JavaScript files
│   └── images/             # Image files
├── media/                  # User-uploaded files
├── staticfiles/            # Collected static files for production
├── docs/                   # Documentation
├── venv/                   # Virtual environment (not in version control)
├── .env                    # Environment variables (not in version control)
├── .env.example            # Example environment variables
├── .gitignore              # Git ignore file
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Docker configuration
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
├── vercel.json             # Vercel deployment configuration
└── README.md               # Project overview
```

## Key Components

### Models

The main models are defined in `customer/models.py`:

- `User`: Extended Django user model with role-based access
- `Customer`: Stores prospective student information
- `CustomerStatusHistory`: Tracks status changes
- `FileImport`: Records file import operations

### Views

Views are organized in `customer/views.py`:

- Authentication views (login, logout)
- Dashboard views (manager, sales)
- Customer management views (list, detail, update)
- File import views

### Templates

Templates are in the `templates/` directory:

- `base.html`: Base template with navigation and common elements
- `customer/`: App-specific templates
  - Dashboard templates
  - Customer list and detail templates
  - Import templates

### Static Files

Static files are in the `static/` directory:

- CSS files (Tailwind CSS)
- JavaScript files
- Images and icons

## Development Workflow

### Setting Up Development Environment

1. Clone the repository
2. Create a virtual environment
3. Install dependencies
4. Set up environment variables
5. Run migrations
6. Create a superuser
7. Run the development server

See the [Getting Started Guide](getting-started.md) for detailed instructions.

### Code Style and Conventions

- Follow PEP 8 for Python code
- Use Django's coding style for templates
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions small and focused
- Write tests for new functionality

### Git Workflow

1. Create a feature branch from `main`
2. Make your changes
3. Write or update tests
4. Run tests to ensure they pass
5. Commit your changes with descriptive commit messages
6. Push your branch and create a pull request
7. Address review comments
8. Merge to `main` when approved

### Adding New Features

1. **Plan the feature**:
   - Define the requirements
   - Design the database changes (if needed)
   - Plan the UI/UX

2. **Implement the feature**:
   - Add/modify models
   - Create migrations
   - Implement views
   - Create/update templates
   - Add static files

3. **Test the feature**:
   - Write unit tests
   - Perform manual testing
   - Check for edge cases

4. **Document the feature**:
   - Update relevant documentation
   - Add inline comments for complex logic

### Database Migrations

When changing models:

1. Make changes to the model in `models.py`
2. Create migrations:
   ```bash
   python manage.py makemigrations
   ```
3. Apply migrations:
   ```bash
   python manage.py migrate
   ```
4. Test the changes

### Adding New Dependencies

1. Install the package:
   ```bash
   pip install package-name
   ```
2. Add it to `requirements.txt`:
   ```bash
   pip freeze > requirements.txt
   ```
   or manually add the package with its version

## Testing

### Running Tests

Run all tests:
```bash
python manage.py test
```

Run specific tests:
```bash
python manage.py test customer.tests.TestCustomerModel
```

### Writing Tests

Tests are in `customer/tests.py`. Follow these guidelines:

- Test each model, view, and form
- Test both valid and invalid inputs
- Test edge cases
- Use Django's TestCase for most tests
- Use setUp and tearDown methods for common setup/cleanup

Example test:
```python
from django.test import TestCase
from customer.models import Customer, User

class CustomerModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass',
            role=User.SALES
        )
        
    def test_customer_creation(self):
        customer = Customer.objects.create(
            name='Test Customer',
            phone_number='1234567890',
            assigned_to=self.user
        )
        self.assertEqual(customer.name, 'Test Customer')
        self.assertEqual(customer.assigned_to, self.user)
```

## Common Development Tasks

### Adding a New Status Type

1. Update the `CustomerStatus` choices in `models.py`
2. Create and apply migrations
3. Update templates to display the new status
4. Update any relevant views or forms

### Adding a New User Role

1. Update the `User` model's role choices in `models.py`
2. Create and apply migrations
3. Update permission checks in views
4. Add role-specific templates or views

### Adding a New Field to Customer

1. Add the field to the `Customer` model in `models.py`
2. Create and apply migrations
3. Update forms to include the new field
4. Update templates to display the new field
5. Update the import process to handle the new field

## Troubleshooting Development Issues

### Migration Issues

If you encounter migration issues:

1. Check for dependencies between migrations
2. Try squashing migrations if they become too complex
3. In development, you can reset migrations by:
   - Deleting migration files (except `__init__.py`)
   - Dropping the database
   - Creating new initial migrations

### Static Files Issues

If static files aren't loading:

1. Check `STATIC_URL` and `STATICFILES_DIRS` in settings
2. Run `python manage.py collectstatic`
3. Check browser console for 404 errors
4. Verify file paths in templates

### Database Issues

For database connection issues:

1. Check database settings in `.env`
2. Verify the database server is running
3. Check for permission issues
4. Try connecting with a database client

## Deployment

See the [Deployment Guide](deployment.md) for detailed instructions on deploying the application.

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [Vercel Documentation](https://vercel.com/docs)
