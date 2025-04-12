from django.core.management.base import BaseCommand
from django.utils import timezone
from customer.models import User, Customer, CustomerStatus, CustomerStatusHistory
import random
from faker import Faker
import uuid

class Command(BaseCommand):
    help = 'Creates sample data for testing the customer management application'
    
    def add_arguments(self, parser):
        parser.add_argument('--customers', type=int, default=50, help='Number of customers to create')
        parser.add_argument('--sales', type=int, default=3, help='Number of sales users to create')
    
    def handle(self, *args, **options):
        fake = Faker()
        num_customers = options['customers']
        num_sales = options['sales']
        
        self.stdout.write(self.style.SUCCESS('Creating sample data...'))
        
        # Create a manager user if it doesn't exist
        if not User.objects.filter(username='manager').exists():
            manager = User.objects.create_user(
                username='manager',
                email='manager@example.com',
                password='password',
                role=User.MANAGER,
                first_name='Manager',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS(f'Created manager user: {manager.username}'))
        else:
            manager = User.objects.get(username='manager')
            self.stdout.write(self.style.SUCCESS(f'Using existing manager user: {manager.username}'))
        
        # Create sales users
        sales_users = []
        for i in range(1, num_sales + 1):
            username = f'sales{i}'
            if not User.objects.filter(username=username).exists():
                sales_user = User.objects.create_user(
                    username=username,
                    email=f'sales{i}@example.com',
                    password='password',
                    role=User.SALES,
                    first_name=fake.first_name(),
                    last_name=fake.last_name()
                )
                self.stdout.write(self.style.SUCCESS(f'Created sales user: {sales_user.username}'))
            else:
                sales_user = User.objects.get(username=username)
                self.stdout.write(self.style.SUCCESS(f'Using existing sales user: {sales_user.username}'))
            
            sales_users.append(sales_user)
        
        # Create customers
        statuses = list(CustomerStatus.values)
        
        for i in range(num_customers):
            # Create customer
            customer = Customer.objects.create(
                name=fake.name(),
                phone_number=fake.phone_number(),
                email=fake.email() if random.random() > 0.2 else None,
                address=fake.address() if random.random() > 0.3 else None,
                assigned_to=random.choice(sales_users) if random.random() > 0.3 else None,
                notes=fake.text(max_nb_chars=200) if random.random() > 0.7 else None
            )
            
            # Randomly assign a status
            if random.random() > 0.2:
                status = random.choice(statuses)
                customer.status = status
                customer.save()
                
                # Create status history
                CustomerStatusHistory.objects.create(
                    customer=customer,
                    previous_status=None,
                    new_status=status,
                    changed_by=customer.assigned_to or manager,
                    changed_at=timezone.now() - timezone.timedelta(days=random.randint(1, 10)),
                    notes=fake.text(max_nb_chars=100) if random.random() > 0.5 else None
                )
                
                # Add additional status changes for some customers
                if random.random() > 0.7:
                    for _ in range(random.randint(1, 3)):
                        previous_status = customer.status
                        new_status = random.choice([s for s in statuses if s != previous_status])
                        
                        history = CustomerStatusHistory.objects.create(
                            customer=customer,
                            previous_status=previous_status,
                            new_status=new_status,
                            changed_by=customer.assigned_to or manager,
                            changed_at=timezone.now() - timezone.timedelta(days=random.randint(0, 5)),
                            notes=fake.text(max_nb_chars=100) if random.random() > 0.5 else None
                        )
                        
                        customer.status = new_status
                        customer.save()
            
            self.stdout.write(self.style.SUCCESS(f'Created customer: {customer.name}'))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {num_customers} customers and {num_sales} sales users'))
        self.stdout.write(self.style.SUCCESS('Login credentials:'))
        self.stdout.write(self.style.SUCCESS('Manager: username=manager, password=password'))
        for i in range(1, num_sales + 1):
            self.stdout.write(self.style.SUCCESS(f'Sales {i}: username=sales{i}, password=password'))
