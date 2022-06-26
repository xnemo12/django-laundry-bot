from django.contrib import admin

# Register your models here.
from order.models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'courier', 'location', 'order_time', 'state', 'description', 'created_at']
