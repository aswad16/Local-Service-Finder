from django.db import models
from django.db.models import Avg
from django.conf import settings
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.CharField(max_length=50, default='🔧')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Service(models.Model):
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='service_set', limit_choices_to={'role': 'provider'}
    )
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='services')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_type = models.CharField(max_length=20, choices=[
        ('fixed', 'Fixed Price'), ('hourly', 'Per Hour'), ('daily', 'Per Day'), ('negotiable', 'Negotiable')
    ], default='fixed')
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=300, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            slug = base
            n = 1
            while Service.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def avg_rating(self):
        if hasattr(self, 'avg_r'):
            result = self.avg_r
        else:
            result = self.reviews.aggregate(avg=Avg('rating'))['avg']
        return round(result, 1) if result else 0

    @property
    def review_count(self):
        if hasattr(self, 'review_cnt'):
            return self.review_cnt
        return self.reviews.count()
