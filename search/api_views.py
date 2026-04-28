from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from services.models import Service
from services.serializers import ServiceSerializer


class SearchAPIView(APIView):
    def get(self, request):
        query = request.GET.get('q', '').strip()
        city = request.GET.get('city', '').strip()
        category = request.GET.get('category', '').strip()

        services = Service.objects.filter(is_active=True).select_related('provider', 'category')
        if query:
            services = services.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(city__icontains=query)
            )
        if city:
            services = services.filter(city__icontains=city)
        if category:
            services = services.filter(category__slug=category)

        serializer = ServiceSerializer(services[:20], many=True, context={'request': request})
        return Response({'count': services.count(), 'results': serializer.data})
