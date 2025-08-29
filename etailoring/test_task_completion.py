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
from etailoring.models import Customer, Fabric, Accessory, Order, Tailor, Task, Commission
from etailoring.business_logic import OrderManager

def test_task_completion():
    # Generate unique usernames
    customer_username = f'testcustomer_{uuid.uuid4().hex[:8]}'
    tailor_username = f'testtailor_{uuid.uuid4().hex[:8]}'
    
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
    
    # Create an order
    order = Order.objects.create(
        customer=customer,
        fabric=fabric,
        total_amount=Decimal('27.25')  # 25.00 (fabric) + 1.50 (thread) + 0.75 (button)
    )
    order.accessories.add(thread, button)
    
    # Assign order to tailor
    task = OrderManager.assign_order_to_tailor(order, tailor)
    
    print(f"Task #{task.id} created with status: {task.status}")
    print(f"Order #{order.id} status: {order.status}")
    
    # Check if commission was created
    commission = task.order.commission_set.first()
    if commission:
        print(f"Commission created: ₱{commission.amount} (status: {commission.status})")
    else:
        print("No commission found!")
    
    # Complete the task
    try:
        completed_commission = OrderManager.complete_task(task)
        print(f"Task #{task.id} completed successfully")
        print(f"Task status updated to: {task.status}")
        print(f"Order #{order.id} status updated to: {order.status}")
        print(f"Commission status: {completed_commission.status}")
        
    except Exception as e:
        print(f"Error completing task: {e}")
    
    # Clean up
    order.delete()
    fabric.delete()
    thread.delete()
    button.delete()
    tailor.delete()
    customer.delete()
    tailor_user.delete()
    customer_user.delete()

if __name__ == '__main__':
    test_task_completion()