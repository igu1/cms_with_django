# Architecture

This document provides an overview of the Customer Management System's architecture, components, and database schema.

## System Overview

The Customer Management System is a Django-based web application designed to manage customer data for alims.co.in. It provides role-based access control, customer status tracking, and file import functionality.

### Key Components

1. **Authentication System**: Handles user authentication and authorization with role-based access control.
2. **Customer Management**: Core functionality for managing customer data and status.
3. **File Import**: Handles importing customer data from CSV and XLSX files.
4. **Dashboard**: Provides analytics and overview for managers and student counsellors.

## Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Django Application                      │
│                                                             │
│  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐  │
│  │ Authentication│   │    Customer   │   │  File Import  │  │
│  │    System     │   │   Management  │   │     System    │  │
│  └───────────────┘   └───────────────┘   └───────────────┘  │
│                                                             │
│  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐  │
│  │   Dashboard   │   │  Status       │   │  User         │  │
│  │               │   │  Tracking     │   │  Management   │  │
│  └───────────────┘   └───────────────┘   └───────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                        Database                             │
│                                                             │
│  ┌───────────────┐   ┌───────────────┐   ┌───────────────┐  │
│  │     User      │   │    Customer   │   │  FileImport   │  │
│  └───────────────┘   └───────────────┘   └───────────────┘  │
│                                                             │
│  ┌───────────────┐                                          │
│  │CustomerStatus │                                          │
│  │   History     │                                          │
│  └───────────────┘                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

- **Backend**: Django 4.2
- **Frontend**: Django Templates with Tailwind CSS
- **Database**: PostgreSQL (production), SQLite (development)
- **Deployment**: Docker, Vercel
- **Static Files**: WhiteNoise
- **Authentication**: Django's built-in authentication system

## Database Schema

### User Model

The User model extends Django's AbstractUser and adds a role field:

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| username | CharField | Username for login |
| email | EmailField | User's email address |
| role | CharField | User role (MANAGER or SALES) |
| is_active | BooleanField | Whether the user account is active |
| date_joined | DateTimeField | When the user joined |

### Customer Model

The Customer model stores information about potential students:

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| name | CharField | Customer's name |
| phone_number | CharField | Customer's phone number |
| area | CharField | Customer's area/location |
| date | DateField | Relevant date |
| remark | TextField | Additional remarks |
| assigned_to | ForeignKey(User) | Student Counsellor assigned to this customer |
| status | CharField | Current status in the enrollment process |
| notes | TextField | Internal notes about the customer |
| created_at | DateTimeField | When the customer was created |
| updated_at | DateTimeField | When the customer was last updated |

### CustomerStatusHistory Model

Tracks changes to customer status:

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| customer | ForeignKey(Customer) | Reference to the customer |
| previous_status | CharField | Previous status |
| new_status | CharField | New status |
| changed_by | ForeignKey(User) | User who made the change |
| changed_at | DateTimeField | When the change was made |
| notes | TextField | Notes about the status change |

### FileImport Model

Tracks file imports:

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| file_name | CharField | Name of the imported file |
| file | FileField | The imported file |
| imported_by | ForeignKey(User) | User who imported the file |
| imported_at | DateTimeField | When the file was imported |
| total_records | IntegerField | Total number of records in the file |
| successful_records | IntegerField | Number of successfully imported records |
| failed_records | IntegerField | Number of failed records |

## Data Flow

1. **Authentication Flow**:
   - User submits login credentials
   - System authenticates and assigns appropriate permissions based on role
   - User is redirected to role-specific dashboard

2. **Customer Management Flow**:
   - Sales Managers can view all customers and assign them to Student Counsellors
   - Student Counsellors can only view and update their assigned customers
   - Status updates are tracked in the CustomerStatusHistory model

3. **File Import Flow**:
   - User uploads CSV/XLSX file
   - System validates the file format
   - System processes the file and creates/updates customer records
   - Import results are stored in the FileImport model

## Security Considerations

- Role-based access control ensures users only see appropriate data
- Password hashing using Django's built-in authentication
- CSRF protection for all forms
- Environment variables for sensitive configuration
- Secure cookie handling in production

## Next Steps

- [Learn how to use the system](user-guide.md)
- [Understand the development workflow](developer-guide.md)
- [Deploy the application](deployment.md)
