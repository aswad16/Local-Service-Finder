from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('users/', views.user_list_view, name='user_list'),
    path('users/<int:pk>/toggle/', views.user_toggle_active, name='user_toggle'),
    path('services/', views.service_list_view, name='service_list'),
    path('services/<int:pk>/featured/', views.service_toggle_featured, name='service_featured'),
    path('services/<int:pk>/active/', views.service_toggle_active, name='service_active'),
    path('reviews/', views.review_list_view, name='review_list'),
    path('reviews/<int:pk>/delete/', views.review_delete_view, name='review_delete'),
    path('categories/', views.category_list_view, name='category_list'),
    path('categories/create/', views.category_create_view, name='category_create'),
    path('categories/<int:pk>/delete/', views.category_delete_view, name='category_delete'),
]
