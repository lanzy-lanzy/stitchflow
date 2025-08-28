from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ...models import UserExtension, Customer, Tailor, Fabric, Accessory, Order, Task, Commission, Testimonial

class Command(BaseCommand):
    help = 'Populate the database with sample data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()

        self.stdout.write('Populating sample data...')
        self.populate_data()
        self.stdout.write(
            self.style.SUCCESS('Successfully populated sample data')
        )

    def clear_data(self):
        """Clear all existing data"""
        Commission.objects.all().delete()
        Task.objects.all().delete()
        Order.objects.all().delete()
        Accessory.objects.all().delete()
        Fabric.objects.all().delete()
        Tailor.objects.all().delete()
        Customer.objects.all().delete()
        Testimonial.objects.all().delete()
        UserExtension.objects.filter(role__in=['CUSTOMER', 'TAILOR']).delete()
        User.objects.filter(is_staff=False).delete()
        
        self.stdout.write('Existing data cleared.')

    def populate_data(self):
        """Populate the database with sample data"""
        
        # Create admin user if not exists
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@stitchflow.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write('Created admin user')
        
        # Create user extensions for admin if not exists
        UserExtension.objects.get_or_create(
            user=admin_user,
            defaults={
                'role': 'ADMIN',
                'phone_number': '123-456-7890'
            }
        )

        # Create sample testimonials
        testimonials_data = [
            {
                'name': 'Sarah Johnson',
                'role': 'Owner',
                'company': 'Elite Tailoring',
                'quote': 'El Senior Dumingag has transformed how we manage our orders and tailors. The commission tracking alone has saved us hours of manual calculations each month.'
            },
            {
                'name': 'Michael Chen',
                'role': 'Manager',
                'company': 'Fashion House',
                'quote': 'The inventory management system prevents us from running out of essential fabrics. The low-stock alerts have been a game-changer for our procurement process.'
            },
            {
                'name': 'Robert Williams',
                'role': 'Master Tailor',
                'company': 'Williams Custom Tailoring',
                'quote': 'As a tailor, I love how easy it is to see my assigned tasks and track my commissions. The mobile-friendly interface means I can check updates on the go.'
            },
            {
                'name': 'Emily Rodriguez',
                'role': 'Operations Manager',
                'company': 'Stitch Perfect',
                'quote': 'The role-based access control means our staff only sees what they need to. As a manager, I appreciate the comprehensive reporting and analytics features.'
            },
            {
                'name': 'David Kim',
                'role': 'CEO',
                'company': 'Modern Tailors Inc.',
                'quote': 'Since implementing El Senior Dumingag, our order fulfillment time has decreased by 30% and customer satisfaction has increased significantly. The ROI has been incredible.'
            }
        ]

        for testimonial_data in testimonials_data:
            testimonial, created = Testimonial.objects.get_or_create(
                name=testimonial_data['name'],
                defaults={
                    'role': testimonial_data['role'],
                    'company': testimonial_data['company'],
                    'quote': testimonial_data['quote'],
                    'is_active': True
                }
            )
            
            if created:
                self.stdout.write(f"Created testimonial from: {testimonial.name}")

        # Create sample customers
        customers_data = [
            {
                'username': 'john_doe',
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'phone_number': '555-0101',
                'address': '123 Main St, City, State 12345',
                'measurements': {
                    'chest': 42,
                    'waist': 36,
                    'hip': 40,
                    'inseam': 32,
                    'sleeve': 34,
                    'shoulder': 18
                }
            },
            {
                'username': 'jane_smith',
                'email': 'jane@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'phone_number': '555-0102',
                'address': '456 Oak Ave, City, State 12345',
                'measurements': {
                    'chest': 38,
                    'waist': 32,
                    'hip': 38,
                    'inseam': 30,
                    'sleeve': 31,
                    'shoulder': 16
                }
            },
            {
                'username': 'bob_johnson',
                'email': 'bob@example.com',
                'first_name': 'Bob',
                'last_name': 'Johnson',
                'phone_number': '555-0103',
                'address': '789 Pine Rd, City, State 12345',
                'measurements': {
                    'chest': 44,
                    'waist': 38,
                    'hip': 42,
                    'inseam': 34,
                    'sleeve': 35,
                    'shoulder': 19
                }
            }
        ]

        for customer_data in customers_data:
            user, created = User.objects.get_or_create(
                username=customer_data['username'],
                defaults={
                    'email': customer_data['email'],
                    'first_name': customer_data['first_name'],
                    'last_name': customer_data['last_name']
                }
            )
            
            if created:
                user.set_password('customer123')
                user.save()
            
            customer, created = Customer.objects.get_or_create(
                user=user,
                defaults={
                    'phone_number': customer_data['phone_number'],
                    'address': customer_data['address'],
                    'measurements': customer_data['measurements']
                }
            )
            
            if created:
                UserExtension.objects.get_or_create(
                    user=user,
                    defaults={
                        'role': 'CUSTOMER',
                        'phone_number': customer_data['phone_number']
                    }
                )
                self.stdout.write(f"Created customer: {customer.user.username}")

        # Create sample tailors
        tailors_data = [
            {
                'username': 'tailor1',
                'email': 'tailor1@example.com',
                'first_name': 'Alice',
                'last_name': 'Williams',
                'phone_number': '555-0201',
                'specialty': 'Suits',
                'commission_rate': '15.00'
            },
            {
                'username': 'tailor2',
                'email': 'tailor2@example.com',
                'first_name': 'Charlie',
                'last_name': 'Brown',
                'phone_number': '555-0202',
                'specialty': 'Dresses',
                'commission_rate': '12.00'
            }
        ]

        for tailor_data in tailors_data:
            user, created = User.objects.get_or_create(
                username=tailor_data['username'],
                defaults={
                    'email': tailor_data['email'],
                    'first_name': tailor_data['first_name'],
                    'last_name': tailor_data['last_name']
                }
            )
            
            if created:
                user.set_password('tailor123')
                user.save()
            
            tailor, created = Tailor.objects.get_or_create(
                user=user,
                defaults={
                    'phone_number': tailor_data['phone_number'],
                    'specialty': tailor_data['specialty'],
                    'commission_rate': tailor_data['commission_rate']
                }
            )
            
            if created:
                UserExtension.objects.get_or_create(
                    user=user,
                    defaults={
                        'role': 'TAILOR',
                        'phone_number': tailor_data['phone_number']
                    }
                )
                self.stdout.write(f"Created tailor: {tailor.user.username}")

        # Create sample fabrics
        fabrics_data = [
            {
                'name': 'Wool Suiting',
                'description': 'Premium wool fabric for suits',
                'unit_type': 'METERS',
                'quantity': '50.00',
                'price_per_unit': '25.00',
                'low_stock_threshold': '10.00'
            },
            {
                'name': 'Cotton Poplin',
                'description': 'Lightweight cotton fabric for shirts',
                'unit_type': 'METERS',
                'quantity': '30.00',
                'price_per_unit': '12.00',
                'low_stock_threshold': '5.00'
            },
            {
                'name': 'Silk Satin',
                'description': 'Luxury silk fabric for evening wear',
                'unit_type': 'METERS',
                'quantity': '15.00',
                'price_per_unit': '45.00',
                'low_stock_threshold': '5.00'
            },
            {
                'name': 'Denim',
                'description': 'Classic denim fabric for jeans',
                'unit_type': 'YARDS',
                'quantity': '100',
                'price_per_unit': '8.00',
                'low_stock_threshold': '20'
            }
        ]

        for fabric_data in fabrics_data:
            fabric, created = Fabric.objects.get_or_create(
                name=fabric_data['name'],
                defaults={
                    'description': fabric_data['description'],
                    'unit_type': fabric_data['unit_type'],
                    'quantity': fabric_data['quantity'],
                    'price_per_unit': fabric_data['price_per_unit'],
                    'low_stock_threshold': fabric_data['low_stock_threshold']
                }
            )
            
            if created:
                self.stdout.write(f"Created fabric: {fabric.name}")

        # Create sample accessories
        accessories_data = [
            {
                'name': 'Buttons (Black)',
                'description': 'Black plastic buttons, pack of 10',
                'quantity': 50,
                'price_per_unit': '2.50',
                'low_stock_threshold': 10
            },
            {
                'name': 'Zippers (Invisible)',
                'description': 'Invisible zippers, 7 inches, pack of 5',
                'quantity': 25,
                'price_per_unit': '8.00',
                'low_stock_threshold': 5
            },
            {
                'name': 'Thread (Nylon)',
                'description': 'Nylon thread, assorted colors, 100m spool',
                'quantity': 40,
                'price_per_unit': '3.50',
                'low_stock_threshold': 10
            },
            {
                'name': 'Interfacing',
                'description': 'Fusible interfacing, 20 inches wide',
                'quantity': 15,
                'price_per_unit': '5.00',
                'low_stock_threshold': 5
            }
        ]

        for accessory_data in accessories_data:
            accessory, created = Accessory.objects.get_or_create(
                name=accessory_data['name'],
                defaults={
                    'description': accessory_data['description'],
                    'quantity': accessory_data['quantity'],
                    'price_per_unit': accessory_data['price_per_unit'],
                    'low_stock_threshold': accessory_data['low_stock_threshold']
                }
            )
            
            if created:
                self.stdout.write(f"Created accessory: {accessory.name}")

        self.stdout.write('Sample data population completed.')