from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.service_list_view, name='service_list'),
    path('create/', views.service_create_view, name='service_create'),
    path('dashboard/', views.provider_dashboard_view, name='provider_dashboard'),
    path('<slug:slug>/', views.service_detail_view, name='service_detail'),
    path('<slug:slug>/edit/', views.service_edit_view, name='service_edit'),
    path('<slug:slug>/delete/', views.service_delete_view, name='service_delete'),
]
