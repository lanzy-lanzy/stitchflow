"""
Test script to verify the payment and commission functionality.
"""
import os
import django
from django.utils import timezone

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stitchflow.settings')
django.setup()

from django.contrib.auth.models import User
from decimal import Decimal
from etailoring.models import Customer, Tailor, Fabric, Accessory, Order, Task, Commission
from etailoring.business_logic import OrderManager

def test_payment_commission_workflow():
    print("Testing payment and commission workflow...")
    
    # Create test users
    customer_user = User.objects.create_user(
        username='test_customer',
        email='customer@test.com',
        password='testpass123',
        first_name='Test',
        last_name='Customer'
    )
    
    tailor_user = User.objects.create_user(
        username='test_tailor',
        email='tailor@test.com',
        password='testpass123',
        first_name='Test',
        last_name='Tailor'
    )
    
    # Create customer and tailor
    customer = Customer.objects.create(
        user=customer_user,
        phone_number='1234567890',
        address='123 Test St, Test City'
    )
    
    tailor = Tailor.objects.create(
        user=tailor_user,
        phone_number='0987654321',
        specialty='Suits',
        commission_rate=Decimal('15.00')  # 15% commission
    )
    
    # Create fabric and accessories
    fabric = Fabric.objects.create(
        name='Premium Wool',
        unit_type='METERS',
        quantity=Decimal('100.00'),
        price_per_unit=Decimal('50.00'),
        low_stock_threshold=Decimal('10.00')
    )
    
    accessory = Accessory.objects.create(
        name='Gold Buttons',
        quantity=50,
        price_per_unit=Decimal('5.00'),
        low_stock_threshold=10
    )
    
    # Create order
    order = Order.objects.create(
        customer=customer,
        fabric=fabric,
        total_amount=Decimal('100.00')  # ₱50 fabric + ₱50 for accessories (estimated)
    )
    order.accessories.add(accessory)
    
    print(f"Created order #{order.id} for ₱{order.total_amount}")
    
    # Assign order to tailor
    task = OrderManager.assign_order_to_tailor(order, tailor)
    print(f"Assigned order to tailor. Task ID: {task.id}")
    
    # Start task
    started_task = OrderManager.start_task(task)
    print(f"Started task. Status: {started_task.status}")
    
    # Complete task
    completed_task = OrderManager.complete_task(started_task)
    print(f"Completed task. Status: {completed_task.status}")
    
    # Verify commission was created
    commission = Commission.objects.get(order=order, tailor=tailor)
    expected_commission = (tailor.commission_rate / 100) * order.total_amount
    print(f"Commission created. Amount: ₱{commission.amount} (expected: ₱{expected_commission})")
    
    # Process customer payment
    order.payment_status = 'PAID'
    order.paid_at = timezone.now()
    order.save()
    print(f"Processed customer payment. Order status: {order.payment_status}")
    
    # Pay commission
    commission.status = 'PAID'
    commission.paid_at = timezone.now()
    commission.save()
    print(f"Paid commission to tailor. Commission status: {commission.status}")
    
    print("Test completed successfully!")

if __name__ == '__main__':
    test_payment_commission_workflow()