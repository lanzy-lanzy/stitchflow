#!/usr/bin/env python
"""
Test script to verify customer creation API endpoint works correctly.
"""
import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stitchflow.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from etailoring.models import Customer, UserExtension

# Clean up test users/customers if they exist
User.objects.filter(username__startswith='test_customer_').delete()

# Create a test client
client = Client()

# Test data
test_data = {
    "user": {
        "username": "test_customer_123456",
        "email": "test@example.com",
        "password": "testpass123",
        "first_name": "John",
        "last_name": "Doe"
    },
    "phone_number": "09171234567",
    "address": "123 Test Street, Test City",
    "measurements": {
        "neck_circumference": 14.5,
        "chest_bust_circumference": 38.0,
        "waist_circumference": 32.0
    }
}

print("Testing customer registration API endpoint...")
print(f"Sending data: {json.dumps(test_data, indent=2)}")

# Make the request
response = client.post(
    '/api/register/',
    data=json.dumps(test_data),
    content_type='application/json'
)

print(f"\nResponse Status: {response.status_code}")
print(f"Response Content: {response.content.decode()}")

if response.status_code == 201:
    response_data = response.json()
    print(f"\nSuccess! Customer created with ID: {response_data.get('id')}")
    
    # Verify the customer was actually created
    try:
        customer = Customer.objects.get(id=response_data.get('id'))
        print(f"Verified customer in database: {customer.user.username}")
        print(f"Customer name: {customer.get_full_name()}")
        print(f"Customer phone: {customer.phone_number}")
        print(f"Customer measurements: {customer.get_measurements()}")
        
        # Check UserExtension
        try:
            ext = UserExtension.objects.get(user=customer.user)
            print(f"UserExtension role: {ext.role}")
        except UserExtension.DoesNotExist:
            print("WARNING: UserExtension not created!")
    except Customer.DoesNotExist:
        print("ERROR: Customer not found in database despite successful response!")
else:
    print(f"\nError! Response indicates failure.")
    try:
        error_data = response.json()
        print(f"Error details: {json.dumps(error_data, indent=2)}")
    except:
        print("Could not parse error response as JSON")

# Clean up
User.objects.filter(username__startswith='test_customer_').delete()
print("\nTest complete and cleaned up.")
