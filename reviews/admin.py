from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'service', 'rating', 'is_verified', 'created_at']
    list_filter = ['rating', 'is_verified']
    list_editable = ['is_verified']
    search_fields = ['reviewer__username', 'service__title', 'comment']
