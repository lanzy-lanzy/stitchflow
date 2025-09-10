#!/usr/bin/env python
"""
Database Population Script for StitchFlow Tailoring System
This script populates the database with sample data including:
- Admin users
- Tailors with different specialties
- Customers with measurements
- Fabrics and accessories inventory
- Sample orders with various statuses
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta
import json
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stitchflow.settings')
django.setup()

from django.contrib.auth.models import User
from etailoring.models import UserExtension, Customer, Tailor, Fabric, Accessory, Order, Task, Commission, Testimonial
from etailoring.business_logic import PricingManager

def create_admin_users():
    """Create admin user - only admins can create customers and manage the system"""
    print("Creating admin user...")

    # Main admin - the only user who can create customers and manage everything
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@stitchflow.com',
            'first_name': 'System',
            'last_name': 'Administrator',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"✓ Created admin user: {admin_user.username}")

        # Create user extension for admin
        UserExtension.objects.get_or_create(
            user=admin_user,
            defaults={
                'role': 'ADMIN',
                'phone_number': '+63-900-000-0001'
            }
        )

def create_tailors():
    """Create tailor users and profiles"""
    print("Creating tailors...")
    
    tailors_data = [
        {
            'username': 'maria_santos',
            'email': 'maria.santos@stitchflow.com',
            'first_name': 'Maria',
            'last_name': 'Santos',
            'phone': '+63-917-123-4567',
            'specialty': 'Formal Dresses & Evening Gowns',
            'commission_rate': Decimal('15.00')
        },
        {
            'username': 'juan_dela_cruz',
            'email': 'juan.delacruz@stitchflow.com',
            'first_name': 'Juan',
            'last_name': 'Dela Cruz',
            'phone': '+63-918-234-5678',
            'specialty': 'Men\'s Suits & Business Attire',
            'commission_rate': Decimal('12.00')
        },
        {
            'username': 'ana_reyes',
            'email': 'ana.reyes@stitchflow.com',
            'first_name': 'Ana',
            'last_name': 'Reyes',
            'phone': '+63-919-345-6789',
            'specialty': 'Casual Wear & Alterations',
            'commission_rate': Decimal('10.00')
        },
        {
            'username': 'carlos_mendoza',
            'email': 'carlos.mendoza@stitchflow.com',
            'first_name': 'Carlos',
            'last_name': 'Mendoza',
            'phone': '+63-920-456-7890',
            'specialty': 'Traditional Filipino Attire',
            'commission_rate': Decimal('18.00')
        },
        {
            'username': 'rosa_garcia',
            'email': 'rosa.garcia@stitchflow.com',
            'first_name': 'Rosa',
            'last_name': 'Garcia',
            'phone': '+63-921-567-8901',
            'specialty': 'Wedding Dresses & Bridal Wear',
            'commission_rate': Decimal('20.00')
        }
    ]
    
    for tailor_data in tailors_data:
        # Create user
        user, created = User.objects.get_or_create(
            username=tailor_data['username'],
            defaults={
                'email': tailor_data['email'],
                'first_name': tailor_data['first_name'],
                'last_name': tailor_data['last_name'],
                'is_staff': False,
                'is_superuser': False,
            }
        )
        if created:
            user.set_password('tailor123')
            user.save()
        
        # Create user extension for role-based access
        user_extension, ext_created = UserExtension.objects.get_or_create(
            user=user,
            defaults={
                'role': 'TAILOR',
                'phone_number': tailor_data['phone']
            }
        )

        # Create tailor profile
        tailor, created = Tailor.objects.get_or_create(
            user=user,
            defaults={
                'phone_number': tailor_data['phone'],
                'specialty': tailor_data['specialty'],
                'commission_rate': tailor_data['commission_rate']
            }
        )
        if created:
            print(f"✓ Created tailor: {user.first_name} {user.last_name} - {tailor.specialty}")

def create_customers():
    """Create customer users and profiles"""
    print("Creating customers...")
    
    customers_data = [
        {
            'username': 'elena_rodriguez',
            'email': 'elena.rodriguez@email.com',
            'first_name': 'Elena',
            'last_name': 'Rodriguez',
            'phone': '+63-917-111-2222',
            'address': '123 Makati Avenue, Makati City, Metro Manila',
            'measurements': {
                'neck_circumference': 14.5,
                'shoulder_width': 16.0,
                'chest_bust_circumference': 36.0,
                'waist_circumference': 28.0,
                'full_hip_circumference': 38.0,
                'bicep_circumference': 11.0,
                'back_length_nape_to_waist': 16.5
            }
        },
        {
            'username': 'miguel_torres',
            'email': 'miguel.torres@email.com',
            'first_name': 'Miguel',
            'last_name': 'Torres',
            'phone': '+63-918-222-3333',
            'address': '456 Ortigas Center, Pasig City, Metro Manila',
            'measurements': {
                'neck_circumference': 16.0,
                'shoulder_width': 18.5,
                'chest_bust_circumference': 42.0,
                'waist_circumference': 34.0,
                'full_hip_circumference': 40.0,
                'bicep_circumference': 13.5,
                'back_length_nape_to_waist': 18.0
            }
        },
        {
            'username': 'sofia_martinez',
            'email': 'sofia.martinez@email.com',
            'first_name': 'Sofia',
            'last_name': 'Martinez',
            'phone': '+63-919-333-4444',
            'address': '789 BGC, Taguig City, Metro Manila',
            'measurements': {
                'neck_circumference': 13.5,
                'shoulder_width': 15.0,
                'chest_bust_circumference': 34.0,
                'waist_circumference': 26.0,
                'full_hip_circumference': 36.0,
                'bicep_circumference': 10.5,
                'back_length_nape_to_waist': 15.5
            }
        },
        {
            'username': 'ricardo_santos',
            'email': 'ricardo.santos@email.com',
            'first_name': 'Ricardo',
            'last_name': 'Santos',
            'phone': '+63-920-444-5555',
            'address': '321 Quezon Avenue, Quezon City, Metro Manila',
            'measurements': {
                'neck_circumference': 17.0,
                'shoulder_width': 19.0,
                'chest_bust_circumference': 44.0,
                'waist_circumference': 36.0,
                'full_hip_circumference': 42.0,
                'bicep_circumference': 14.0,
                'back_length_nape_to_waist': 19.0
            }
        },
        {
            'username': 'carmen_lopez',
            'email': 'carmen.lopez@email.com',
            'first_name': 'Carmen',
            'last_name': 'Lopez',
            'phone': '+63-921-555-6666',
            'address': '654 Alabang, Muntinlupa City, Metro Manila',
            'measurements': {
                'neck_circumference': 14.0,
                'shoulder_width': 15.5,
                'chest_bust_circumference': 38.0,
                'waist_circumference': 30.0,
                'full_hip_circumference': 40.0,
                'bicep_circumference': 11.5,
                'back_length_nape_to_waist': 17.0
            }
        }
    ]
    
    for customer_data in customers_data:
        # Create user
        user, created = User.objects.get_or_create(
            username=customer_data['username'],
            defaults={
                'email': customer_data['email'],
                'first_name': customer_data['first_name'],
                'last_name': customer_data['last_name'],
                'is_staff': False,
                'is_superuser': False,
            }
        )
        if created:
            user.set_password('customer123')
            user.save()
        
        # Create user extension for role-based access
        user_extension, ext_created = UserExtension.objects.get_or_create(
            user=user,
            defaults={
                'role': 'CUSTOMER',
                'phone_number': customer_data['phone']
            }
        )

        # Create customer profile
        customer, created = Customer.objects.get_or_create(
            user=user,
            defaults={
                'phone_number': customer_data['phone'],
                'address': customer_data['address'],
                'measurements': json.dumps(customer_data['measurements'])
            }
        )
        if created:
            print(f"✓ Created customer: {user.first_name} {user.last_name}")

def create_fabrics():
    """Create fabric inventory"""
    print("Creating fabric inventory...")

    fabrics_data = [
        {
            'name': 'Premium Cotton',
            'description': 'High-quality 100% cotton fabric, perfect for casual wear and shirts',
            'unit_type': 'METERS',
            'quantity': Decimal('150.00'),
            'price_per_unit': Decimal('25.00'),
            'low_stock_threshold': Decimal('20.00')
        },
        {
            'name': 'Silk Charmeuse',
            'description': 'Luxurious silk fabric with a lustrous finish, ideal for formal dresses',
            'unit_type': 'METERS',
            'quantity': Decimal('80.00'),
            'price_per_unit': Decimal('120.00'),
            'low_stock_threshold': Decimal('15.00')
        },
        {
            'name': 'Wool Suiting',
            'description': 'Professional-grade wool blend for business suits and formal wear',
            'unit_type': 'METERS',
            'quantity': Decimal('100.00'),
            'price_per_unit': Decimal('85.00'),
            'low_stock_threshold': Decimal('25.00')
        },
        {
            'name': 'Linen Blend',
            'description': 'Breathable linen-cotton blend, perfect for tropical climate clothing',
            'unit_type': 'METERS',
            'quantity': Decimal('120.00'),
            'price_per_unit': Decimal('35.00'),
            'low_stock_threshold': Decimal('30.00')
        },
        {
            'name': 'Chiffon',
            'description': 'Lightweight, sheer fabric perfect for evening wear and overlays',
            'unit_type': 'METERS',
            'quantity': Decimal('60.00'),
            'price_per_unit': Decimal('45.00'),
            'low_stock_threshold': Decimal('10.00')
        },
        {
            'name': 'Denim',
            'description': 'Sturdy cotton denim fabric for casual pants and jackets',
            'unit_type': 'METERS',
            'quantity': Decimal('90.00'),
            'price_per_unit': Decimal('40.00'),
            'low_stock_threshold': Decimal('20.00')
        },
        {
            'name': 'Satin',
            'description': 'Smooth, glossy fabric perfect for formal wear and linings',
            'unit_type': 'METERS',
            'quantity': Decimal('70.00'),
            'price_per_unit': Decimal('55.00'),
            'low_stock_threshold': Decimal('15.00')
        }
    ]

    for fabric_data in fabrics_data:
        fabric, created = Fabric.objects.get_or_create(
            name=fabric_data['name'],
            defaults=fabric_data
        )
        if created:
            print(f"✓ Created fabric: {fabric.name} - {fabric.quantity} {fabric.unit_type.lower()}")

def create_accessories():
    """Create accessories inventory"""
    print("Creating accessories inventory...")

    accessories_data = [
        {
            'name': 'Pearl Buttons',
            'description': 'Elegant pearl-finish buttons for formal wear',
            'quantity': 500,
            'price_per_unit': Decimal('2.50'),
            'low_stock_threshold': 50
        },
        {
            'name': 'Metal Zippers',
            'description': 'Durable metal zippers in various lengths',
            'quantity': 200,
            'price_per_unit': Decimal('8.00'),
            'low_stock_threshold': 30
        },
        {
            'name': 'Invisible Zippers',
            'description': 'Concealed zippers for dresses and skirts',
            'quantity': 150,
            'price_per_unit': Decimal('12.00'),
            'low_stock_threshold': 25
        },
        {
            'name': 'Shoulder Pads',
            'description': 'Professional shoulder pads for blazers and jackets',
            'quantity': 100,
            'price_per_unit': Decimal('15.00'),
            'low_stock_threshold': 20
        },
        {
            'name': 'Interfacing',
            'description': 'Fusible interfacing for collar and cuff reinforcement',
            'quantity': 80,
            'price_per_unit': Decimal('6.00'),
            'low_stock_threshold': 15
        },
        {
            'name': 'Decorative Trim',
            'description': 'Ornamental trim for embellishing garments',
            'quantity': 300,
            'price_per_unit': Decimal('4.00'),
            'low_stock_threshold': 40
        },
        {
            'name': 'Elastic Bands',
            'description': 'Stretchable elastic for waistbands and cuffs',
            'quantity': 250,
            'price_per_unit': Decimal('3.00'),
            'low_stock_threshold': 35
        }
    ]

    for accessory_data in accessories_data:
        accessory, created = Accessory.objects.get_or_create(
            name=accessory_data['name'],
            defaults=accessory_data
        )
        if created:
            print(f"✓ Created accessory: {accessory.name} - {accessory.quantity} pieces")

def create_sample_orders():
    """Create sample orders with different statuses"""
    print("Creating sample orders...")

    # Get some customers, tailors, fabrics, and accessories
    customers = list(Customer.objects.all())
    tailors = list(Tailor.objects.all())
    fabrics = list(Fabric.objects.all())
    accessories = list(Accessory.objects.all())

    if not customers or not fabrics:
        print("⚠️  Skipping orders creation - no customers or fabrics available")
        return

    orders_data = [
        {
            'customer': customers[0],  # Elena Rodriguez
            'fabric': fabrics[1] if len(fabrics) > 1 else fabrics[0],  # Silk Charmeuse
            'category': 'FORMAL_WEAR',
            'garment_type': 'DRESS',
            'quantity': 1,
            'fabric_type': 'Silk',
            'color_design_preference': 'Elegant navy blue evening dress with subtle beading',
            'accessories_preference': 'Pearl buttons, invisible zipper',
            'status': 'COMPLETED',
            'due_date': datetime.now().date() - timedelta(days=5),
            'measurements': {
                'neck_circumference': 14.5,
                'chest_bust_circumference': 36.0,
                'waist_circumference': 28.0,
                'skirt_dress_length': 45.0
            }
        },
        {
            'customer': customers[1],  # Miguel Torres
            'fabric': fabrics[2] if len(fabrics) > 2 else fabrics[0],  # Wool Suiting
            'category': 'BUSINESS_ATTIRE',
            'garment_type': 'JACKET',
            'quantity': 1,
            'fabric_type': 'Wool Blend',
            'color_design_preference': 'Classic charcoal gray business suit jacket',
            'accessories_preference': 'Shoulder pads, metal buttons',
            'status': 'IN_PROGRESS',
            'due_date': datetime.now().date() + timedelta(days=10),
            'measurements': {
                'neck_circumference': 16.0,
                'chest_bust_circumference': 42.0,
                'waist_circumference': 34.0,
                'jacket_length_shoulder_to_hem': 28.0
            }
        },
        {
            'customer': customers[2],  # Sofia Martinez
            'fabric': fabrics[0],  # Premium Cotton
            'category': 'CASUAL_WEAR',
            'garment_type': 'BLOUSE',
            'quantity': 2,
            'fabric_type': 'Cotton',
            'color_design_preference': 'White and light blue casual blouses',
            'accessories_preference': 'Pearl buttons, standard trim',
            'status': 'ASSIGNED',
            'due_date': datetime.now().date() + timedelta(days=7),
            'measurements': {
                'neck_circumference': 13.5,
                'chest_bust_circumference': 34.0,
                'waist_circumference': 26.0,
                'blouse_length_shoulder_to_hem': 24.0
            }
        },
        {
            'customer': customers[3],  # Ricardo Santos
            'fabric': fabrics[5] if len(fabrics) > 5 else fabrics[0],  # Denim
            'category': 'CASUAL_WEAR',
            'garment_type': 'PANTS',
            'quantity': 1,
            'fabric_type': 'Denim',
            'color_design_preference': 'Classic blue jeans with straight cut',
            'accessories_preference': 'Metal zipper, standard pockets',
            'status': 'PENDING',
            'due_date': datetime.now().date() + timedelta(days=14),
            'measurements': {
                'waist_circumference': 36.0,
                'full_hip_circumference': 42.0,
                'inseam_crotch_to_ankle': 32.0,
                'outseam_waist_to_ankle': 42.0
            }
        },
        {
            'customer': customers[4],  # Carmen Lopez
            'fabric': fabrics[4] if len(fabrics) > 4 else fabrics[0],  # Chiffon
            'category': 'SPECIAL_OCCASION',
            'garment_type': 'SKIRT',
            'quantity': 1,
            'fabric_type': 'Chiffon',
            'color_design_preference': 'Flowing maxi skirt in soft pink',
            'accessories_preference': 'Invisible zipper, decorative trim',
            'status': 'DELIVERED',
            'due_date': datetime.now().date() - timedelta(days=15),
            'measurements': {
                'waist_circumference': 30.0,
                'full_hip_circumference': 40.0,
                'skirt_dress_length': 38.0
            }
        }
    ]

    for i, order_data in enumerate(orders_data):
        # Calculate pricing using the business logic
        total_amount = PricingManager.calculate_order_total(
            order_data['garment_type'],
            order_data['quantity']
        )
        down_payment = PricingManager.calculate_down_payment(total_amount)

        # Create order with basic fields first
        order_fields = {
            'customer': order_data['customer'],
            'fabric': order_data['fabric'],
            'category': order_data['category'],
            'garment_type': order_data['garment_type'],
            'quantity': order_data['quantity'],
            'fabric_type': order_data['fabric_type'],
            'color_design_preference': order_data['color_design_preference'],
            'accessories_preference': order_data['accessories_preference'],
            'status': order_data['status'],
            'due_date': order_data['due_date'],
            'total_amount': total_amount,
            'down_payment_amount': down_payment,
            'remaining_balance': total_amount - down_payment,
            'down_payment_status': 'PAID' if order_data['status'] in ['COMPLETED', 'DELIVERED', 'IN_PROGRESS'] else 'PENDING',
        }

        # Add measurement fields directly
        measurements = order_data['measurements']
        for field_name, value in measurements.items():
            if hasattr(Order, field_name):
                order_fields[field_name] = Decimal(str(value))

        order = Order.objects.create(**order_fields)

        # Add some accessories to orders
        if accessories and i < 3:  # Add accessories to first 3 orders
            order.accessories.add(accessories[i % len(accessories)])

        # Create tasks for assigned/in-progress orders
        if order_data['status'] in ['ASSIGNED', 'IN_PROGRESS', 'COMPLETED'] and tailors:
            tailor = tailors[i % len(tailors)]  # Distribute among tailors
            task = Task.objects.create(
                order=order,
                tailor=tailor,
                status='COMPLETED' if order_data['status'] == 'COMPLETED' else order_data['status'],
                assigned_at=timezone.now() - timedelta(days=i+1),
                completed_at=timezone.now() - timedelta(days=1) if order_data['status'] == 'COMPLETED' else None
            )

            # Create commission for completed tasks
            if order_data['status'] == 'COMPLETED':
                commission_amount = (tailor.commission_rate / 100) * order.total_amount
                Commission.objects.create(
                    tailor=tailor,
                    amount=commission_amount,
                    order=order,
                    status='PAID'
                )

        print(f"✓ Created order: {order.garment_type} for {order.customer.user.first_name} - Status: {order.status}")

def create_testimonials():
    """Create sample testimonials"""
    print("Creating testimonials...")

    customers = list(Customer.objects.all())
    if not customers:
        print("⚠️  Skipping testimonials - no customers available")
        return

    testimonials_data = [
        {
            'name': f"{customers[0].user.first_name} {customers[0].user.last_name}",
            'role': 'Business Executive',
            'company': 'Corporate Client',
            'quote': 'Absolutely amazing work! The evening dress was perfect for my special event. The attention to detail and quality of craftsmanship exceeded my expectations.'
        },
        {
            'name': f"{customers[4].user.first_name} {customers[4].user.last_name}",
            'role': 'Fashion Enthusiast',
            'company': 'Regular Customer',
            'quote': 'Beautiful chiffon skirt that fits perfectly. The team was professional and delivered exactly what I wanted. Highly recommended!'
        },
        {
            'name': f"{customers[2].user.first_name} {customers[2].user.last_name}",
            'role': 'Professional',
            'company': 'Satisfied Customer',
            'quote': 'Great service and quality work. The blouses are well-made and the measurements were spot on. Will definitely come back for more orders.'
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
            print(f"✓ Created testimonial from {testimonial.name}")

if __name__ == '__main__':
    print("🧵 Starting StitchFlow Database Population...")
    print("=" * 50)

    try:
        create_admin_users()
        print()
        create_tailors()
        print()
        create_fabrics()
        print()
        create_accessories()
        print()
        create_testimonials()
        print()

        print("✅ Database population completed successfully!")
        print("\n📋 Summary:")
        print(f"   • Admin user: {User.objects.filter(is_staff=True).count()}")
        print(f"   • Tailors: {Tailor.objects.count()}")
        print(f"   • Fabrics: {Fabric.objects.count()}")
        print(f"   • Accessories: {Accessory.objects.count()}")
        print(f"   • Orders: {Order.objects.count()}")
        print(f"   • Tasks: {Task.objects.count()}")
        print(f"   • Commissions: {Commission.objects.count()}")
        print(f"   • Testimonials: {Testimonial.objects.count()}")

        print("\n🔐 Login Credentials:")
        print("   Admin: admin / admin123 (creates customers & manages system)")
        print("   Tailors: [username] / tailor123 (view assigned tasks)")

        print("\n📝 Note:")
        print("   • Customers are created by admin through the system")
        print("   • No separate customer login accounts needed")
        print("   • Admin manages all customer data and orders")

        print("\n🎯 Next Steps:")
        print("   1. Run: uv run python manage.py runserver")
        print("   2. Visit: http://localhost:8000")
        print("   3. Login with admin credentials to explore the system")

    except Exception as e:
        print(f"❌ Error during population: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
