from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from .models import (
    UserExtension, Customer, Tailor, Fabric, Accessory, 
    Order, Task, Commission
)
from .business_logic import OrderManager, CommissionManager, InventoryManager
from django.core.exceptions import ValidationError


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_user_extension_creation(self):
        user_ext = UserExtension.objects.create(
            user=self.user,
            role='CUSTOMER',
            phone_number='1234567890'
        )
        self.assertEqual(user_ext.user, self.user)
        self.assertEqual(user_ext.role, 'CUSTOMER')
        self.assertEqual(user_ext.phone_number, '1234567890')


class CustomerModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testcustomer',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone_number='1234567890',
            address='123 Test St, Test City',
            measurements={'chest': 42, 'waist': 36}
        )
    
    def test_customer_creation(self):
        self.assertEqual(self.customer.user, self.user)
        self.assertEqual(self.customer.phone_number, '1234567890')
        self.assertEqual(self.customer.address, '123 Test St, Test City')
        self.assertEqual(self.customer.measurements['chest'], 42)


class TailorModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testtailor',
            password='testpass123'
        )
        self.tailor = Tailor.objects.create(
            user=self.user,
            phone_number='1234567890',
            specialty='Suits',
            commission_rate=Decimal('10.00')
        )
    
    def test_tailor_creation(self):
        self.assertEqual(self.tailor.user, self.user)
        self.assertEqual(self.tailor.phone_number, '1234567890')
        self.assertEqual(self.tailor.specialty, 'Suits')
        self.assertEqual(self.tailor.commission_rate, Decimal('10.00'))


class FabricModelTest(TestCase):
    def setUp(self):
        self.fabric = Fabric.objects.create(
            name='Cotton',
            description='High quality cotton fabric',
            unit_type='METERS',
            quantity=Decimal('100.00'),
            price_per_unit=Decimal('15.00'),
            low_stock_threshold=Decimal('10.00')
        )
    
    def test_fabric_creation(self):
        self.assertEqual(self.fabric.name, 'Cotton')
        self.assertEqual(self.fabric.unit_type, 'METERS')
        self.assertEqual(self.fabric.quantity, Decimal('100.00'))
        self.assertEqual(self.fabric.price_per_unit, Decimal('15.00'))
        self.assertFalse(self.fabric.is_low_stock)
    
    def test_low_stock_detection(self):
        self.fabric.quantity = Decimal('5.00')
        self.fabric.save()
        self.assertTrue(self.fabric.is_low_stock)


class AccessoryModelTest(TestCase):
    def setUp(self):
        self.accessory = Accessory.objects.create(
            name='Buttons',
            description='Plastic buttons',
            quantity=100,
            price_per_unit=Decimal('0.50'),
            low_stock_threshold=20
        )
    
    def test_accessory_creation(self):
        self.assertEqual(self.accessory.name, 'Buttons')
        self.assertEqual(self.accessory.quantity, 100)
        self.assertEqual(self.accessory.price_per_unit, Decimal('0.50'))
        self.assertFalse(self.accessory.is_low_stock)
    
    def test_low_stock_detection(self):
        self.accessory.quantity = 10
        self.accessory.save()
        self.assertTrue(self.accessory.is_low_stock)


class OrderModelTest(TestCase):
    def setUp(self):
        # Create customer
        customer_user = User.objects.create_user(
            username='testcustomer',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=customer_user,
            phone_number='1234567890',
            address='123 Test St, Test City'
        )
        
        # Create fabric
        self.fabric = Fabric.objects.create(
            name='Cotton',
            unit_type='METERS',
            quantity=Decimal('100.00'),
            price_per_unit=Decimal('15.00'),
            low_stock_threshold=Decimal('10.00')
        )
        
        # Create order
        self.order = Order.objects.create(
            customer=self.customer,
            fabric=self.fabric,
            total_amount=Decimal('150.00')
        )
    
    def test_order_creation(self):
        self.assertEqual(self.order.customer, self.customer)
        self.assertEqual(self.order.fabric, self.fabric)
        self.assertEqual(self.order.total_amount, Decimal('150.00'))
        self.assertEqual(self.order.status, 'PENDING')


