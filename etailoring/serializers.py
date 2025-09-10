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
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    measurements = serializers.JSONField(required=False, allow_null=True)

    class Meta:
        model = Customer
        fields = ['id', 'user', 'full_name', 'phone_number', 'address', 'measurements']
        read_only_fields = ['id', 'full_name']

    def to_representation(self, instance):
        """Convert the instance to a dictionary for serialization."""
        data = super().to_representation(instance)
        # Convert measurements from JSON string to dictionary for output
        data['measurements'] = instance.get_measurements()
        return data

    def create(self, validated_data):
        measurements_data = validated_data.pop('measurements', {})
        user_data = validated_data.pop('user')

        # Create user
        user = User.objects.create_user(**user_data)

        # Create customer
        customer = Customer.objects.create(user=user, **validated_data)

        # Set measurements if provided
        if measurements_data:
            customer.set_measurements(measurements_data)
            customer.save()

        return customer

    def update(self, instance, validated_data):
        measurements_data = validated_data.pop('measurements', None)
        user_data = validated_data.pop('user', None)

        # Update user fields if provided
        if user_data:
            user_serializer = UserSerializer(instance.user, data=user_data, partial=True)
            if user_serializer.is_valid():
                user_serializer.save()

        # Update customer fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update measurements if provided
        if measurements_data is not None:
            instance.set_measurements(measurements_data)

        instance.save()
        return instance

    def validate_phone_number(self, value):
        """
        Validate phone number format.
        """
        import re
        if value:
            # Remove all non-digit characters for validation
            digits_only = re.sub(r'\D', '', value)
            if len(digits_only) < 10:
                raise serializers.ValidationError("Phone number must contain at least 10 digits.")
        return value


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
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(),
        source='customer',
        write_only=True
    )
    fabric = FabricSerializer(read_only=True)
    fabric_id = serializers.PrimaryKeyRelatedField(
        queryset=Fabric.objects.all(),
        source='fabric',
        write_only=True,
        required=False,
        allow_null=True
    )
    accessories = AccessorySerializer(many=True, read_only=True)
    accessories_ids = serializers.PrimaryKeyRelatedField(
        queryset=Accessory.objects.all(),
        many=True,
        required=False,
        source='accessories',
        write_only=True
    )

    # New preference fields for static pricing model
    accessories_preference = serializers.CharField(max_length=500, required=False, allow_blank=True)

    # Payment option field (not stored in model, used for processing)
    payment_option = serializers.ChoiceField(
        choices=[('DOWN_PAYMENT', 'Down Payment'), ('FULL_PAYMENT', 'Full Payment')],
        required=False,
        default='DOWN_PAYMENT',
        write_only=True
    )

    # Add display fields for choices
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    garment_type_display = serializers.CharField(source='get_garment_type_display', read_only=True)
    sleeve_length_display = serializers.CharField(source='get_sleeve_length_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'customer_id', 'fabric', 'fabric_id', 'accessories', 'accessories_ids',
            'category', 'category_display', 'garment_type', 'garment_type_display', 'quantity',
            'fabric_type', 'color_design_preference', 'accessories_preference', 'payment_option', 'order_date', 'due_date',
            'total_amount', 'status', 'payment_status', 'paid_at', 'created_at', 'updated_at',
            # Measurement fields
            'neck_circumference', 'shoulder_width', 'chest_bust_circumference',
            'upper_bust_circumference', 'under_bust_circumference', 'waist_circumference',
            'armhole_circumference', 'sleeve_length', 'sleeve_length_display', 'bicep_circumference',
            'wrist_circumference', 'back_length_nape_to_waist', 'blouse_length_shoulder_to_hem',
            'high_hip_circumference', 'full_hip_circumference', 'thigh_circumference',
            'knee_circumference', 'calf_circumference', 'ankle_circumference',
            'inseam_crotch_to_ankle', 'outseam_waist_to_ankle', 'front_rise', 'back_rise',
            'skirt_dress_length', 'hem_circumference', 'jacket_length_shoulder_to_hem'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'paid_at', 'order_date']
    
    def create(self, validated_data):
        from django.utils import timezone
        from datetime import timedelta
        from .business_logic import OrderManager, PricingManager

        # Extract accessories data and payment option before creating order
        accessories = validated_data.pop('accessories', [])
        payment_option = validated_data.pop('payment_option', 'DOWN_PAYMENT')

        # Set default due_date if not provided (7 days from now)
        if 'due_date' not in validated_data or not validated_data.get('due_date'):
            validated_data['due_date'] = timezone.now().date() + timedelta(days=7)

        # Use static pricing instead of dynamic calculation
        garment_type = validated_data.get('garment_type', 'OTHERS')
        quantity = validated_data.get('quantity', 1)

        # Calculate total amount using static pricing
        total_amount = PricingManager.calculate_order_total(garment_type, quantity)
        validated_data['total_amount'] = total_amount

        # Calculate down payment (50% of total)
        down_payment_amount = PricingManager.calculate_down_payment(total_amount)
        validated_data['down_payment_amount'] = down_payment_amount
        validated_data['remaining_balance'] = total_amount - down_payment_amount

        # Handle payment option
        if payment_option == 'FULL_PAYMENT':
            # Customer is paying in full
            validated_data['payment_status'] = 'PAID'
            validated_data['paid_at'] = timezone.now()
            validated_data['down_payment_status'] = 'PAID'
            validated_data['down_payment_paid_at'] = timezone.now()
        else:
            # Customer is paying down payment only
            validated_data['payment_status'] = 'PENDING'
            validated_data['down_payment_status'] = 'PENDING'

        # For static pricing model, we need to assign default fabric and accessories
        # if not provided, based on availability
        if not validated_data.get('fabric'):
            # Get the first available fabric (this could be enhanced with better logic)
            from .models import Fabric
            available_fabric = Fabric.objects.filter(quantity__gt=0).first()
            if available_fabric:
                validated_data['fabric'] = available_fabric

        # Create the order instance without accessories
        order = Order.objects.create(**validated_data)

        # Add accessories using set() method to handle many-to-many relationship
        if accessories:
            order.accessories.set(accessories)
        else:
            # For static pricing, assign default accessories if none provided
            from .models import Accessory
            available_accessories = Accessory.objects.filter(quantity__gt=0)[:2]  # Get up to 2 accessories
            if available_accessories:
                order.accessories.set(available_accessories)

        # Process order creation (including inventory deduction)
        try:
            OrderManager.process_order_creation(order)
        except ValidationError as e:
            # If inventory deduction fails, delete the order and re-raise the error
            order.delete()
            raise e

        return order
    
    def update(self, instance, validated_data):
        # Extract accessories before updating other fields
        accessories = validated_data.pop('accessories', None)
        
        # Update the order instance with other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # If total_amount wasn't provided or was set to 0, calculate it
        if 'total_amount' not in validated_data or not instance.total_amount:
            instance.total_amount = instance.calculate_total_amount()
        
        # Save the instance
        instance.save()
        
        # Update accessories using set() if provided
        if accessories is not None:
            instance.accessories.set(accessories)
        
        return instance

    def validate_due_date(self, value):
        """
        Validate that due_date is not in the past.
        """
        from django.utils import timezone
        if value and value < timezone.now().date():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value

    def validate_quantity(self, value):
        """
        Validate that quantity is positive.
        """
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value

    def validate(self, data):
        """
        Validate the entire order data.
        """
        # Validate that due_date is after order_date
        order_date = data.get('order_date')
        due_date = data.get('due_date')

        if order_date and due_date and due_date <= order_date:
            raise serializers.ValidationError({
                'due_date': 'Due date must be after order date.'
            })

        return data


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
                'category': obj.order.get_category_display() if obj.order.category else 'N/A',
                'garment_type': obj.order.get_garment_type_display() if obj.order.garment_type else 'N/A',
                'quantity': obj.order.quantity,
                'fabric': obj.order.fabric.name if obj.order.fabric else 'N/A',
                'fabric_type': obj.order.fabric_type or 'N/A',
                'fabric_unit_type': obj.order.fabric.unit_type if obj.order.fabric else 'N/A',
                'color_design_preference': obj.order.color_design_preference or 'N/A',
                'due_date': obj.order.due_date,
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
                'category': 'N/A',
                'garment_type': 'N/A',
                'quantity': 1,
                'fabric': 'N/A',
                'fabric_type': 'N/A',
                'fabric_unit_type': 'N/A',
                'color_design_preference': 'N/A',
                'due_date': None,
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
            if obj.order:
                # Get order-specific measurements
                order_measurements = obj.order.get_measurements_for_garment_type()

                # Format order measurements as readable strings
                order_measurements_formatted = {}
                for key, value in order_measurements.items():
                    if value is not None and value != '':
                        # Convert field names to readable format
                        readable_key = key.replace('_', ' ').title()
                        # Format numeric values with units
                        if isinstance(value, (int, float)) or (isinstance(value, str) and value.replace('.', '').isdigit()):
                            order_measurements_formatted[readable_key] = f"{value} cm"
                        else:
                            order_measurements_formatted[readable_key] = str(value)

                # Get customer's basic measurements
                customer_measurements_formatted = {}
                if obj.order.customer:
                    customer_measurements = obj.order.customer.get_measurements()
                    for key, value in customer_measurements.items():
                        if value is not None and value != '':
                            # Convert field names to readable format
                            readable_key = key.replace('_', ' ').title()
                            customer_measurements_formatted[readable_key] = f"{value} cm" if isinstance(value, (int, float)) else str(value)

                return {
                    'order_measurements': order_measurements_formatted,
                    'customer_measurements': customer_measurements_formatted
                }
            return {
                'order_measurements': {},
                'customer_measurements': {}
            }
        except AttributeError:
            return {
                'order_measurements': {},
                'customer_measurements': {}
            }


class CommissionSerializer(serializers.ModelSerializer):
    tailor = TailorSerializer(read_only=True)
    
    class Meta:
        model = Commission
        fields = [
            'id', 'tailor', 'amount', 'order', 
            'status', 'created_at', 'paid_at'
        ]
        read_only_fields = ['id', 'created_at']