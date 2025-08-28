from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserExtension, Customer, Tailor, Fabric, 
    Accessory, Order, Task, Commission
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class UserExtensionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserExtension
        fields = ['id', 'user', 'role', 'phone_number']
        read_only_fields = ['id']


class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = Customer
        fields = ['id', 'user', 'phone_number', 'address', 'measurements']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        customer = Customer.objects.create(user=user, **validated_data)
        return customer


class TailorSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = Tailor
        fields = ['id', 'user', 'phone_number', 'specialty', 'commission_rate']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        tailor = Tailor.objects.create(user=user, **validated_data)
        return tailor


class FabricSerializer(serializers.ModelSerializer):
    is_low_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = Fabric
        fields = [
            'id', 'name', 'description', 'unit_type', 
            'quantity', 'price_per_unit', 'low_stock_threshold', 'is_low_stock'
        ]
        read_only_fields = ['id', 'is_low_stock']


class AccessorySerializer(serializers.ModelSerializer):
    is_low_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = Accessory
        fields = [
            'id', 'name', 'description', 
            'quantity', 'price_per_unit', 'low_stock_threshold', 'is_low_stock'
        ]
        read_only_fields = ['id', 'is_low_stock']


class OrderSerializer(serializers.ModelSerializer):
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    customer = CustomerSerializer(read_only=True)
    fabric = FabricSerializer(read_only=True)
    accessories = AccessorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'fabric', 'accessories',
            'total_amount', 'status', 'payment_status', 'paid_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'paid_at']
    
    def create(self, validated_data):
        # Extract accessories data before creating the order
        accessories_data = validated_data.pop('accessories', [])
        
        # Get customer and fabric IDs
        customer_id = validated_data.pop('customer') if 'customer' in validated_data else None
        fabric_id = validated_data.pop('fabric') if 'fabric' in validated_data else None
        
        # Retrieve the actual customer and fabric objects
        if customer_id is not None:
            validated_data['customer'] = Customer.objects.get(id=customer_id)
            
        if fabric_id is not None:
            validated_data['fabric'] = Fabric.objects.get(id=fabric_id)
            
        # Calculate total_amount if not provided
        if 'total_amount' not in validated_data or not validated_data['total_amount']:
            # We need to calculate the total based on fabric and accessories
            fabric = validated_data.get('fabric')
            total = fabric.price_per_unit if fabric else 0
            
            # For accessories, we need to fetch them from the database
            for accessory_id in accessories_data:
                accessory = Accessory.objects.get(id=accessory_id.id if hasattr(accessory_id, 'id') else accessory_id)
                total += accessory.price_per_unit
                
            validated_data['total_amount'] = total
        
        # Create the order instance
        order = Order.objects.create(**validated_data)
        
        # Add accessories to the order
        if accessories_data:
            order.accessories.set(accessories_data)
            
        return order
    
    def update(self, instance, validated_data):
        # Extract accessories data if provided
        accessories_data = validated_data.pop('accessories', None)
        
        # Handle customer and fabric if provided as IDs
        if 'customer' in validated_data:
            customer_id = validated_data.pop('customer')
            validated_data['customer'] = Customer.objects.get(id=customer_id)
            
        if 'fabric' in validated_data:
            fabric_id = validated_data.pop('fabric')
            validated_data['fabric'] = Fabric.objects.get(id=fabric_id)
        
        # Update the order instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Update accessories if provided
        if accessories_data is not None:
            instance.accessories.set(accessories_data)
        
        # If total_amount wasn't provided or was set to 0, calculate it
        if 'total_amount' not in validated_data or not instance.total_amount:
            instance.total_amount = instance.calculate_total_amount()
            
        instance.save()
        return instance


class TaskSerializer(serializers.ModelSerializer):
    order_details = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    commission_amount = serializers.SerializerMethodField()
    customer_phone = serializers.SerializerMethodField()
    customer_address = serializers.SerializerMethodField()
    order_measurements = serializers.SerializerMethodField()
    tailor = TailorSerializer(read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'order', 'tailor', 'status', 
            'assigned_at', 'completed_at', 'order_details', 
            'customer_name', 'commission_amount', 'customer_phone',
            'customer_address', 'order_measurements'
        ]
        read_only_fields = ['id', 'assigned_at']
    
    def get_order_details(self, obj):
        try:
            return {
                'id': obj.order.id,
                'fabric': obj.order.fabric.name if obj.order.fabric else 'N/A',
                'fabric_unit_type': obj.order.fabric.unit_type if obj.order.fabric else 'N/A',
                'total_amount': str(obj.order.total_amount) if obj.order.total_amount else '0.00',
                'status': obj.order.status,
                'created_at': obj.order.created_at,
                'accessories': [
                    {'id': accessory.id, 'name': accessory.name} 
                    for accessory in obj.order.accessories.all()
                ] if hasattr(obj.order, 'accessories') else []
            }
        except AttributeError:
            return {
                'id': obj.order.id if obj.order else None,
                'fabric': 'N/A',
                'fabric_unit_type': 'N/A',
                'total_amount': '0.00',
                'status': 'UNKNOWN',
                'created_at': None,
                'accessories': []
            }
    
    def get_customer_name(self, obj):
        try:
            if obj.order and obj.order.customer and obj.order.customer.user:
                return f"{obj.order.customer.user.first_name} {obj.order.customer.user.last_name}"
            return "Unknown Customer"
        except AttributeError:
            return "Unknown Customer"
    
    def get_commission_amount(self, obj):
        try:
            if obj.order and obj.tailor:
                commission = Commission.objects.get(order=obj.order, tailor=obj.tailor)
                return str(commission.amount)
            return "0.00"
        except (Commission.DoesNotExist, AttributeError):
            return "0.00"
    
    def get_customer_phone(self, obj):
        try:
            if obj.order and obj.order.customer:
                return obj.order.customer.phone_number
            return "N/A"
        except AttributeError:
            return "N/A"
    
    def get_customer_address(self, obj):
        try:
            if obj.order and obj.order.customer:
                return obj.order.customer.address
            return "N/A"
        except AttributeError:
            return "N/A"
    
    def get_order_measurements(self, obj):
        try:
            if obj.order and obj.order.customer:
                return obj.order.customer.measurements or {}
            return {}
        except AttributeError:
            return {}


class CommissionSerializer(serializers.ModelSerializer):
    tailor = TailorSerializer(read_only=True)
    
    class Meta:
        model = Commission
        fields = [
            'id', 'tailor', 'amount', 'order', 
            'status', 'created_at', 'paid_at'
        ]
        read_only_fields = ['id', 'created_at']