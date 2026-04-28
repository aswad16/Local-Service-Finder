from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Import home view directly to avoid double-including services.urls
from services.views import home_view

urlpatterns = [
    path('admin/', admin.site.urls),

    # Home page (served by services app, no namespace conflict)
    path('', home_view, name='home'),

    # Apps with namespaces
    path('services/', include('services.urls', namespace='services')),
    path('users/', include('users.urls', namespace='users')),
    path('reviews/', include('reviews.urls')),
    path('search/', include('search.urls')),
    path('adminpanel/', include('adminpanel.urls')),

    # REST API
    path('api/users/', include('users.api_urls')),
    path('api/services/', include('services.api_urls')),
    path('api/reviews/', include('reviews.api_urls')),
    path('api/search/', include('search.api_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
