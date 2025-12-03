from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from .models import Customer, Fabric, Order


class OrderDownPaymentAPITest(TestCase):
    def setUp(self):
        # Create admin user and authenticate
        self.admin_user = User.objects.create_user(username='admin_test', password='testpass')
        self.admin_user.is_staff = True
        self.admin_user.save()

        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)

        # Create a customer
        self.customer_user = User.objects.create_user(username='cust_test', password='testpass')
        self.customer = Customer.objects.create(user=self.customer_user, phone_number='09171234567', address='Test Addr')

        # Create a fabric so serializer can pick a default
        self.fabric = Fabric.objects.create(name='TestFabric', unit_type='METERS', quantity=Decimal('100.00'), price_per_unit=Decimal('10.00'))

    def test_create_order_down_payment_sets_pending_and_amount(self):
        payload = {
            'customer_id': self.customer.id,
            'payment_option': 'DOWN_PAYMENT'
        }

        response = self.client.post('/api/admin/orders/', payload, format='json')
        self.assertEqual(response.status_code, 201, msg=f"Unexpected response: {response.status_code} {response.content}")

        data = response.json()
        # Ensure payment_status is PENDING and down_payment_amount is present and > 0
        self.assertEqual(data.get('payment_status'), 'PENDING')
        self.assertIn('down_payment_amount', data)
        self.assertGreater(Decimal(data.get('down_payment_amount') or '0'), Decimal('0'))

        # Also verify order exists in DB with matching status
        order = Order.objects.get(id=data.get('id'))
        self.assertEqual(order.payment_status, 'PENDING')
        self.assertGreater(order.down_payment_amount, Decimal('0'))
