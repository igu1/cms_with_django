# Customer Management System

## Overview

A web-based software application designed to import, read, and manage preformatted XLSX and CSV files containing customer data. The application provides an elegant user interface, enabling managers to oversee sales assistants while restricting data access based on user roles. Sales staff can update customer status while managers can monitor overall activity, making customer management efficient and organized.

## Features

- **User Authentication**: Secure sign-up and login for managers and sales users with role-based access control
- **File Importing**: Simple and effective functionality for uploading preformatted XLSX and CSV files to the database
- **Dashboard Interface**: Intuitive dashboards for managers and sales staff displaying relevant metrics and statuses
- **Dynamic Data Access**: Role-based access allows users to view only the data assigned to them
- **Status Management**: Sales users can set customer status from predefined options (CALLED, NOT ANSWERED, INVALID NUMBER, PLAN PRESENTED, SHORTLISTED)

## Technical Stack

- **Frontend**: Django Templates with Tailwind CSS
- **Backend**: Django 4.2
- **Database**: SQLite (default), PostgreSQL (Docker)

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

### Manager
- Can import customer data via CSV/XLSX files
- Can view all customers in the system
- Can assign customers to sales users
- Can view performance metrics of sales users

### Sales
- Can view only assigned customers
- Can update customer status
- Can add notes to customer records

## File Import Format

The system accepts CSV and XLSX files with the following columns:
- `name` (required): Customer's full name
- `phone_number` (required): Customer's phone number
- `email` (optional): Customer's email address
- `address` (optional): Customer's address

## License

This project is licensed under the MIT License - see the LICENSE file for details.
