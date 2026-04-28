from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from django.views.decorators.http import require_POST
from .forms import RegisterForm, LoginForm, ProfileUpdateForm, OTPVerifyForm, CustomPasswordChangeForm
from .models import CustomUser
from services.models import Service
from reviews.models import Review


# ─────────────────────────────────────────────────────────────────────────────
# OTP delivery  (swap _send_otp_sms body for Twilio / MSG91 in production)
# ─────────────────────────────────────────────────────────────────────────────
def _send_otp_sms(phone: str, otp_code: str) -> bool:
    print(f"[OTP] >>> {otp_code} <<< → {phone}")   # visible in dev console only
    return True


from django.conf import settings

def _otp_send_and_store_in_session(request, user, purpose: str) -> bool:
    try:
        otp = user.generate_otp(purpose=purpose)
        _send_otp_sms(user.phone, otp)
        if getattr(settings, 'DEBUG', False):
            request.session['_dev_otp'] = otp
        return True
    except ValueError as e:
        messages.error(request, str(e))
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Registration
# ─────────────────────────────────────────────────────────────────────────────
def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Welcome, {user.first_name or user.username}! Account created.')
            request.session['verify_after_register'] = True
            return redirect('users:verify_phone')
        else:
            if form.non_field_errors():
                messages.error(request, form.non_field_errors()[0])
            else:
                messages.error(request, 'Please fix the errors below.')
    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form})


# ─────────────────────────────────────────────────────────────────────────────
# Login
# ─────────────────────────────────────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.two_factor_enabled and user.phone and user.phone_verified:
                sent = _otp_send_and_store_in_session(request, user, '2fa_login')
                request.session['2fa_user_id'] = user.pk
                if sent:
                    messages.info(request, f'OTP sent to ···{user.phone[-4:]}. Check your phone.')
                return redirect('users:verify_2fa')
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.GET.get('next', '').strip()
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            if user.is_admin_user:
                return redirect('adminpanel:dashboard')
            if user.is_provider:
                return redirect('services:provider_dashboard')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})


