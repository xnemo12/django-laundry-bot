from django.contrib import admin

from core.models import ProductCategory, Product


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'lang', 'emoji', 'order', 'created_at']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'uom', 'price', 'lang', 'emoji', 'order', 'created_at']
