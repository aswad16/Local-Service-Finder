from rest_framework import serializers
from .models import Service, Category
from users.serializers import UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    service_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'description', 'service_count']

    def get_service_count(self, obj):
        return obj.services.filter(is_active=True).count()


class ServiceSerializer(serializers.ModelSerializer):
    provider = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    avg_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()

    class Meta:
        model = Service
        fields = ['id', 'provider', 'category', 'category_id', 'title', 'slug',
                  'description', 'price', 'price_type', 'city', 'state', 'address',
                  'phone', 'email', 'image', 'is_active', 'is_featured',
                  'views_count', 'avg_rating', 'review_count', 'created_at']
        read_only_fields = ['slug', 'views_count', 'created_at']

    def create(self, validated_data):
        validated_data['provider'] = self.context['request'].user
        return super().create(validated_data)
