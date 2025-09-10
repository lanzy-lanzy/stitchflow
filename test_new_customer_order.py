#!/usr/bin/env python
"""
Test script to validate the new customer order creation functionality.
This script tests the integration between customer creation and order creation.
"""

import os
import sys
import django
from django.test import TestCase
from django.contrib.auth.models import User

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stitchflow.settings')
django.setup()

from etailoring.models import Customer, Fabric, Accessory, Order
from etailoring.serializers import CustomerSerializer, OrderSerializer


def test_new_customer_order_workflow():
    """Test the complete workflow of creating an order with a new customer."""
    print("Testing new customer order creation workflow...")
    
    # Step 1: Create a fabric for the order
    fabric = Fabric.objects.create(
        name='Test Cotton Fabric',
        unit_type='YARD',
        price_per_unit=25.00,
        quantity=100,
        low_stock_threshold=10
    )
    print(f"✓ Created fabric: {fabric.name}")
    
    # Step 2: Create an accessory for the order
    accessory = Accessory.objects.create(
        name='Test Button',
        description='Standard button for testing',
        quantity=50,
        price_per_unit=2.00,
        low_stock_threshold=5
    )
    print(f"✓ Created accessory: {accessory.name}")
    
    # Step 3: Simulate new customer creation (as done by frontend)
    customer_data = {
        'user': {
            'username': 'newcustomer_test',
            'email': 'newcustomer@test.com',
            'password': 'testpassword123',
            'first_name': 'John',
            'last_name': 'Doe'
        },
        'phone_number': '1234567890',
        'address': '123 Test Street, Test City',
        'measurements': {
            'chest': 40.0,
            'waist': 32.0,
            'hip': 38.0
        }
    }
    
    customer_serializer = CustomerSerializer(data=customer_data)
    if customer_serializer.is_valid():
        customer = customer_serializer.save()
        print(f"✓ Created customer: {customer.get_full_name()}")
    else:
        print(f"✗ Customer creation failed: {customer_serializer.errors}")
        return False
    
    # Step 4: Create order with the new customer (as done by frontend)
    order_data = {
        'customer_id': customer.id,
        'fabric_id': fabric.id,
        'accessories_ids': [accessory.id],
        'category': 'CASUAL_WEAR',
        'garment_type': 'BLOUSE',
        'quantity': 2,
        'fabric_type': 'Cotton blend',
        'color_design_preference': 'Blue with white collar',
        'due_date': '2025-09-20',
        'total_amount': 54.00,  # (25 * 2) + (2 * 2) = 54
        'status': 'PENDING',
        # Measurement fields for blouse
        'chest_bust_circumference': 36.0,
        'waist_circumference': 32.0,
        'shoulder_width': 16.0,
        'sleeve_length': 'LONG',
        'blouse_length_shoulder_to_hem': 24.0
    }
    
    order_serializer = OrderSerializer(data=order_data)
    if order_serializer.is_valid():
        order = order_serializer.save()
        print(f"✓ Created order: Order #{order.id} for {order.customer.get_full_name()}")
        print(f"  - Category: {order.get_category_display()}")
        print(f"  - Garment: {order.get_garment_type_display()}")
        print(f"  - Quantity: {order.quantity}")
        print(f"  - Total: ₱{order.total_amount}")
        print(f"  - Status: {order.status}")
    else:
        print(f"✗ Order creation failed: {order_serializer.errors}")
        return False
    
    # Step 5: Verify the relationships
    assert order.customer == customer, "Order customer relationship failed"
    assert order.fabric == fabric, "Order fabric relationship failed"
    assert accessory in order.accessories.all(), "Order accessories relationship failed"
    
    print("✓ All relationships verified successfully")
    
    # Step 6: Test order measurements
    measurements = order.get_measurements_for_garment_type()
    assert 'chest_bust_circumference' in measurements, "Measurements not saved correctly"
    print("✓ Order measurements saved correctly")
    
    # Step 7: Test customer measurements
    customer_measurements = customer.get_measurements()
    assert 'chest' in customer_measurements, "Customer measurements not saved correctly"
    print("✓ Customer measurements saved correctly")
    
    print("\n🎉 New customer order workflow test passed!")
    return True


def cleanup_test_data():
    """Clean up test data."""
    print("\nCleaning up test data...")
    
    # Delete in proper order to avoid foreign key constraints
    Order.objects.filter(customer__user__username='newcustomer_test').delete()
    Customer.objects.filter(user__username='newcustomer_test').delete()
    User.objects.filter(username='newcustomer_test').delete()
    Fabric.objects.filter(name='Test Cotton Fabric').delete()
    Accessory.objects.filter(name='Test Button').delete()
    
    print("✓ Cleanup completed")


if __name__ == '__main__':
    try:
        success = test_new_customer_order_workflow()
        if success:
            print("\n✅ All tests passed! The new customer order functionality is working correctly.")
        else:
            print("\n❌ Tests failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        cleanup_test_data()
