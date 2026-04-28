from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.ReviewListCreateAPIView.as_view(), name='api_review_list'),
    path('<int:pk>/', api_views.ReviewDetailAPIView.as_view(), name='api_review_detail'),
]
