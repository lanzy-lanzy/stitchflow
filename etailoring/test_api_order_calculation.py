import os
import sys
import django
import uuid
import json
from decimal import Decimal

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stitchflow.settings')
django.setup()

from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from etailoring.models import Customer, Fabric, Accessory

def test_api_order_calculation():
    # Generate a unique username
    unique_username = f'testadmin_{uuid.uuid4().hex[:8]}'
    
    # Create a test admin user
    admin_user = User.objects.create_user(
        username=unique_username,
        email='admin@example.com',
        password='testpass123'
    )
    admin_user.is_staff = True
    admin_user.save()
    
    # Create a token for the admin user
    token = Token.objects.create(user=admin_user)
    
    # Create a test customer
    customer_user = User.objects.create_user(
        username=f'customer_{uuid.uuid4().hex[:8]}',
        email='customer@example.com',
        password='testpass123'
    )
    
    customer = Customer.objects.create(
        user=customer_user,
        phone_number='1234567890',
        address='123 Test St'
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
    
    # Create an API client
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    
    # Test creating an order without specifying total_amount
    order_data = {
        'customer': customer.id,
        'fabric': fabric.id,
        'accessories': [thread.id, button.id],
        'status': 'PENDING'
    }
    
    response = client.post('/api/admin/orders/', order_data, format='json')
    
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.content}")
    
    if response.status_code == 201:
        try:
            order = response.json()
            expected_total = float(fabric.price_per_unit + thread.price_per_unit + button.price_per_unit)
            actual_total = float(order['total_amount'])
            
            print(f"Fabric price: ${fabric.price_per_unit}")
            print(f"Thread price: ${thread.price_per_unit}")
            print(f"Button price: ${button.price_per_unit}")
            print(f"Expected total: ${expected_total}")
            print(f"Actual total: ${actual_total}")
            
            if expected_total == actual_total:
                print("API test passed! Order total amount calculation is working correctly through the API.")
            else:
                print(f"API test failed! Expected {expected_total}, got {actual_total}")
        except Exception as e:
            print(f"Error parsing response: {e}")
    else:
        print(f"API test failed! Status code: {response.status_code}")
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response content: {response.content}")
    
    # Clean up
    customer.delete()
    customer_user.delete()
    fabric.delete()
    thread.delete()
    button.delete()
    token.delete()
    admin_user.delete()

if __name__ == '__main__':
    test_api_order_calculation()