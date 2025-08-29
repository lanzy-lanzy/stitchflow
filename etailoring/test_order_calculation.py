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

from etailoring.models import Customer, Fabric, Accessory, Order, User

def test_order_calculation():
    # Generate a unique username
    unique_username = f'testuser_{uuid.uuid4().hex[:8]}'
    
    # Create a test user
    user = User.objects.create_user(
        username=unique_username,
        email='test@example.com',
        password='testpass123'
    )
    
    # Create a test customer
    customer = Customer.objects.create(
        user=user,
        phone_number='1234567890',
        address='123 Test St'
    )
    
    # Create a test fabric
    fabric = Fabric.objects.create(
        name='Cotton',
        unit_type='METERS',
        quantity=Decimal('10.00'),
        price_per_unit=Decimal('15.00')
    )
    
    # Create test accessories
    button = Accessory.objects.create(
        name='Button',
        quantity=100,
        price_per_unit=Decimal('0.50')
    )
    
    zipper = Accessory.objects.create(
        name='Zipper',
        quantity=50,
        price_per_unit=Decimal('2.00')
    )
    
    # Create an order without accessories first
    order = Order.objects.create(
        customer=customer,
        fabric=fabric,
        total_amount=fabric.price_per_unit  # Initial amount with just fabric
    )
    
    # Add accessories to the order
    order.accessories.add(button, zipper)
    
    # Recalculate total amount
    calculated_total = order.calculate_total_amount()
    expected_total = fabric.price_per_unit + button.price_per_unit + zipper.price_per_unit
    
    print(f"Fabric price: ₱{fabric.price_per_unit}")
    print(f"Button price: ₱{button.price_per_unit}")
    print(f"Zipper price: ₱{zipper.price_per_unit}")
    print(f"Expected total: ₱{expected_total}")
    print(f"Calculated total: ₱{calculated_total}")
    
    # Verify the calculation
    assert calculated_total == expected_total, f"Expected {expected_total}, got {calculated_total}"
    
    print("Test passed! Order total amount calculation is working correctly.")
    
    # Clean up
    order.delete()
    zipper.delete()
    button.delete()
    fabric.delete()
    customer.delete()
    user.delete()

if __name__ == '__main__':
    test_order_calculation()