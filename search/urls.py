from django.urls import path
from . import views

urlpatterns = [
    path('', views.search_view, name='search'),
    path('recommend/', views.ai_recommend_view, name='ai_recommend'),
]
