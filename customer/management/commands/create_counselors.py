from django.core.management.base import BaseCommand
from customer.models import User

class Command(BaseCommand):
    help = 'Creates the specified student counselors in the database'
    
    def handle(self, *args, **options):
        counselors = [
            'Hiba',
            'Hadiya',
            'Aneesha',
            'Devika',
            'Risily',
            'Safa',
            'Suhaila',
            'Jamshada'
        ]
        
        created_count = 0
        existing_count = 0
        
        for counselor_name in counselors:
            username = counselor_name.lower()
            
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.WARNING(f'Student counselor {counselor_name} already exists'))
                existing_count += 1
                continue
            
            # Create the user
            user = User.objects.create_user(
                username=username,
                email=f'{username}@alims.co.in',
                password=f'{username}@password',
                first_name=counselor_name,
                last_name='',
                role=User.SALES
            )
            
            self.stdout.write(self.style.SUCCESS(f'Created student counselor: {user.username}'))
            created_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} student counselors'))
        if existing_count > 0:
            self.stdout.write(self.style.WARNING(f'{existing_count} student counselors already existed'))
        
        self.stdout.write(self.style.SUCCESS('Login credentials for all created counselors:'))
        self.stdout.write(self.style.SUCCESS('Username: <counselor name in lowercase>'))
        self.stdout.write(self.style.SUCCESS('Password: password'))
        self.stdout.write(self.style.WARNING('Please change the default passwords after first login!'))
