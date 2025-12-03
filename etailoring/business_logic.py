from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Commission, Task, Order


# Static pricing configuration for garment types
GARMENT_PRICES = {
    'BLOUSE': Decimal('550.00'),
    'PANTS': Decimal('650.00'),
    'SKIRT': Decimal('500.00'),
    'DRESS': Decimal('800.00'),
    'JACKET': Decimal('750.00'),
    'OTHERS': Decimal('600.00'),
}


class PricingManager:
    @staticmethod
    def get_garment_price(garment_type):
        """
        Get the fixed price for a garment type.
        """
        return GARMENT_PRICES.get(garment_type, GARMENT_PRICES['OTHERS'])

    @staticmethod
    def calculate_order_total(garment_type, quantity=1):
        """
        Calculate total order amount based on garment type and quantity.
        """
        base_price = PricingManager.get_garment_price(garment_type)
        return base_price * quantity

    @staticmethod
    def calculate_down_payment(total_amount):
        """
        Calculate 50% down payment of total amount.
        """
        return total_amount * Decimal('0.5')


class OrderManager:
    @staticmethod
    def create_order_with_pricing(order_data):
        """
        Create an order with static pricing and automatic inventory deduction.
        """
        # Calculate total amount using static pricing
        garment_type = order_data.get('garment_type', 'OTHERS')
        quantity = order_data.get('quantity', 1)
        total_amount = PricingManager.calculate_order_total(garment_type, quantity)

        # Update order data with calculated amounts
        order_data['total_amount'] = total_amount
        order_data['down_payment_amount'] = PricingManager.calculate_down_payment(total_amount)
        order_data['remaining_balance'] = total_amount - order_data['down_payment_amount']

        return order_data

    @staticmethod
    def process_order_creation(order):
        """
        Process order creation including inventory deduction.
        """
        # Check inventory first
        has_inventory, message = InventoryManager.check_inventory_for_garment(order)
        if not has_inventory:
            raise ValidationError(message)

        # Deduct inventory immediately upon order creation
        InventoryManager.deduct_inventory_for_garment(order)

        return order

    @staticmethod
    def assign_order_to_tailor(order, tailor):
        """
        Assign an order to a tailor and create a task.
        Note: Commission is NOT created here - only when admin approves the completed task.
        """
        # Update order status
        order.status = 'ASSIGNED'
        order.save()

        # Create task
        task = Task.objects.create(
            order=order,
            tailor=tailor
        )

        # Do NOT create commission here - only when task is approved
        return task
    
    @staticmethod
    def start_task(task):
        """
        Start a task and update related objects.
        """
        # Update task
        task.status = 'IN_PROGRESS'
        task.started_at = timezone.now()
        task.save()
        
        # Update order
        task.order.status = 'IN_PROGRESS'
        task.order.save()
        
        return task
    
    @staticmethod
    def complete_task(task):
        """
        Complete a task and update related objects.
        Note: Commission is NOT created here - only when admin approves the task.
        """
        # Update task
        task.status = 'COMPLETED'
        task.completed_at = timezone.now()
        task.save()

        # Update order
        task.order.status = 'COMPLETED'
        task.order.save()

        return task

    @staticmethod
    def approve_task(task):
        """
        Approve a completed task and create commission.
        Only admin can approve tasks.
        """
        if task.status != 'COMPLETED':
            raise ValueError("Task must be completed before it can be approved")

        # Update task
        task.status = 'APPROVED'
        task.approved_at = timezone.now()
        task.save()

        # Update order
        task.order.status = 'APPROVED'
        task.order.save()

        # Create commission only when approved
        try:
            commission = Commission.objects.get(order=task.order)
        except Commission.DoesNotExist:
            commission = CommissionManager.create_commission(task)

        return commission


class CommissionManager:
    @staticmethod
    def calculate_commission(task):
        """
        Calculate commission amount for a task.
        """
        order = task.order
        tailor = task.tailor
        # Prefer fixed tariff defined on the tailor. If no fixed tariff exists for
        # the garment_type, fall back to legacy percentage-based calculation.
        try:
            fixed = tailor.get_commission_amount(order.garment_type)
        except Exception:
            fixed = None

        if fixed is not None:
            return fixed

        # Legacy fallback: use percentage of order total
        return (tailor.commission_rate / 100) * order.total_amount
    
    @staticmethod
    def create_commission(task):
        """
        Create a commission record for a task.
        Commission is created with APPROVED status when task is approved by admin.
        """
        amount = CommissionManager.calculate_commission(task)
        commission = Commission.objects.create(
            tailor=task.tailor,
            amount=amount,
            order=task.order,
            status='APPROVED'  # Commission is approved when created (after task approval)
        )
        return commission


