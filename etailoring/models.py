from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class UserExtension(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('TAILOR', 'Tailor'),
        ('CUSTOMER', 'Customer'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone_number = models.CharField(max_length=15)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    measurements = models.TextField(default='{}', blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} (Customer)"

    def get_full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip()

    def get_measurements(self):
        """Get measurements as a dictionary."""
        import json
        try:
            return json.loads(self.measurements) if self.measurements else {}
        except json.JSONDecodeError:
            return {}

    def set_measurements(self, measurements_dict):
        """Set measurements from a dictionary."""
        import json
        self.measurements = json.dumps(measurements_dict)

    def clean(self):
        from django.core.exceptions import ValidationError
        import re

        # Validate phone number format
        if self.phone_number:
            # Remove all non-digit characters for validation
            digits_only = re.sub(r'\D', '', self.phone_number)
            if len(digits_only) < 10:
                raise ValidationError({'phone_number': 'Phone number must contain at least 10 digits.'})

    class Meta:
        ordering = ['user__first_name', 'user__last_name']


class Tailor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    specialty = models.CharField(max_length=100)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('10.00'))
    
    def __str__(self):
        return f"{self.user.username} (Tailor)"


class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    quote = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} from {self.company}"


class Fabric(models.Model):
    UNIT_TYPE_CHOICES = [
        ('METERS', 'Meters'),
        ('YARDS', 'Yards'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    unit_type = models.CharField(max_length=10, choices=UNIT_TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    low_stock_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('10.00'))
    
    @property
    def is_low_stock(self):
        return self.quantity <= self.low_stock_threshold
    
    def __str__(self):
        return self.name


class Accessory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    quantity = models.IntegerField(default=0)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    low_stock_threshold = models.IntegerField(default=10)
    
    @property
    def is_low_stock(self):
        return self.quantity <= self.low_stock_threshold
    
    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ASSIGNED', 'Assigned'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('DOWN_PAYMENT_PAID', 'Down Payment Paid'),
        ('PAID', 'Paid'),
    ]

    DOWN_PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
    ]

    CATEGORY_CHOICES = [
        ('SCHOOL_UNIFORM', 'School Uniforms'),
        ('TEACHERS_UNIFORM', 'Teachers\' Uniforms'),
        ('OFFICE_ATTIRE', 'Office Attire'),
        ('CASUAL_WEAR', 'Casual Wear'),
        ('SPECIAL_ORDER', 'Special Orders'),
    ]

    GARMENT_TYPE_CHOICES = [
        ('BLOUSE', 'Blouse'),
        ('PANTS', 'Pants'),
        ('SKIRT', 'Skirt'),
        ('DRESS', 'Dress'),
        ('JACKET', 'Jacket'),
        ('OTHERS', 'Others'),
    ]

    SLEEVE_LENGTH_CHOICES = [
        ('SHORT', 'Short'),
        ('THREE_QUARTER', '3/4'),
        ('LONG', 'Long'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    fabric = models.ForeignKey(Fabric, on_delete=models.CASCADE)
    accessories = models.ManyToManyField(Accessory, blank=True)

    # New order categorization fields
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='CASUAL_WEAR')
    garment_type = models.CharField(max_length=10, choices=GARMENT_TYPE_CHOICES, default='OTHERS')
    quantity = models.PositiveIntegerField(default=1)
    fabric_type = models.CharField(max_length=100, blank=True)
    accessories_preference = models.CharField(max_length=500, blank=True)
    color_design_preference = models.TextField(blank=True)
    order_date = models.DateField(auto_now_add=True, null=True)
    due_date = models.DateField(null=True, blank=True)

    # Existing fields
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    # Down payment fields
    down_payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    down_payment_status = models.CharField(max_length=10, choices=DOWN_PAYMENT_STATUS_CHOICES, default='PENDING')
    down_payment_paid_at = models.DateTimeField(null=True, blank=True)
    remaining_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Comprehensive measurement fields for different garment types
    # Blouse/Shirt/Top measurements
    neck_circumference = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    shoulder_width = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    chest_bust_circumference = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    upper_bust_circumference = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    under_bust_circumference = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    waist_circumference = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    armhole_circumference = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    sleeve_length = models.CharField(max_length=15, choices=SLEEVE_LENGTH_CHOICES, blank=True)
    bicep_circumference = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    wrist_circumference = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    back_length_nape_to_waist = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    blouse_length_shoulder_to_hem = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Pants/Trousers measurements
    high_hip_circumference = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    full_hip_circumference = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    thigh_circumference = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    knee_circumference = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    calf_circumference = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ankle_circumference = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    inseam_crotch_to_ankle = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    outseam_waist_to_ankle = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    front_rise = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    back_rise = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Skirt/Dress measurements
    skirt_dress_length = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    hem_circumference = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Jacket/Coat measurements (optional)
    jacket_length_shoulder_to_hem = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"Order {self.id} - {self.customer.user.username} ({self.get_category_display()} - {self.get_garment_type_display()})"

    def calculate_total_amount(self):
        """
        Calculate the total amount using static pricing based on garment type.
        """
        from .business_logic import PricingManager
        return PricingManager.calculate_order_total(self.garment_type, self.quantity)

    def calculate_down_payment(self):
        """
        Calculate 50% down payment of total amount.
        """
        return self.total_amount * Decimal('0.5')

    def calculate_remaining_balance(self):
        """
        Calculate remaining balance after down payment.
        """
        return self.total_amount - self.down_payment_amount

    def update_payment_amounts(self):
        """
        Update down payment and remaining balance based on total amount.
        """
        self.down_payment_amount = self.calculate_down_payment()
        self.remaining_balance = self.calculate_remaining_balance()

    def save(self, *args, **kwargs):
        # Only calculate total amount automatically if it's not provided or is zero
        if not self.total_amount:
            # For new orders, we can't access accessories yet, so we'll calculate in the serializer
            if self.pk:
                self.total_amount = self.calculate_total_amount()

        # Update payment amounts when total amount changes
        if self.total_amount:
            self.update_payment_amounts()

        super().save(*args, **kwargs)

    def get_measurements_for_garment_type(self):
        """
        Return relevant measurements based on garment type.
        """
        measurements = {}

        if self.garment_type in ['BLOUSE']:
            measurements.update({
                'neck_circumference': self.neck_circumference,
                'shoulder_width': self.shoulder_width,
                'chest_bust_circumference': self.chest_bust_circumference,
                'upper_bust_circumference': self.upper_bust_circumference,
                'under_bust_circumference': self.under_bust_circumference,
                'waist_circumference': self.waist_circumference,
                'armhole_circumference': self.armhole_circumference,
                'sleeve_length': self.sleeve_length,
                'bicep_circumference': self.bicep_circumference,
                'wrist_circumference': self.wrist_circumference,
                'back_length_nape_to_waist': self.back_length_nape_to_waist,
                'blouse_length_shoulder_to_hem': self.blouse_length_shoulder_to_hem,
            })

        if self.garment_type in ['PANTS']:
            measurements.update({
                'waist_circumference': self.waist_circumference,
                'high_hip_circumference': self.high_hip_circumference,
                'full_hip_circumference': self.full_hip_circumference,
                'thigh_circumference': self.thigh_circumference,
                'knee_circumference': self.knee_circumference,
                'calf_circumference': self.calf_circumference,
                'ankle_circumference': self.ankle_circumference,
                'inseam_crotch_to_ankle': self.inseam_crotch_to_ankle,
                'outseam_waist_to_ankle': self.outseam_waist_to_ankle,
                'front_rise': self.front_rise,
                'back_rise': self.back_rise,
            })

        if self.garment_type in ['SKIRT', 'DRESS']:
            measurements.update({
                'waist_circumference': self.waist_circumference,
                'high_hip_circumference': self.high_hip_circumference,
                'full_hip_circumference': self.full_hip_circumference,
                'skirt_dress_length': self.skirt_dress_length,
                'hem_circumference': self.hem_circumference,
            })

            # For dresses, also include upper body measurements
            if self.garment_type == 'DRESS':
                measurements.update({
                    'chest_bust_circumference': self.chest_bust_circumference,
                    'upper_bust_circumference': self.upper_bust_circumference,
                    'under_bust_circumference': self.under_bust_circumference,
                    'shoulder_width': self.shoulder_width,
                })

        if self.garment_type in ['JACKET']:
            measurements.update({
                'neck_circumference': self.neck_circumference,
                'shoulder_width': self.shoulder_width,
                'chest_bust_circumference': self.chest_bust_circumference,
                'waist_circumference': self.waist_circumference,
                'full_hip_circumference': self.full_hip_circumference,
                'sleeve_length': self.sleeve_length,
                'bicep_circumference': self.bicep_circumference,
                'wrist_circumference': self.wrist_circumference,
                'jacket_length_shoulder_to_hem': self.jacket_length_shoulder_to_hem,
            })

        # Filter out None values
        return {k: v for k, v in measurements.items() if v is not None}

    class Meta:
        ordering = ['-created_at']


class Task(models.Model):
    STATUS_CHOICES = [
        ('ASSIGNED', 'Assigned'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    tailor = models.ForeignKey(Tailor, on_delete=models.CASCADE)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ASSIGNED')
    assigned_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Task for Order {self.order.id}"


class Commission(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
    ]
    
    tailor = models.ForeignKey(Tailor, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Commission for {self.tailor.user.username} - Order {self.order.id}"