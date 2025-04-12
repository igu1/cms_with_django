# Data Import Guide

This guide explains how to import customer data into the Customer Management System using CSV or XLSX files.

## Supported File Formats

The system supports importing customer data from:

- CSV (Comma-Separated Values) files
- XLSX (Microsoft Excel) files

## File Structure

### Required Columns

The following columns are required in your import file:

| Column | Description | Example |
|--------|-------------|---------|
| `name` | Customer's full name | John Smith |
| `phone_number` | Customer's phone number | 9876543210 |

### Optional Columns

The following columns are optional:

| Column | Description | Example |
|--------|-------------|---------|
| `area` | Customer's area/location | North Delhi |
| `date` | Relevant date (YYYY-MM-DD format) | 2025-04-15 |
| `remark` | Additional remarks | Interested in BCA program |

## Sample CSV File

Here's a sample CSV file format:

```csv
name,phone_number,area,date,remark
John Smith,9876543210,North Delhi,2025-04-15,Interested in BCA program
Priya Sharma,8765432109,South Delhi,2025-04-16,Looking for engineering courses
Rahul Kumar,7654321098,East Delhi,2025-04-17,Wants information about MBA
Ananya Patel,6543210987,West Delhi,2025-04-18,Interested in B.Tech Computer Science
Mohammed Khan,5432109876,Central Delhi,2025-04-19,Inquired about scholarship options
```

## Sample XLSX File

The XLSX file should have the same column structure as the CSV file. The first row should contain the column headers.

## Import Process

### Step 1: Access the Import Page

1. Log in as a Sales Manager
2. Click on "Import Data" in the navigation menu

### Step 2: Upload the File

1. Click "Choose File" and select your CSV or XLSX file
2. Click "Upload File"

### Step 3: Review Import Results

After the import is complete, you'll see a summary of the import results:

- Total records processed
- Successfully imported records
- Failed records

### Step 4: View Imported Data

1. Click on "Prospective Students" in the navigation menu
2. The newly imported customers will appear in the list

## Data Validation

The system performs the following validations during import:

1. **Required Fields**: Checks that `name` and `phone_number` are present
2. **Phone Number Format**: Validates phone number format
3. **Date Format**: Validates that dates are in YYYY-MM-DD format
4. **Duplicate Check**: Checks for existing customers with the same phone number

## Handling Duplicates

When a record with an existing phone number is found:

1. The system updates the existing customer record
2. All provided fields are updated with the new values
3. Fields not included in the import file remain unchanged

## Error Handling

Common import errors include:

1. **Missing Required Fields**: If `name` or `phone_number` is missing
2. **Invalid Date Format**: If the date is not in YYYY-MM-DD format
3. **File Format Issues**: If the file is not a valid CSV or XLSX
4. **Encoding Issues**: If the file uses an unsupported encoding

## Best Practices

1. **Use UTF-8 Encoding**: Save CSV files with UTF-8 encoding to ensure proper handling of special characters
2. **Validate Your Data**: Check your data for errors before importing
3. **Start Small**: Test with a small file before importing large datasets
4. **Back Up Data**: Back up your database before large imports
5. **Check Results**: Verify imported data after the import process

## Creating Import Files

### Using Microsoft Excel

1. Create a new Excel file
2. Add the column headers in the first row
3. Enter your data in the subsequent rows
4. Save as either XLSX or CSV format

### Using Google Sheets

1. Create a new Google Sheet
2. Add the column headers in the first row
3. Enter your data in the subsequent rows
4. Export as CSV (File > Download > Comma-separated values)

### Using a Text Editor

1. Open a text editor (like Notepad, VS Code, etc.)
2. Add the column headers separated by commas
3. Add each record on a new line, with values separated by commas
4. Save with a .csv extension

## Sample Files

### Download Sample Files

You can download sample import files to use as templates:

- [Sample CSV File](../sample_customers.csv)
- [Sample XLSX File](../sample_customers.xlsx)

### Sample CSV Content

```csv
name,phone_number,area,date,remark
John Smith,9876543210,North Delhi,2025-04-15,Interested in BCA program
Priya Sharma,8765432109,South Delhi,2025-04-16,Looking for engineering courses
Rahul Kumar,7654321098,East Delhi,2025-04-17,Wants information about MBA
Ananya Patel,6543210987,West Delhi,2025-04-18,Interested in B.Tech Computer Science
Mohammed Khan,5432109876,Central Delhi,2025-04-19,Inquired about scholarship options
Sanjay Gupta,4321098765,Noida,2025-04-20,Wants to visit campus next week
Neha Singh,3210987654,Gurgaon,2025-04-21,Referred by current student
Vikram Malhotra,2109876543,Faridabad,2025-04-22,Looking for hostel facilities
Deepika Reddy,1098765432,Ghaziabad,2025-04-23,Interested in part-time courses
Rajesh Verma,9087654321,Greater Noida,2025-04-24,Wants fee structure details
```

## Bulk Import Considerations

When importing large datasets:

1. **Performance**: Large imports may take longer to process
2. **Memory Usage**: Very large files may require more server resources
3. **Batch Processing**: Consider splitting very large files into smaller batches
4. **Error Handling**: Check the import results carefully for any failed records

## Import History

The system keeps a record of all imports, including:

1. File name
2. Import date and time
3. User who performed the import
4. Number of records processed
5. Number of successful and failed records

To view import history:

1. Log in as a Sales Manager
2. Click on "Import History" in the navigation menu

## Troubleshooting Import Issues

### File Not Uploading

1. Check file size (max 10MB)
2. Verify file format (CSV or XLSX)
3. Check file permissions

### Import Errors

1. Check for missing required columns
2. Verify data format (especially dates)
3. Check for special characters or encoding issues
4. Look for duplicate phone numbers

### No Records Imported

1. Check if the file has data beyond the header row
2. Verify column names match the expected format
3. Check for validation errors in the data

## Advanced Import Features

### Data Transformation

The import process performs some basic data transformations:

1. Trims whitespace from text fields
2. Converts dates to the system's internal format
3. Handles basic phone number formatting variations

### Status Assignment

Newly imported customers are not assigned a status by default. You can:

1. Set the status manually after import
2. Update the status using bulk actions
3. Include a status column in future versions of the import feature
