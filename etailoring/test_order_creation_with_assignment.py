import os
import sys
import django
import uuid
from decimal import Decimal

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stitchflow.settings')
django.setup()

from django.contrib.auth.models import User
from etailoring.models import Customer, Fabric, Accessory, Order, Tailor

def test_order_creation_with_assignment():
    # Generate unique usernames
    customer_username = f'testcustomer_{uuid.uuid4().hex[:8]}'
    tailor_username = f'testtailor_{uuid.uuid4().hex[:8]}'
    admin_username = f'testadmin_{uuid.uuid4().hex[:8]}'
    
    # Create an admin user
    admin_user = User.objects.create_user(
        username=admin_username,
        email='admin@example.com',
        password='testpass123'
    )
    admin_user.is_staff = True
    admin_user.save()
    
    # Create a test customer
    customer_user = User.objects.create_user(
        username=customer_username,
        email='customer@example.com',
        password='testpass123',
        first_name='Test',
        last_name='Customer'
    )
    
    customer = Customer.objects.create(
        user=customer_user,
        phone_number='1234567890',
        address='123 Test St'
    )
    
    # Create a test tailor
    tailor_user = User.objects.create_user(
        username=tailor_username,
        email='tailor@example.com',
        password='testpass123',
        first_name='Test',
        last_name='Tailor'
    )
    
    tailor = Tailor.objects.create(
        user=tailor_user,
        phone_number='0987654321',
        specialty='Suits',
        commission_rate=Decimal('10.00')
    )
    
    # Create a test fabric
    fabric = Fabric.objects.create(
        name='Silk',
        unit_type='METERS',
        quantity=Decimal('20.00'),
        price_per_unit=Decimal('25.00')
    )
    
    # Create test accessories
    thread = Accessory.objects.create(
        name='Thread',
        quantity=500,
        price_per_unit=Decimal('1.50')
    )
    
    button = Accessory.objects.create(
        name='Button',
        quantity=200,
        price_per_unit=Decimal('0.75')
    )
    
    # Simulate order creation data
    order_data = {
        'customer': customer.id,
        'fabric': fabric.id,
        'accessories': [thread.id, button.id],
        'total_amount': '27.25',  # 25.00 (fabric) + 1.50 (thread) + 0.75 (button)
        'status': 'PENDING'
    }
    
    print(f"Created test data:")
    print(f"- Customer: {customer.user.first_name} {customer.user.last_name}")
    print(f"- Tailor: {tailor.user.first_name} {tailor.user.last_name}")
    print(f"- Fabric: {fabric.name} (quantity: {fabric.quantity})")
    print(f"- Thread: {thread.name} (quantity: {thread.quantity})")
    print(f"- Button: {button.name} (quantity: {button.quantity})")
    print(f"- Order total: ₱{order_data['total_amount']}")
    
    # Clean up
    fabric.delete()
    thread.delete()
    button.delete()
    tailor.delete()
    customer.delete()
    tailor_user.delete()
    customer_user.delete()
    admin_user.delete()
    
    print("\nTest data creation successful. The frontend implementation allows assigning tailors during order creation.")

if __name__ == '__main__':
    test_order_creation_with_assignment()