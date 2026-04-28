from django.contrib import admin
from .models import Service, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'provider', 'category', 'city', 'price', 'is_active', 'is_featured', 'views_count']
    list_filter = ['is_active', 'is_featured', 'category']
    search_fields = ['title', 'city', 'provider__username']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_active', 'is_featured']
