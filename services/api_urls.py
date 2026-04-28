from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.ServiceListCreateAPIView.as_view(), name='api_service_list'),
    path('<slug:slug>/', api_views.ServiceDetailAPIView.as_view(), name='api_service_detail'),
    path('categories/', api_views.CategoryListAPIView.as_view(), name='api_category_list'),
]
