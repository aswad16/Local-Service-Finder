from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import api_views

urlpatterns = [
    path('register/', api_views.RegisterAPIView.as_view(), name='api_register'),
    path('login/', api_views.CustomTokenObtainPairView.as_view(), name='api_login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', api_views.MeAPIView.as_view(), name='api_me'),
    path('profile/update/', api_views.ProfileUpdateAPIView.as_view(), name='api_profile_update'),
]
