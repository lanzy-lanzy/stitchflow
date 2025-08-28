from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ...models import Customer, UserExtension

class Command(BaseCommand):
    help = 'Manage customer operations'

    def add_arguments(self, parser):
        parser.add_argument(
            'operation',
            type=str,
            help='Operation to perform: list, create, update, delete, search',
            choices=['list', 'create', 'update', 'delete', 'search']
        )
        
        parser.add_argument(
            '--customer-id',
            type=int,
            help='Customer ID for search/update/delete operations'
        )
        
        parser.add_argument(
            '--username',
            type=str,
            help='Username for create/search operations'
        )
        
        parser.add_argument(
            '--email',
            type=str,
            help='Email for create/update operations'
        )
        
        parser.add_argument(
            '--first-name',
            type=str,
            help='First name for create/update operations'
        )
        
        parser.add_argument(
            '--last-name',
            type=str,
            help='Last name for create/update operations'
        )
        
        parser.add_argument(
            '--phone',
            type=str,
            help='Phone number for create/update operations'
        )
        
        parser.add_argument(
            '--address',
            type=str,
            help='Address for create/update operations'
        )
        
        parser.add_argument(
            '--search-term',
            type=str,
            help='Search term for search operation'
        )

    def handle(self, *args, **options):
        operation = options['operation']
        
        try:
            if operation == 'list':
                self.list_customers()
            elif operation == 'create':
                self.create_customer(options)
            elif operation == 'update':
                self.update_customer(options)
            elif operation == 'delete':
                self.delete_customer(options)
            elif operation == 'search':
                self.search_customers(options)
                
            self.stdout.write(
                self.style.SUCCESS(f'Successfully completed {operation} operation')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during {operation} operation: {str(e)}')
            )

    def list_customers(self):
        """List all customers"""
        customers = Customer.objects.all().select_related('user')
        
        if not customers.exists():
            self.stdout.write('No customers found')
            return
            
        self.stdout.write('=== CUSTOMER LIST ===')
        for customer in customers:
            self.stdout.write(
                f"ID: {customer.id} | "
                f"Name: {customer.user.first_name} {customer.user.last_name} | "
                f"Username: {customer.user.username} | "
                f"Email: {customer.user.email} | "
                f"Phone: {customer.phone_number}"
            )

    def create_customer(self, options):
        """Create a new customer"""
        username = options.get('username')
        email = options.get('email')
        first_name = options.get('first_name')
        last_name = options.get('last_name')
        phone = options.get('phone')
        address = options.get('address')
        
        if not all([username, email, first_name, last_name, phone, address]):
            self.stdout.write(
                self.style.ERROR(
                    'All customer details are required: --username, --email, '
                    '--first-name, --last-name, --phone, --address'
                )
            )
            return
            
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'User with username {username} already exists'))
            return
            
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.ERROR(f'User with email {email} already exists'))
            return
            
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password='customer123'  # Default password
        )
        
        # Create customer
        customer = Customer.objects.create(
            user=user,
            phone_number=phone,
            address=address,
            measurements={}  # Empty measurements by default
        )
        
        # Create user extension
        UserExtension.objects.create(
            user=user,
            role='CUSTOMER',
            phone_number=phone
        )
        
        self.stdout.write(
            f"Successfully created customer: {customer.user.username} "
            f"(ID: {customer.id})"
        )
        self.stdout.write(
            f"Default password: customer123 (please change after first login)"
        )

    def update_customer(self, options):
        """Update an existing customer"""
        customer_id = options.get('customer_id')
        
        if not customer_id:
            self.stdout.write(self.style.ERROR('--customer-id is required for update operation'))
            return
            
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Customer with ID {customer_id} not found'))
            return
            
        # Update fields if provided
        if options.get('email'):
            customer.user.email = options['email']
            
        if options.get('first_name'):
            customer.user.first_name = options['first_name']
            
        if options.get('last_name'):
            customer.user.last_name = options['last_name']
            
        if options.get('phone'):
            customer.phone_number = options['phone']
            # Also update user extension
            try:
                user_extension = UserExtension.objects.get(user=customer.user)
                user_extension.phone_number = options['phone']
                user_extension.save()
            except UserExtension.DoesNotExist:
                pass  # User extension might not exist
                
        if options.get('address'):
            customer.address = options['address']
            
        # Save changes
        customer.user.save()
        customer.save()
        
        self.stdout.write(f"Successfully updated customer: {customer.user.username}")

    def delete_customer(self, options):
        """Delete a customer"""
        customer_id = options.get('customer_id')
        
        if not customer_id:
            self.stdout.write(self.style.ERROR('--customer-id is required for delete operation'))
            return
            
        try:
            customer = Customer.objects.get(id=customer_id)
            username = customer.user.username
            
            # Delete user (this will cascade delete customer and user extension)
            customer.user.delete()
            
            self.stdout.write(f"Successfully deleted customer: {username}")
        except Customer.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Customer with ID {customer_id} not found'))

    def search_customers(self, options):
        """Search customers by term"""
        search_term = options.get('search_term')
        username = options.get('username')
        customer_id = options.get('customer_id')
        
        # Build query
        customers = Customer.objects.all().select_related('user')
        
        if customer_id:
            customers = customers.filter(id=customer_id)
        elif search_term:
            customers = customers.filter(
                user__first_name__icontains=search_term
            ) | customers.filter(
                user__last_name__icontains=search_term
            ) | customers.filter(
                user__username__icontains=search_term
            ) | customers.filter(
                phone_number__icontains=search_term
            )
        elif username:
            customers = customers.filter(user__username__icontains=username)
        else:
            self.stdout.write(self.style.ERROR('Either --search-term, --username, or --customer-id is required for search operation'))
            return
            
        if not customers.exists():
            self.stdout.write('No customers found matching the criteria')
            return
            
        self.stdout.write(f'=== SEARCH RESULTS ({customers.count()} found) ===')
        for customer in customers:
            self.stdout.write(
                f"ID: {customer.id} | "
                f"Name: {customer.user.first_name} {customer.user.last_name} | "
                f"Username: {customer.user.username} | "
                f"Email: {customer.user.email} | "
                f"Phone: {customer.phone_number}"
            )