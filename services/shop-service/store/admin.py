from django.contrib import admin
from .models import Category,Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name','parent','product_count','is_active')
    search_fields = ('name',)
    list_filter = ('is_active','parent')
# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','category','price','is_active')
    search_fields = ('name','description')
    list_filter = ('category','is_active','created_at')