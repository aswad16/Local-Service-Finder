from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profile/password/', views.password_change_view, name='password_change'),
    path('profile/language/', views.set_language_view, name='set_language'),
    path('provider/<int:pk>/', views.provider_detail_view, name='provider_detail'),
    path('verify-phone/', views.verify_phone_view, name='verify_phone'),
    path('verify-2fa/', views.verify_2fa_view, name='verify_2fa'),
]
