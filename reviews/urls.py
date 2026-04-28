from django.urls import path
from . import views

urlpatterns = [
    path('add/<slug:service_slug>/', views.add_review_view, name='add_review'),
    path('delete/<int:pk>/', views.delete_review_view, name='delete_review'),
]
