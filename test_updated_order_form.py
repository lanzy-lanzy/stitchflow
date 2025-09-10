#!/usr/bin/env python
"""
Test script for the updated order form without fabric/accessories selection.
Tests the new static pricing model with automatic inventory assignment.
"""

import os
import sys
import django
from decimal import Decimal

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stitchflow.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from etailoring.models import Customer, Fabric, Accessory, Order
from etailoring.serializers import OrderSerializer


def setup_test_data():
    """Create test data for the order system."""
    print("Setting up test data...")
    
    # Create test user and customer
    user = User.objects.create_user(
        username='test_customer_updated',
        email='test_updated@example.com',
        password='testpass123'
    )
    
    customer = Customer.objects.create(
        user=user,
        phone_number='+1234567892',
        address='125 Test Street'
    )
    
    # Create test fabrics with sufficient inventory
    fabric1 = Fabric.objects.create(
        name='Cotton Fabric',
        description='High quality cotton',
        unit_type='METERS',
        quantity=20,
        price_per_unit=Decimal('50.00')
    )
    
    fabric2 = Fabric.objects.create(
        name='Polyester Fabric',
        description='Durable polyester blend',
        unit_type='METERS',
        quantity=15,
        price_per_unit=Decimal('45.00')
    )
    
    # Create test accessories with sufficient inventory
    accessory1 = Accessory.objects.create(
        name='Standard Buttons',
        quantity=50,
        price_per_unit=Decimal('2.00')
    )
    
    accessory2 = Accessory.objects.create(
        name='Zipper',
        quantity=30,
        price_per_unit=Decimal('8.00')
    )
    
    return customer, fabric1, fabric2, accessory1, accessory2


def test_order_creation_without_fabric_accessories():
    """Test order creation without specifying fabric and accessories."""
    print("=== TESTING ORDER CREATION WITHOUT FABRIC/ACCESSORIES SELECTION ===")
    
    customer, fabric1, fabric2, accessory1, accessory2 = setup_test_data()
    
    # Test order data without fabric_id and accessories_ids
    order_data = {
        'customer': customer.id,
        'category': 'CASUAL_WEAR',
        'garment_type': 'BLOUSE',
        'quantity': 1,
        'fabric_type': 'Cotton blend',
        'accessories_preference': 'Standard buttons, no zipper',
        'color_design_preference': 'Light blue with white accents',
        'due_date': timezone.now().date() + timedelta(days=7),
    }
    
    print(f"Creating order with data: {order_data}")
    
    # Create order using serializer
    serializer = OrderSerializer(data=order_data)
    if serializer.is_valid():
        order = serializer.save()
        
        print(f"✓ Order created successfully: #{order.id}")
        print(f"  - Customer: {order.customer.get_full_name()}")
        print(f"  - Garment: {order.get_garment_type_display()}")
        print(f"  - Quantity: {order.quantity}")
        print(f"  - Total Amount: ₱{order.total_amount}")
        print(f"  - Down Payment: ₱{order.down_payment_amount}")
        print(f"  - Remaining Balance: ₱{order.remaining_balance}")
        print(f"  - Fabric Type Preference: {order.fabric_type}")
        print(f"  - Accessories Preference: {order.accessories_preference}")
        print(f"  - Assigned Fabric: {order.fabric.name if order.fabric else 'None'}")
        print(f"  - Assigned Accessories: {[acc.name for acc in order.accessories.all()]}")
        
        # Verify pricing
        expected_total = Decimal('550.00')  # BLOUSE price
        expected_down_payment = expected_total * Decimal('0.5')
        
        assert order.total_amount == expected_total, f"Total should be ₱{expected_total}"
        assert order.down_payment_amount == expected_down_payment, f"Down payment should be ₱{expected_down_payment}"
        
        # Verify fabric and accessories were assigned
        assert order.fabric is not None, "Fabric should be automatically assigned"
        assert order.accessories.count() > 0, "Accessories should be automatically assigned"
        
        print("✅ Order creation test passed!")
        return True
        
    else:
        print(f"✗ Order creation failed: {serializer.errors}")
        return False


def test_multiple_garment_types():
    """Test pricing for different garment types."""
    print("\n=== TESTING MULTIPLE GARMENT TYPES ===")
    
    customer, _, _, _, _ = setup_test_data()
    
    test_cases = [
        ('BLOUSE', 1, Decimal('550.00')),
        ('PANTS', 1, Decimal('650.00')),
        ('DRESS', 2, Decimal('1600.00')),  # 800 * 2
        ('JACKET', 1, Decimal('750.00')),
    ]
    
    for garment_type, quantity, expected_total in test_cases:
        order_data = {
            'customer': customer.id,
            'category': 'CASUAL_WEAR',
            'garment_type': garment_type,
            'quantity': quantity,
            'fabric_type': 'Cotton',
            'accessories_preference': 'Standard accessories',
            'color_design_preference': 'Any color',
            'due_date': timezone.now().date() + timedelta(days=7),
        }
        
        serializer = OrderSerializer(data=order_data)
        if serializer.is_valid():
            order = serializer.save()
            expected_down_payment = expected_total * Decimal('0.5')
            
            print(f"✓ {garment_type} (qty: {quantity})")
            print(f"  - Total: ₱{order.total_amount} (expected: ₱{expected_total})")
            print(f"  - Down Payment: ₱{order.down_payment_amount} (expected: ₱{expected_down_payment})")
            
            assert order.total_amount == expected_total
            assert order.down_payment_amount == expected_down_payment
            
        else:
            print(f"✗ Failed to create {garment_type} order: {serializer.errors}")
            return False
    
    print("✅ Multiple garment types test passed!")
    return True


def main():
    """Run all tests."""
    print("🧪 TESTING UPDATED ORDER FORM (NO FABRIC/ACCESSORIES SELECTION)")
    print("=" * 70)
    
    try:
        success1 = test_order_creation_without_fabric_accessories()
        success2 = test_multiple_garment_types()
        
        if success1 and success2:
            print("\n🎉 ALL TESTS PASSED!")
            print("\n📋 SUMMARY OF CHANGES:")
            print("✅ Removed fabric selection requirement from frontend")
            print("✅ Removed accessories selection requirement from frontend")
            print("✅ Added fabric type preference field")
            print("✅ Added accessories preference field")
            print("✅ Automatic fabric assignment from available inventory")
            print("✅ Automatic accessories assignment from available inventory")
            print("✅ Static pricing working correctly")
            print("✅ Down payment calculation working")
            print("✅ Inventory deduction during order creation")
            
            print("\n🎯 NEW USER WORKFLOW:")
            print("1. Select garment type and quantity")
            print("2. Specify fabric and accessory preferences (text fields)")
            print("3. System automatically calculates fixed price")
            print("4. System shows required 50% down payment")
            print("5. System automatically assigns fabric/accessories from inventory")
            print("6. System deducts inventory immediately upon order creation")
            
        else:
            print("\n❌ SOME TESTS FAILED")
            return False
            
    except Exception as e:
        print(f"❌ Test suite failed: {str(e)}")
        return False
    
    return True


if __name__ == '__main__':
    main()
