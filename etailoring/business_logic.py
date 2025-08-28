from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Commission, Task, Order


class OrderManager:
    @staticmethod
    def assign_order_to_tailor(order, tailor):
        """
        Assign an order to a tailor, deduct inventory, and create a task.
        """
        from .business_logic import InventoryManager, CommissionManager
        
        # Check inventory first
        has_inventory, message = InventoryManager.check_inventory(order)
        if not has_inventory:
            raise ValidationError(message)
        
        # Deduct inventory
        InventoryManager.deduct_inventory(order)
        
        # Update order status
        order.status = 'ASSIGNED'
        order.save()
        
        # Create task
        task = Task.objects.create(
            order=order,
            tailor=tailor
        )
        
        # Create commission
        CommissionManager.create_commission(task)
        
        return task
    
    @staticmethod
    def start_task(task):
        """
        Start a task and update related objects.
        """
        from django.utils import timezone
        
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
        """
        from .business_logic import CommissionManager
        from django.utils import timezone
        
        # Update task
        task.status = 'COMPLETED'
        task.completed_at = timezone.now()
        task.save()
        
        # Update order
        task.order.status = 'COMPLETED'
        task.order.save()
        
        # Get or create commission
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
        return (tailor.commission_rate / 100) * order.total_amount
    
    @staticmethod
    def create_commission(task):
        """
        Create a commission record for a task.
        """
        amount = CommissionManager.calculate_commission(task)
        commission = Commission.objects.create(
            tailor=task.tailor,
            amount=amount,
            order=task.order
        )
        return commission


class InventoryManager:
    @staticmethod
    def check_inventory(order):
        """
        Check if there's sufficient inventory for an order.
        Returns (has_inventory: bool, message: str)
        """
        # Check fabric
        if order.fabric.quantity < 1:  # Assuming 1 unit per order
            return False, f"Insufficient fabric: {order.fabric.name}"
        
        # Check accessories
        for accessory in order.accessories.all():
            if accessory.quantity < 1:  # Assuming 1 unit per accessory per order
                return False, f"Insufficient accessory: {accessory.name}"
        
        return True, "Sufficient inventory"
    
    @staticmethod
    def deduct_inventory(order):
        """
        Deduct inventory for an order.
        """
        # Deduct fabric (assuming 1 meter/yard per order)
        order.fabric.quantity -= 1
        order.fabric.save()
        
        # Deduct accessories (assuming 1 unit per accessory per order)
        for accessory in order.accessories.all():
            accessory.quantity -= 1
            accessory.save()