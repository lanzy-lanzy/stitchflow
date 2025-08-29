from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.db.models import F
from ...models import Fabric, Accessory, Order
from ...business_logic import InventoryManager

class Command(BaseCommand):
    help = 'Manage inventory operations'

    def add_arguments(self, parser):
        parser.add_argument(
            'operation',
            type=str,
            help='Operation to perform: check, restock, low-stock, deduct',
            choices=['check', 'restock', 'low-stock', 'deduct']
        )
        
        parser.add_argument(
            '--fabric-id',
            type=int,
            help='Fabric ID for specific operations'
        )
        
        parser.add_argument(
            '--accessory-id',
            type=int,
            help='Accessory ID for specific operations'
        )
        
        parser.add_argument(
            '--quantity',
            type=int,
            help='Quantity for restock operation'
        )
        
        parser.add_argument(
            '--order-id',
            type=int,
            help='Order ID for inventory deduction'
        )

    def handle(self, *args, **options):
        operation = options['operation']
        
        try:
            if operation == 'check':
                self.check_inventory()
            elif operation == 'restock':
                self.restock_inventory(options)
            elif operation == 'low-stock':
                self.show_low_stock()
            elif operation == 'deduct':
                self.deduct_inventory(options)
                
            self.stdout.write(
                self.style.SUCCESS(f'Successfully completed {operation} operation')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during {operation} operation: {str(e)}')
            )

    def check_inventory(self):
        """Check overall inventory status"""
        self.stdout.write('=== FABRIC INVENTORY ===')
        fabrics = Fabric.objects.all()
        for fabric in fabrics:
            status = "LOW STOCK" if fabric.is_low_stock else "OK"
            self.stdout.write(
                f"{fabric.name}: {fabric.quantity} {fabric.get_unit_type_display()} "
                f"(Price: ₱{fabric.price_per_unit}) [{status}]"
            )
        
        self.stdout.write('\n=== ACCESSORY INVENTORY ===')
        accessories = Accessory.objects.all()
        for accessory in accessories:
            status = "LOW STOCK" if accessory.is_low_stock else "OK"
            self.stdout.write(
                f"{accessory.name}: {accessory.quantity} units "
                f"(Price: ₱{accessory.price_per_unit}) [{status}]"
            )

    def restock_inventory(self, options):
        """Restock inventory items"""
        fabric_id = options.get('fabric_id')
        accessory_id = options.get('accessory_id')
        quantity = options.get('quantity')
        
        if not quantity:
            self.stdout.write(self.style.ERROR('Quantity is required for restock operation'))
            return
            
        if fabric_id:
            try:
                fabric = Fabric.objects.get(id=fabric_id)
                fabric.quantity += quantity
                fabric.save()
                self.stdout.write(
                    f"Restocked {fabric.name} with {quantity} units. "
                    f"New quantity: {fabric.quantity} {fabric.get_unit_type_display()}"
                )
            except Fabric.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Fabric with ID {fabric_id} not found'))
                return
                
        elif accessory_id:
            try:
                accessory = Accessory.objects.get(id=accessory_id)
                accessory.quantity += quantity
                accessory.save()
                self.stdout.write(
                    f"Restocked {accessory.name} with {quantity} units. "
                    f"New quantity: {accessory.quantity} units"
                )
            except Accessory.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Accessory with ID {accessory_id} not found'))
                return
        else:
            self.stdout.write(self.style.ERROR('Either --fabric-id or --accessory-id is required for restock operation'))

    def show_low_stock(self):
        """Show items with low stock"""
        self.stdout.write('=== LOW STOCK FABRICS ===')
        low_stock_fabrics = Fabric.objects.filter(quantity__lte=F('low_stock_threshold'))
        if low_stock_fabrics.exists():
            for fabric in low_stock_fabrics:
                self.stdout.write(
                    f"{fabric.name}: {fabric.quantity} {fabric.get_unit_type_display()} "
                    f"(Threshold: {fabric.low_stock_threshold})"
                )
        else:
            self.stdout.write('No fabrics with low stock')
            
        self.stdout.write('\n=== LOW STOCK ACCESSORIES ===')
        low_stock_accessories = Accessory.objects.filter(quantity__lte=F('low_stock_threshold'))
        if low_stock_accessories.exists():
            for accessory in low_stock_accessories:
                self.stdout.write(
                    f"{accessory.name}: {accessory.quantity} units "
                    f"(Threshold: {accessory.low_stock_threshold})"
                )
        else:
            self.stdout.write('No accessories with low stock')

    def deduct_inventory(self, options):
        """Deduct inventory for an order"""
        order_id = options.get('order_id')
        
        if not order_id:
            self.stdout.write(self.style.ERROR('--order-id is required for deduct operation'))
            return
            
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Order with ID {order_id} not found'))
            return
            
        try:
            # Check inventory first
            has_inventory, message = InventoryManager.check_inventory(order)
            if not has_inventory:
                self.stdout.write(self.style.ERROR(f'Insufficient inventory: {message}'))
                return
                
            # Deduct inventory
            InventoryManager.deduct_inventory(order)
            self.stdout.write(f'Successfully deducted inventory for order #{order.id}')
            
            # Show updated inventory
            self.stdout.write('\nUpdated inventory status:')
            fabric = order.fabric
            self.stdout.write(
                f"Fabric {fabric.name}: {fabric.quantity} {fabric.get_unit_type_display()} remaining"
            )
            
            for accessory in order.accessories.all():
                self.stdout.write(
                    f"Accessory {accessory.name}: {accessory.quantity} units remaining"
                )
        except ValidationError as e:
            self.stdout.write(self.style.ERROR(f'Validation error: {str(e)}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error deducting inventory: {str(e)}'))