class TaskModelTest(TestCase):
    def setUp(self):
        # Create customer
        customer_user = User.objects.create_user(
            username='testcustomer',
            password='testpass123'
        )
        customer = Customer.objects.create(
            user=customer_user,
            phone_number='1234567890',
            address='123 Test St, Test City'
        )
        
        # Create tailor
        tailor_user = User.objects.create_user(
            username='testtailor',
            password='testpass123'
        )
        self.tailor = Tailor.objects.create(
            user=tailor_user,
            phone_number='1234567890',
            specialty='Suits',
            commission_rate=Decimal('10.00')
        )
        
        # Create fabric
        fabric = Fabric.objects.create(
            name='Cotton',
            unit_type='METERS',
            quantity=Decimal('100.00'),
            price_per_unit=Decimal('15.00'),
            low_stock_threshold=Decimal('10.00')
        )
        
        # Create order
        self.order = Order.objects.create(
            customer=customer,
            fabric=fabric,
            total_amount=Decimal('150.00')
        )
        
        # Create task
        self.task = Task.objects.create(
            order=self.order,
            tailor=self.tailor
        )
    
    def test_task_creation(self):
        self.assertEqual(self.task.order, self.order)
        self.assertEqual(self.task.tailor, self.tailor)
        self.assertEqual(self.task.status, 'ASSIGNED')


class CommissionModelTest(TestCase):
    def setUp(self):
        # Create customer
        customer_user = User.objects.create_user(
            username='testcustomer',
            password='testpass123'
        )
        customer = Customer.objects.create(
            user=customer_user,
            phone_number='1234567890',
            address='123 Test St, Test City'
        )
        
        # Create tailor
        tailor_user = User.objects.create_user(
            username='testtailor',
            password='testpass123'
        )
        self.tailor = Tailor.objects.create(
            user=tailor_user,
            phone_number='1234567890',
            specialty='Suits',
            commission_rate=Decimal('10.00')
        )
        
        # Create fabric
        fabric = Fabric.objects.create(
            name='Cotton',
            unit_type='METERS',
            quantity=Decimal('100.00'),
            price_per_unit=Decimal('15.00'),
            low_stock_threshold=Decimal('10.00')
        )
        
        # Create order
        self.order = Order.objects.create(
            customer=customer,
            fabric=fabric,
            total_amount=Decimal('150.00')
        )
        
        # Create commission
        self.commission = Commission.objects.create(
            tailor=self.tailor,
            amount=Decimal('15.00'),
            order=self.order
        )
    
    def test_commission_creation(self):
        self.assertEqual(self.commission.tailor, self.tailor)
        self.assertEqual(self.commission.amount, Decimal('15.00'))
        self.assertEqual(self.commission.order, self.order)
        self.assertEqual(self.commission.status, 'PENDING')


class InventoryManagerTest(TestCase):
    def setUp(self):
        # Create customer
        customer_user = User.objects.create_user(
            username='testcustomer',
            password='testpass123'
        )
        customer = Customer.objects.create(
            user=customer_user,
            phone_number='1234567890',
            address='123 Test St, Test City'
        )
        
        # Create fabric
        self.fabric = Fabric.objects.create(
            name='Cotton',
            unit_type='METERS',
            quantity=Decimal('100.00'),
            price_per_unit=Decimal('15.00'),
            low_stock_threshold=Decimal('10.00')
        )
        
        # Create accessory
        self.accessory = Accessory.objects.create(
            name='Buttons',
            quantity=100,
            price_per_unit=Decimal('0.50'),
            low_stock_threshold=20
        )
        
        # Create order
        self.order = Order.objects.create(
            customer=customer,
            fabric=self.fabric,
            total_amount=Decimal('150.00')
        )
        self.order.accessories.add(self.accessory)
    
    def test_check_inventory_sufficient(self):
        has_inventory, message = InventoryManager.check_inventory(self.order)
        self.assertTrue(has_inventory)
        self.assertEqual(message, "Sufficient inventory")
    
    def test_check_inventory_insufficient_fabric(self):
        self.fabric.quantity = Decimal('0.00')
        self.fabric.save()
        has_inventory, message = InventoryManager.check_inventory(self.order)
        self.assertFalse(has_inventory)
        self.assertIn("Insufficient fabric", message)
    
    def test_check_inventory_insufficient_accessory(self):
        self.accessory.quantity = 0
        self.accessory.save()
        has_inventory, message = InventoryManager.check_inventory(self.order)
        self.assertFalse(has_inventory)
        self.assertIn("Insufficient accessory", message)
    
    def test_deduct_inventory(self):
        initial_fabric_qty = self.fabric.quantity
        initial_accessory_qty = self.accessory.quantity
        
        InventoryManager.deduct_inventory(self.order)
        
        self.fabric.refresh_from_db()
        self.accessory.refresh_from_db()
        
        self.assertEqual(self.fabric.quantity, initial_fabric_qty - 1)
        self.assertEqual(self.accessory.quantity, initial_accessory_qty - 1)


