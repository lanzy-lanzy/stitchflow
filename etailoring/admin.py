from django.contrib import admin
from .models import (
    UserExtension, Customer, Tailor, Fabric, 
    Accessory, Order, Task, Commission, Testimonial
)


@admin.register(UserExtension)
class UserExtensionAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone_number']
    list_filter = ['role']
    search_fields = ['user__username', 'user__email']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number']
    search_fields = ['user__username', 'user__email']


@admin.register(Tailor)
class TailorAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'specialty', 'commission_rate']
    list_filter = ['specialty']
    search_fields = ['user__username', 'user__email']


@admin.register(Fabric)
class FabricAdmin(admin.ModelAdmin):
    list_display = ['name', 'unit_type', 'quantity', 'price_per_unit', 'is_low_stock']
    list_filter = ['unit_type']
    search_fields = ['name']


@admin.register(Accessory)
class AccessoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'quantity', 'price_per_unit', 'is_low_stock']
    search_fields = ['name']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'fabric', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer__user__username', 'id']
    filter_horizontal = ['accessories']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['order', 'tailor', 'status', 'assigned_at']
    list_filter = ['status', 'assigned_at']
    search_fields = ['order__id', 'tailor__user__username']


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ['tailor', 'amount', 'order', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['tailor__user__username', 'order__id']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'role', 'company', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'company']
    list_editable = ['is_active']