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
    measurements = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"{self.user.username} (Customer)"


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
        ('PARTIAL', 'Partial'),
        ('PAID', 'Paid'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    fabric = models.ForeignKey(Fabric, on_delete=models.CASCADE)
    accessories = models.ManyToManyField(Accessory, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Order {self.id} - {self.customer.user.username}"
    
    def calculate_total_amount(self):
        """
        Calculate the total amount based on fabric and accessories.
        Assumes 1 unit of fabric and 1 unit of each accessory.
        """
        total = self.fabric.price_per_unit if self.fabric else 0
        
        # For existing orders, we can access accessories
        if self.pk:
            for accessory in self.accessories.all():
                total += accessory.price_per_unit
            
        return total
    
    def save(self, *args, **kwargs):
        # Only calculate total amount automatically if it's not provided or is zero
        if not self.total_amount:
            # For new orders, we can't access accessories yet, so we'll calculate in the serializer
            if self.pk:
                self.total_amount = self.calculate_total_amount()
        super().save(*args, **kwargs)


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