# ─────────────────────────────────────────────────────────────────────────────
# 2FA verification
# ─────────────────────────────────────────────────────────────────────────────
def verify_2fa_view(request):
    user_id = request.session.get('2fa_user_id')
    if not user_id:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('users:login')

    try:
        user = CustomUser.objects.get(pk=user_id)
    except CustomUser.DoesNotExist:
        return redirect('users:login')

    dev_otp = request.session.pop('_dev_otp', None)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'resend':
            sent = _otp_send_and_store_in_session(request, user, '2fa_login')
            request.session['2fa_user_id'] = user_id
            if sent:
                dev_otp = request.session.pop('_dev_otp', None)
                messages.info(request, 'New OTP sent.')
            return render(request, 'users/verify_otp.html', {
                'form': OTPVerifyForm(), 'purpose': '2fa',
                'phone_hint': user.phone[-4:] if user.phone else '',
                'dev_otp': dev_otp, 'otp_sent': True,
            })

        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            entered = form.cleaned_data['otp']
            if user.verify_otp(entered, purpose='2fa_login'):
                user.clear_otp()
                request.session.pop('2fa_user_id', None)
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                if user.is_admin_user:
                    return redirect('adminpanel:dashboard')
                if user.is_provider:
                    return redirect('services:provider_dashboard')
                return redirect('home')
            else:
                messages.error(request, 'Invalid or expired OTP.')
        return render(request, 'users/verify_otp.html', {
            'form': form, 'purpose': '2fa',
            'phone_hint': user.phone[-4:] if user.phone else '',
            'dev_otp': dev_otp,
        })

    return render(request, 'users/verify_otp.html', {
        'form': OTPVerifyForm(), 'purpose': '2fa',
        'phone_hint': user.phone[-4:] if user.phone else '',
        'dev_otp': dev_otp,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Phone verification
# ─────────────────────────────────────────────────────────────────────────────
@login_required
def verify_phone_view(request):
    user = request.user
    dev_otp = request.session.pop('_dev_otp', None)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'send_otp':
            if not user.phone:
                messages.error(request, 'Add a phone number to your profile first.')
                return redirect('users:profile_edit')
            sent = _otp_send_and_store_in_session(request, user, 'phone_verify')
            if sent:
                dev_otp = request.session.pop('_dev_otp', None)
                messages.info(request, f'OTP sent to {user.phone}.')
            return render(request, 'users/verify_otp.html', {
                'form': OTPVerifyForm(), 'purpose': 'phone',
                'phone_hint': user.phone[-4:] if user.phone else '',
                'dev_otp': dev_otp, 'otp_sent': True,
            })

        if action == 'resend':
            if not user.phone:
                return redirect('users:profile_edit')
            sent = _otp_send_and_store_in_session(request, user, 'phone_verify')
            if sent:
                dev_otp = request.session.pop('_dev_otp', None)
                messages.info(request, 'New OTP sent.')
            return render(request, 'users/verify_otp.html', {
                'form': OTPVerifyForm(), 'purpose': 'phone',
                'phone_hint': user.phone[-4:] if user.phone else '',
                'dev_otp': dev_otp, 'otp_sent': True,
            })

        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            entered = form.cleaned_data['otp']
            if user.verify_otp(entered, purpose='phone_verify'):
                user.phone_verified = True
                user.is_verified = True
                user.clear_otp()
                user.save(update_fields=['phone_verified', 'is_verified'])
                messages.success(request, 'Phone verified! Your account is now verified.')
                request.session.pop('verify_after_register', None)
                return redirect('users:profile')
            else:
                messages.error(request, 'Invalid or expired OTP. Please try again.')
        return render(request, 'users/verify_otp.html', {
            'form': form, 'purpose': 'phone',
            'phone_hint': user.phone[-4:] if user.phone else '',
            'dev_otp': dev_otp,
        })

    # GET — show option to send OTP
    if not user.phone:
        messages.warning(request, 'Please add a phone number to your profile first.')
        return redirect('users:profile_edit')

    # Auto-send on first arrival after registration
    if request.session.get('verify_after_register') and not dev_otp:
        sent = _otp_send_and_store_in_session(request, user, 'phone_verify')
        if sent:
            dev_otp = request.session.pop('_dev_otp', None)

    return render(request, 'users/verify_otp.html', {
        'form': OTPVerifyForm(), 'purpose': 'phone',
        'phone_hint': user.phone[-4:] if user.phone else '',
        'dev_otp': dev_otp, 'otp_sent': bool(dev_otp),
    })


# ─────────────────────────────────────────────────────────────────────────────
# Logout
# ─────────────────────────────────────────────────────────────────────────────
@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been signed out.')
    return redirect('home')


# ─────────────────────────────────────────────────────────────────────────────
# Profile
# ─────────────────────────────────────────────────────────────────────────────
@login_required
def profile_view(request):
    user = request.user
    tab = request.GET.get('tab', 'overview')
    services = Service.objects.filter(provider=user).select_related('category') if user.is_provider else None
    reviews  = Review.objects.filter(reviewer=user).select_related('service').order_by('-created_at')[:10]
    given_reviews_count = Review.objects.filter(reviewer=user).count()
    received_reviews = Review.objects.filter(service__provider=user).order_by('-created_at')[:10] if user.is_provider else None
    return render(request, 'users/profile.html', {
        'profile_user': user,
        'services': services,
        'reviews': reviews,
        'given_reviews_count': given_reviews_count,
        'received_reviews': received_reviews,
        'active_tab': tab,
    })


@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            # Save country codes too
            user.phone_country_code = form.cleaned_data.get('phone_country_code', '+91')
            user.whatsapp_country_code = form.cleaned_data.get('whatsapp_country_code', '+91')
            user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'users/profile_edit.html', {'form': form})


# ─────────────────────────────────────────────────────────────────────────────
# Password Change
# ─────────────────────────────────────────────────────────────────────────────
@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'users/password_change.html', {'form': form})


# ─────────────────────────────────────────────────────────────────────────────
# Language Switch
# ─────────────────────────────────────────────────────────────────────────────
@login_required
@require_POST
def set_language_view(request):
    lang = request.POST.get('language', 'en')
    if lang in ('en', 'hi'):
        request.user.preferred_language = lang
        request.user.save(update_fields=['preferred_language'])
    return redirect(request.META.get('HTTP_REFERER', '/'))


# ─────────────────────────────────────────────────────────────────────────────
# Provider Detail
# ─────────────────────────────────────────────────────────────────────────────
def provider_detail_view(request, pk):
    provider = get_object_or_404(CustomUser, pk=pk, role='provider')
    services  = Service.objects.filter(provider=provider, is_active=True)
    reviews   = Review.objects.filter(service__provider=provider).order_by('-created_at')[:10]
    avg_rating = services.aggregate(avg=Avg('reviews__rating'))['avg']
    avg_rating = round(avg_rating, 1) if avg_rating else 0
    return render(request, 'users/provider_detail.html', {
        'provider': provider, 'services': services,
        'reviews': reviews,   'avg_rating': avg_rating,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def _phone_hint(phone: str) -> str:
    return phone[-4:] if phone and len(phone) >= 4 else phone or ''


def _post_login_url(user) -> str:
    if user.is_admin_user:
        return '/adminpanel/'
    if user.is_provider:
        return '/services/dashboard/'
    return '/'
