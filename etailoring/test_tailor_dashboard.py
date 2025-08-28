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

from etailoring.models import Customer, Fabric, Accessory, Order, User, Tailor, Task, Commission
from etailoring.serializers import TaskSerializer

def test_tailor_dashboard_enhancement():
    # Generate a unique username
    unique_username = f'testuser_{uuid.uuid4().hex[:8]}'
    
    # Create a test user for customer
    customer_user = User.objects.create_user(
        username=unique_username,
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='Customer'
    )
    
    # Create a test customer
    customer = Customer.objects.create(
        user=customer_user,
        phone_number='1234567890',
        address='123 Test St, Test City',
        measurements={
            'chest': 42,
            'waist': 36,
            'hips': 40,
            'inseam': 32
        }
    )
    
    # Create a test user for tailor
    tailor_user = User.objects.create_user(
        username=f'tailor_{uuid.uuid4().hex[:8]}',
        email='tailor@example.com',
        password='testpass123',
        first_name='Test',
        last_name='Tailor'
    )
    
    # Create a test tailor
    tailor = Tailor.objects.create(
        user=tailor_user,
        phone_number='0987654321',
        specialty='Suits',
        commission_rate=Decimal('15.00')
    )
    
    # Create a test fabric
    fabric = Fabric.objects.create(
        name='Wool',
        unit_type='METERS',
        quantity=Decimal('10.00'),
        price_per_unit=Decimal('25.00')
    )
    
    # Create test accessories
    button = Accessory.objects.create(
        name='Premium Button',
        quantity=100,
        price_per_unit=Decimal('1.50')
    )
    
    zipper = Accessory.objects.create(
        name='Gold Zipper',
        quantity=50,
        price_per_unit=Decimal('5.00')
    )
    
    # Create an order
    order = Order.objects.create(
        customer=customer,
        fabric=fabric,
        total_amount=fabric.price_per_unit + button.price_per_unit + zipper.price_per_unit
    )
    
    # Add accessories to the order
    order.accessories.add(button, zipper)
    
    # Create a task for the order
    task = Task.objects.create(
        order=order,
        tailor=tailor,
        status='ASSIGNED'
    )
    
    # Create a commission for the task
    commission = Commission.objects.create(
        tailor=tailor,
        amount=Decimal('4.50'),  # 15% of $30
        order=order,
        status='PENDING'
    )
    
    # Test the enhanced TaskSerializer
    serializer = TaskSerializer(task)
    serialized_data = serializer.data
    
    print("Enhanced TaskSerializer Output:")
    print(f"Task ID: {serialized_data['id']}")
    print(f"Order ID: {serialized_data['order_details']['id']}")
    print(f"Customer Name: {serialized_data['customer_name']}")
    print(f"Customer Phone: {serialized_data['customer_phone']}")
    print(f"Customer Address: {serialized_data['customer_address']}")
    print(f"Fabric: {serialized_data['order_details']['fabric']}")
    print(f"Total Amount: ${serialized_data['order_details']['total_amount']}")
    print(f"Commission Amount: ${serialized_data['commission_amount']}")
    print(f"Measurements: {serialized_data['order_measurements']}")
    
    # Verify that all the new fields are present
    required_fields = ['customer_phone', 'customer_address', 'order_measurements']
    for field in required_fields:
        if field not in serialized_data:
            print(f"ERROR: Missing field {field}")
            return False
    
    print("\nTest passed! Enhanced TaskSerializer includes comprehensive customer and order information.")
    
    # Clean up
    commission.delete()
    task.delete()
    order.delete()
    zipper.delete()
    button.delete()
    fabric.delete()
    tailor.delete()
    customer.delete()
    tailor_user.delete()
    customer_user.delete()
    
    return True

if __name__ == '__main__':
    success = test_tailor_dashboard_enhancement()
    if success:
        print("All tests passed!")
    else:
        print("Some tests failed!")
        sys.exit(1)