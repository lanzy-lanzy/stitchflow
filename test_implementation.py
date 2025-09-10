#!/usr/bin/env python
"""
Test script to verify the order management system implementation.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stitchflow.settings')
django.setup()

from django.contrib.auth.models import User
from etailoring.models import Customer, Order, Fabric, Accessory, Tailor
from django.utils import timezone
from datetime import timedelta

def test_customer_creation():
    """Test customer creation with measurements."""
    print("Testing customer creation...")
    
    # Create a user
    user = User.objects.create_user(
        username='testcustomer',
        email='test@example.com',
        first_name='Test',
        last_name='Customer'
    )
    
    # Create a customer
    customer = Customer.objects.create(
        user=user,
        phone_number='+1234567890',
        address='123 Test Street'
    )
    
    # Set measurements
    measurements = {
        'chest': 36,
        'waist': 32,
        'hips': 38,
        'shoulder_width': 16
    }
    customer.set_measurements(measurements)
    customer.save()
    
    # Verify measurements
    retrieved_measurements = customer.get_measurements()
    assert retrieved_measurements == measurements, f"Expected {measurements}, got {retrieved_measurements}"
    
    print("✓ Customer creation test passed")
    return customer

def test_order_creation():
    """Test order creation with new fields."""
    print("Testing order creation...")
    
    # Get or create test customer
    try:
        customer = Customer.objects.get(user__username='testcustomer')
    except Customer.DoesNotExist:
        customer = test_customer_creation()
    
    # Create test fabric
    fabric = Fabric.objects.create(
        name='Test Fabric',
        description='A test fabric',
        unit_type='YARD',
        quantity=100,
        price_per_unit=25.00
    )
    
    # Create test accessory
    accessory = Accessory.objects.create(
        name='Test Button',
        description='A test button',
        quantity=50,
        price_per_unit=2.00
    )
    
    # Create order with new fields
    order = Order.objects.create(
        customer=customer,
        fabric=fabric,
        category='SCHOOL_UNIFORM',
        garment_type='BLOUSE',
        quantity=2,
        fabric_type='Cotton',
        color_design_preference='Blue with white collar',
        due_date=timezone.now().date() + timedelta(days=14),
        total_amount=100.00,
        status='PENDING',
        # Measurement fields
        chest_bust_circumference=36.0,
        waist_circumference=32.0,
        shoulder_width=16.0,
        sleeve_length='LONG',
        blouse_length_shoulder_to_hem=24.0
    )
    
    # Add accessories
    order.accessories.add(accessory)
    
    # Verify order fields
    assert order.category == 'SCHOOL_UNIFORM'
    assert order.garment_type == 'BLOUSE'
    assert order.quantity == 2
    assert order.get_category_display() == 'School Uniforms'
    assert order.get_garment_type_display() == 'Blouse'
    
    # Test measurement retrieval
    measurements = order.get_measurements_for_garment_type()
    assert 'chest_bust_circumference' in measurements
    assert measurements['chest_bust_circumference'] == 36.0
    
    print("✓ Order creation test passed")
    return order

def test_serializers():
    """Test serializers with new fields."""
    print("Testing serializers...")
    
    from etailoring.serializers import CustomerSerializer, OrderSerializer
    
    # Test customer serializer
    try:
        customer = Customer.objects.get(user__username='testcustomer')
    except Customer.DoesNotExist:
        customer = test_customer_creation()
    
    customer_serializer = CustomerSerializer(customer)
    customer_data = customer_serializer.data
    
    assert 'measurements' in customer_data
    assert isinstance(customer_data['measurements'], dict)
    
    # Test order serializer
    try:
        order = Order.objects.first()
        if not order:
            order = test_order_creation()
    except:
        order = test_order_creation()
    
    order_serializer = OrderSerializer(order)
    order_data = order_serializer.data
    
    assert 'category_display' in order_data
    assert 'garment_type_display' in order_data
    assert 'quantity' in order_data
    
    print("✓ Serializer test passed")

def cleanup():
    """Clean up test data."""
    print("Cleaning up test data...")
    
    # Delete test objects
    Order.objects.filter(customer__user__username='testcustomer').delete()
    Customer.objects.filter(user__username='testcustomer').delete()
    User.objects.filter(username='testcustomer').delete()
    Fabric.objects.filter(name='Test Fabric').delete()
    Accessory.objects.filter(name='Test Button').delete()
    
    print("✓ Cleanup completed")

def main():
    """Run all tests."""
    print("Starting order management system tests...\n")
    
    try:
        test_customer_creation()
        test_order_creation()
        test_serializers()
        
        print("\n🎉 All tests passed! The order management system is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        cleanup()

if __name__ == '__main__':
    main()
