from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review
from .forms import ReviewForm
from services.models import Service


@login_required
def add_review_view(request, service_slug):
    service = get_object_or_404(Service, slug=service_slug, is_active=True)
    if service.provider == request.user:
        messages.error(request, "You cannot review your own service.")
        return redirect('services:service_detail', slug=service_slug)

    existing = Review.objects.filter(service=service, reviewer=request.user).first()
    if existing:
        messages.info(request, "You have already reviewed this service.")
        return redirect('services:service_detail', slug=service_slug)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.service = service
            review.reviewer = request.user
            review.save()
            messages.success(request, "Review submitted successfully!")
        else:
            messages.error(request, "Please correct the errors.")
    return redirect('services:service_detail', slug=service_slug)


@login_required
def delete_review_view(request, pk):
    review = get_object_or_404(Review, pk=pk, reviewer=request.user)
    service_slug = review.service.slug
    if request.method == 'POST':
        review.delete()
        messages.success(request, "Review deleted.")
    return redirect('services:service_detail', slug=service_slug)
