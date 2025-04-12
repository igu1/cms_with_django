from django.core.management.base import BaseCommand
from django.db.models import Q
from customer.models import User, Customer
import random

class Command(BaseCommand):
    help = 'Assigns a random number of unassigned customers to a specified sales person'
    
    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the sales person')
        parser.add_argument('count', type=int, help='Number of customers to assign')
        parser.add_argument('--force', action='store_true', help='Assign customers even if they are already assigned')
    
    def handle(self, *args, **options):
        username = options['username']
        count = options['count']
        force = options.get('force', False)
        
        try:
            # Get the sales user
            sales_user = User.objects.get(username=username, role=User.SALES)
            
            # Get unassigned customers or all customers if force is True
            if force:
                available_customers = Customer.objects.exclude(assigned_to=sales_user)
            else:
                available_customers = Customer.objects.filter(assigned_to__isnull=True)
            
            # Check if we have enough customers
            available_count = available_customers.count()
            if available_count == 0:
                self.stdout.write(self.style.ERROR('No available customers to assign'))
                return
            
            # Adjust count if needed
            if count > available_count:
                self.stdout.write(self.style.WARNING(f'Only {available_count} customers available. Adjusting count.'))
                count = available_count
            
            # Randomly select customers
            selected_customers = random.sample(list(available_customers), count)
            
            # Assign customers
            for customer in selected_customers:
                customer.assigned_to = sales_user
                customer.save()
            
            self.stdout.write(self.style.SUCCESS(f'Successfully assigned {count} customers to {username}'))
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Sales user with username {username} does not exist'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
