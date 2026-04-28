import functools
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta
from users.models import CustomUser
from services.models import Service, Category
from reviews.models import Review
from .forms import CategoryForm


def admin_required(view_func):
    """Decorator: requires authenticated admin user. Preserves all function metadata."""
    @functools.wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_admin_user:
            messages.error(request, 'Admin access required.')
            return redirect('users:login')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def dashboard_view(request):
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    stats = {
        'total_users': CustomUser.objects.count(),
        'new_users_week': CustomUser.objects.filter(date_joined__gte=week_ago).count(),
        'total_providers': CustomUser.objects.filter(role='provider').count(),
        'total_services': Service.objects.count(),
        'active_services': Service.objects.filter(is_active=True).count(),
        'new_services_month': Service.objects.filter(created_at__gte=month_ago).count(),
        'total_reviews': Review.objects.count(),
        'new_reviews_week': Review.objects.filter(created_at__gte=week_ago).count(),
        'total_categories': Category.objects.count(),
    }

    recent_users = CustomUser.objects.order_by('-date_joined')[:8]
    recent_services = Service.objects.select_related('provider', 'category').order_by('-created_at')[:8]
    recent_reviews = Review.objects.select_related('reviewer', 'service').order_by('-created_at')[:6]
    top_categories = Category.objects.annotate(count=Count('services')).order_by('-count')[:5]

    return render(request, 'adminpanel/dashboard.html', {
        'stats': stats,
        'recent_users': recent_users,
        'recent_services': recent_services,
        'recent_reviews': recent_reviews,
        'top_categories': top_categories,
    })


@admin_required
def user_list_view(request):
    role = request.GET.get('role', '')
    search = request.GET.get('q', '')
    users = CustomUser.objects.all().order_by('-date_joined')
    if role:
        users = users.filter(role=role)
    if search:
        users = users.filter(username__icontains=search) | users.filter(email__icontains=search)
    return render(request, 'adminpanel/user_list.html', {'users': users, 'role': role, 'search': search})


@admin_required
@require_POST
def user_toggle_active(request, pk):
    """Toggle user active status. POST-only to prevent CSRF via GET."""
    user = get_object_or_404(CustomUser, pk=pk)
    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])
    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'User {user.username} has been {status}.')
    return redirect('adminpanel:user_list')


@admin_required
def service_list_view(request):
    search = request.GET.get('q', '')
    status = request.GET.get('status', '')
    services = Service.objects.select_related('provider', 'category').order_by('-created_at')
    if search:
        services = services.filter(title__icontains=search)
    if status == 'active':
        services = services.filter(is_active=True)
    elif status == 'inactive':
        services = services.filter(is_active=False)
    return render(request, 'adminpanel/service_list.html', {
        'services': services, 'search': search, 'status': status
    })


@admin_required
@require_POST
def service_toggle_featured(request, pk):
    """Toggle featured status. POST-only."""
    service = get_object_or_404(Service, pk=pk)
    service.is_featured = not service.is_featured
    service.save(update_fields=['is_featured'])
    messages.success(request, f'Service "{service.title}" featured status updated.')
    return redirect('adminpanel:service_list')


@admin_required
@require_POST
def service_toggle_active(request, pk):
    """Toggle active status. POST-only."""
    service = get_object_or_404(Service, pk=pk)
    service.is_active = not service.is_active
    service.save(update_fields=['is_active'])
    messages.success(request, f'Service "{service.title}" status updated.')
    return redirect('adminpanel:service_list')


@admin_required
def review_list_view(request):
    reviews = Review.objects.select_related('reviewer', 'service').order_by('-created_at')
    return render(request, 'adminpanel/review_list.html', {'reviews': reviews})


@admin_required
@require_POST
def review_delete_view(request, pk):
    review = get_object_or_404(Review, pk=pk)
    review.delete()
    messages.success(request, 'Review deleted.')
    return redirect('adminpanel:review_list')


@admin_required
def category_list_view(request):
    categories = Category.objects.annotate(count=Count('services')).order_by('name')
    return render(request, 'adminpanel/category_list.html', {'categories': categories})


@admin_required
def category_create_view(request):
    """Use a proper ModelForm instead of raw POST data."""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" created.')
            return redirect('adminpanel:category_list')
    else:
        form = CategoryForm()
    return render(request, 'adminpanel/category_form.html', {'form': form, 'action': 'Create'})


@admin_required
@require_POST
def category_delete_view(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    name = cat.name
    cat.delete()
    messages.success(request, f'Category "{name}" deleted.')
    return redirect('adminpanel:category_list')
