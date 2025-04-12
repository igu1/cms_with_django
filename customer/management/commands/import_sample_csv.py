from django.core.management.base import BaseCommand
from django.utils import timezone
from customer.models import User, Customer, FileImport
import pandas as pd
import os
from django.conf import settings
import uuid

class Command(BaseCommand):
    help = 'Imports the sample CSV file with Indian customers'
    
    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default='sample_indian_customers.csv', help='Path to the CSV file')
        parser.add_argument('--username', type=str, default='manager', help='Username of the manager to import as')
    
    def handle(self, *args, **options):
        file_path = options['file']
        username = options['username']
        
        # Check if file exists
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File {file_path} does not exist'))
            return
        
        try:
            # Get the manager user
            try:
                manager = User.objects.get(username=username, role=User.MANAGER)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Manager user with username {username} does not exist'))
                return
            
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Validate required columns
            required_columns = ['name', 'phone_number']
            for col in required_columns:
                if col not in df.columns:
                    self.stdout.write(self.style.ERROR(f'Required column {col} is missing'))
                    return
            
            # Create file import record
            file_import = FileImport.objects.create(
                file_name=os.path.basename(file_path),
                file=file_path,
                imported_by=manager
            )
            
            # Process the data
            total_records = len(df)
            successful_records = 0
            failed_records = 0
            
            for _, row in df.iterrows():
                try:
                    # Check if customer with same phone number already exists
                    existing_customer = Customer.objects.filter(phone_number=row['phone_number']).first()
                    
                    if existing_customer:
                        # Update existing customer
                        existing_customer.name = row['name']
                        if 'email' in row and pd.notna(row['email']):
                            existing_customer.email = row['email']
                        if 'address' in row and pd.notna(row['address']):
                            existing_customer.address = row['address']
                        existing_customer.save()
                        self.stdout.write(self.style.WARNING(f'Updated existing customer: {row["name"]}'))
                    else:
                        # Create new customer
                        customer_data = {
                            'name': row['name'],
                            'phone_number': row['phone_number']
                        }
                        
                        if 'email' in row and pd.notna(row['email']):
                            customer_data['email'] = row['email']
                        if 'address' in row and pd.notna(row['address']):
                            customer_data['address'] = row['address']
                        
                        customer = Customer.objects.create(**customer_data)
                        self.stdout.write(self.style.SUCCESS(f'Created new customer: {row["name"]}'))
                    
                    successful_records += 1
                except Exception as e:
                    failed_records += 1
                    self.stdout.write(self.style.ERROR(f'Error processing record: {e}'))
            
            # Update file import record
            file_import.total_records = total_records
            file_import.successful_records = successful_records
            file_import.failed_records = failed_records
            file_import.save()
            
            self.stdout.write(self.style.SUCCESS(
                f'File imported successfully. {successful_records} records processed, {failed_records} failed.'
            ))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error processing file: {str(e)}'))