class InventoryManager:
    # Garment-based inventory requirements
    GARMENT_INVENTORY_REQUIREMENTS = {
        'BLOUSE': {'fabric_units': 2, 'accessories_units': 1},
        'PANTS': {'fabric_units': 3, 'accessories_units': 1},
        'SKIRT': {'fabric_units': 2, 'accessories_units': 1},
        'DRESS': {'fabric_units': 4, 'accessories_units': 2},
        'JACKET': {'fabric_units': 3, 'accessories_units': 2},
        'OTHERS': {'fabric_units': 2, 'accessories_units': 1},
    }

    @staticmethod
    def get_inventory_requirements(garment_type):
        """
        Get inventory requirements for a specific garment type.
        """
        return InventoryManager.GARMENT_INVENTORY_REQUIREMENTS.get(
            garment_type,
            InventoryManager.GARMENT_INVENTORY_REQUIREMENTS['OTHERS']
        )

    @staticmethod
    def check_inventory_for_garment(order):
        """
        Check if there's sufficient inventory for an order based on garment type.
        Returns (has_inventory: bool, message: str)
        """
        requirements = InventoryManager.get_inventory_requirements(order.garment_type)
        fabric_needed = requirements['fabric_units'] * order.quantity
        accessories_needed = requirements['accessories_units'] * order.quantity

        # Check fabric
        if order.fabric.quantity < fabric_needed:
            return False, f"Insufficient fabric: {order.fabric.name}. Need {fabric_needed} units, have {order.fabric.quantity}"

        # Check accessories
        for accessory in order.accessories.all():
            if accessory.quantity < accessories_needed:
                return False, f"Insufficient accessory: {accessory.name}. Need {accessories_needed} units, have {accessory.quantity}"

        return True, "Sufficient inventory"

    @staticmethod
    def deduct_inventory_for_garment(order):
        """
        Deduct inventory for an order based on garment type.
        """
        requirements = InventoryManager.get_inventory_requirements(order.garment_type)
        fabric_needed = requirements['fabric_units'] * order.quantity
        accessories_needed = requirements['accessories_units'] * order.quantity

        # Deduct fabric
        order.fabric.quantity -= fabric_needed
        order.fabric.save()

        # Deduct accessories
        for accessory in order.accessories.all():
            accessory.quantity -= accessories_needed
            accessory.save()

        # Return a summary report of what was deducted for audit purposes
        report = {
            'order_id': order.id,
            'fabric': {
                'id': order.fabric.id,
                'name': order.fabric.name,
                'deducted_units': float(fabric_needed),
                'remaining': float(order.fabric.quantity)
            },
            'accessories': [
                {
                    'id': accessory.id,
                    'name': accessory.name,
                    'deducted_units': int(accessories_needed),
                    'remaining': int(accessory.quantity)
                }
                for accessory in order.accessories.all()
            ]
        }

        return report

    @staticmethod
    def get_deduction_report(order):
        """
        Return a report (without mutating inventory) describing how much fabric
        and accessories would be deducted for the given order. Useful for
        audit and preview endpoints.
        """
        requirements = InventoryManager.get_inventory_requirements(order.garment_type)
        fabric_needed = requirements['fabric_units'] * order.quantity
        accessories_needed = requirements['accessories_units'] * order.quantity

        report = {
            'order_id': order.id,
            'fabric': {
                'id': order.fabric.id if order.fabric else None,
                'name': order.fabric.name if order.fabric else None,
                'required_units': float(fabric_needed),
                'available': float(order.fabric.quantity) if order.fabric else 0
            },
            'accessories': [
                {
                    'id': accessory.id,
                    'name': accessory.name,
                    'required_units': int(accessories_needed),
                    'available': int(accessory.quantity)
                }
                for accessory in order.accessories.all()
            ]
        }

        return report

    # Legacy methods for backward compatibility
    @staticmethod
    def check_inventory(order):
        """
        Legacy method - redirects to new garment-based checking.
        """
        return InventoryManager.check_inventory_for_garment(order)

    @staticmethod
    def deduct_inventory(order):
        """
        Legacy method - redirects to new garment-based deduction.
        """
        return InventoryManager.deduct_inventory_for_garment(order)