class CommissionManagerTest(TestCase):
    def setUp(self):
        # Create customer
        customer_user = User.objects.create_user(
            username='testcustomer',
            password='testpass123'
        )
        customer = Customer.objects.create(
            user=customer_user,
            phone_number='1234567890',
            address='123 Test St, Test City'
        )
        
        # Create tailor
        self.tailor = Tailor.objects.create(
            user=customer_user,
            phone_number='1234567890',
            specialty='Suits',
            commission_rate=Decimal('10.00')
        )
        
        # Create fabric
        fabric = Fabric.objects.create(
            name='Cotton',
            unit_type='METERS',
            quantity=Decimal('100.00'),
            price_per_unit=Decimal('15.00'),
            low_stock_threshold=Decimal('10.00')
        )
        
        # Create order
        self.order = Order.objects.create(
            customer=customer,
            fabric=fabric,
            total_amount=Decimal('150.00')
        )
        
        # Create task
        self.task = Task.objects.create(
            order=self.order,
            tailor=self.tailor
        )
    
    def test_calculate_commission(self):
        commission_amount = CommissionManager.calculate_commission(self.task)
        expected_amount = (self.tailor.commission_rate / 100) * self.order.total_amount
        self.assertEqual(commission_amount, expected_amount)
    
    def test_create_commission(self):
        commission = CommissionManager.create_commission(self.task)
        expected_amount = (self.tailor.commission_rate / 100) * self.order.total_amount
        self.assertEqual(commission.tailor, self.tailor)
        self.assertEqual(commission.amount, expected_amount)
        self.assertEqual(commission.order, self.order)
        self.assertEqual(commission.status, 'PENDING')


class OrderManagerTest(TestCase):
    def setUp(self):
        # Create customer
        customer_user = User.objects.create_user(
            username='testcustomer',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=customer_user,
            phone_number='1234567890',
            address='123 Test St, Test City'
        )
        
        # Create tailor
        tailor_user = User.objects.create_user(
            username='testtailor',
            password='testpass123'
        )
        self.tailor = Tailor.objects.create(
            user=tailor_user,
            phone_number='1234567890',
            specialty='Suits',
            commission_rate=Decimal('10.00')
        )
        
        # Create fabric
        self.fabric = Fabric.objects.create(
            name='Cotton',
            unit_type='METERS',
            quantity=Decimal('100.00'),
            price_per_unit=Decimal('15.00'),
            low_stock_threshold=Decimal('10.00')
        )
        
        # Create accessory
        self.accessory = Accessory.objects.create(
            name='Buttons',
            quantity=100,
            price_per_unit=Decimal('0.50'),
            low_stock_threshold=20
        )
        
        # Create order
        self.order = Order.objects.create(
            customer=self.customer,
            fabric=self.fabric,
            total_amount=Decimal('150.00')
        )
        self.order.accessories.add(self.accessory)
    
    def test_assign_order_to_tailor(self):
        initial_fabric_qty = self.fabric.quantity
        initial_accessory_qty = self.accessory.quantity
        
        task = OrderManager.assign_order_to_tailor(self.order, self.tailor)
        
        # Refresh from database
        self.order.refresh_from_db()
        self.fabric.refresh_from_db()
        self.accessory.refresh_from_db()
        
        # Check task creation
        self.assertEqual(task.order, self.order)
        self.assertEqual(task.tailor, self.tailor)
        self.assertEqual(task.status, 'ASSIGNED')
        
        # Check order status update
        self.assertEqual(self.order.status, 'ASSIGNED')
        
        # Check inventory deduction
        self.assertEqual(self.fabric.quantity, initial_fabric_qty - 1)
        self.assertEqual(self.accessory.quantity, initial_accessory_qty - 1)
    
    def test_assign_order_to_tailor_insufficient_inventory(self):
        # Make fabric quantity insufficient
        self.fabric.quantity = Decimal('0.00')
        self.fabric.save()
        
        with self.assertRaises(ValidationError):
            OrderManager.assign_order_to_tailor(self.order, self.tailor)
    
    def test_complete_task(self):
        # First assign order to tailor
        task = OrderManager.assign_order_to_tailor(self.order, self.tailor)
        
        # Then complete the task
        commission = OrderManager.complete_task(task)
        
        # Refresh from database
        task.refresh_from_db()
        self.order.refresh_from_db()
        
        # Check task status
        self.assertEqual(task.status, 'COMPLETED')
        
        # Check order status
        self.assertEqual(self.order.status, 'COMPLETED')
        
        # Check commission creation
        expected_amount = (self.tailor.commission_rate / 100) * self.order.total_amount
        self.assertEqual(commission.tailor, self.tailor)
        self.assertEqual(commission.amount, expected_amount)
        self.assertEqual(commission.order, self.order)
        self.assertEqual(commission.status, 'PENDING')