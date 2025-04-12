# User Guide

This guide explains how to use the Customer Management System for alims.co.in, including user roles, dashboards, and key features.

## User Roles

The system has two main user roles:

### Sales Manager

Sales Managers have full access to the system and can:

- View all prospective students in the system
- Import customer data via CSV/XLSX files
- Assign prospective students to Student Counsellors
- View performance metrics of Student Counsellors
- Access import history
- Update any customer's status
- Generate reports

### Student Counsellor

Student Counsellors have limited access and can:

- View only their assigned prospective students
- Update status of their assigned students
- Add notes to student records
- View their own performance metrics

## Logging In

1. Navigate to the login page
2. Enter your username and password
3. Click "Sign In"
4. You will be redirected to your role-specific dashboard

## Dashboards

### Sales Manager Dashboard

The Sales Manager Dashboard provides an overview of:

- Total number of prospective students
- Number of assigned and unassigned students
- Distribution of students by status
- Student Counsellor performance metrics
- Recent imports
- Quick access to key functions

![Sales Manager Dashboard](../screenshots/manager_dashboard.png)

### Student Counsellor Dashboard

The Student Counsellor Dashboard shows:

- Total number of assigned prospective students
- Distribution of assigned students by status
- Recent activity (status changes)
- Quick access to assigned students

![Student Counsellor Dashboard](../screenshots/sales_dashboard.png)

## Managing Prospective Students

### Viewing Students

1. Click on "Prospective Students" in the navigation menu
2. Use filters to narrow down the list:
   - Filter by status using the dropdown
   - Search by name, phone number, or area
3. Click on a student's name to view details

### Student Details

The student detail page shows:

- Personal information (name, phone number, area)
- Current status
- Assignment information
- Status history
- Notes

From this page, you can:
- Update the student's status
- Add notes
- Assign to a different Student Counsellor (Sales Managers only)

### Updating Student Status

1. Navigate to the student detail page
2. Select the new status from the dropdown
3. Add notes explaining the status change (optional but recommended)
4. Click "Update Status"

The system will record the status change in the history section.

## Status Types

The system tracks the following enrollment stages:

| Status | Description |
|--------|-------------|
| INVALID | Contact information needs verification |
| VALID | Contact information verified |
| CALL_NOT_ATTENDED | Customer missed the call |
| PLAN_PRESENTED | Course details shared with customer |
| INTERESTED | Customer showed positive interest |
| NOT_INTERESTED | Customer declined to proceed |
| FOLLOW_UP | Scheduled for next contact |
| SHORTLISTED | Customer shortlisted our institution |
| CAMPUS_VISIT | Customer visited or scheduled a visit |
| REGISTRATION | Customer registered for a program |
| ADMISSION | Customer completed admission process |

## Importing Data

### Import Process (Sales Managers only)

1. Click on "Import Data" in the navigation menu
2. Click "Choose File" and select a CSV or XLSX file
3. Click "Upload File"
4. The system will process the file and display results
5. View import history to see details of past imports

For file format details, see the [Data Import Guide](data-import.md).

## Assigning Students

### Individual Assignment (Sales Managers only)

1. Navigate to the student detail page
2. Select a Student Counsellor from the dropdown
3. Click "Assign"

### Bulk Assignment (Sales Managers only)

1. Click on "Unassigned Students" in the navigation menu
2. Select students using the checkboxes
3. Choose a Student Counsellor from the dropdown
4. Click "Assign Selected"

Alternatively, you can use "Random Assignment" to distribute students evenly among Student Counsellors.

## Reports and Analytics

### Status Distribution

The dashboard shows the distribution of students by status, helping you track:
- How many students are at each stage of the enrollment process
- Conversion rates between stages
- Trends over time

### Student Counsellor Performance

Sales Managers can view performance metrics for each Student Counsellor:
- Number of assigned students
- Status distribution of their students
- Conversion rates
- Activity levels

## Account Management

### Updating Your Profile

1. Click on your username in the top-right corner
2. Select "Profile"
3. Update your information
4. Click "Save Changes"

### Changing Your Password

1. Click on your username in the top-right corner
2. Select "Change Password"
3. Enter your current password
4. Enter and confirm your new password
5. Click "Change Password"

## Logging Out

1. Click on your username in the top-right corner
2. Select "Logout"

## Next Steps

- [Learn about the data import format](data-import.md)
- [Troubleshoot common issues](troubleshooting.md)
