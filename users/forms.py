from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.core.validators import RegexValidator
from .models import CustomUser

# Country codes list
COUNTRY_CODES = [
    ('+91', '🇮🇳 +91 India'),
    ('+1',  '🇺🇸 +1 USA/Canada'),
    ('+44', '🇬🇧 +44 UK'),
    ('+971','🇦🇪 +971 UAE'),
    ('+966','🇸🇦 +966 Saudi Arabia'),
    ('+92', '🇵🇰 +92 Pakistan'),
    ('+880','🇧🇩 +880 Bangladesh'),
    ('+94', '🇱🇰 +94 Sri Lanka'),
    ('+977','🇳🇵 +977 Nepal'),
    ('+60', '🇲🇾 +60 Malaysia'),
    ('+65', '🇸🇬 +65 Singapore'),
    ('+61', '🇦🇺 +61 Australia'),
    ('+49', '🇩🇪 +49 Germany'),
    ('+33', '🇫🇷 +33 France'),
    ('+81', '🇯🇵 +81 Japan'),
    ('+86', '🇨🇳 +86 China'),
    ('+7',  '🇷🇺 +7 Russia'),
    ('+55', '🇧🇷 +55 Brazil'),
    ('+27', '🇿🇦 +27 South Africa'),
    ('+234','🇳🇬 +234 Nigeria'),
]

phone_validator = RegexValidator(
    regex=r'^[0-9]{6,14}$',
    message='Enter digits only (6-14 digits, no spaces or dashes).'
)


class RegisterForm(UserCreationForm):
    ROLE_CHOICES = [
        ('customer', 'Customer - Find local services'),
        ('provider', 'Provider - Offer your services'),
    ]

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'role-radio'}),
        initial='customer',
    )
    first_name = forms.CharField(max_length=150, required=True,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First name'}))
    last_name = forms.CharField(max_length=150, required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last name'}))
    email = forms.EmailField(required=True,
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'you@example.com'}))

    phone_country_code = forms.ChoiceField(
        choices=COUNTRY_CODES, initial='+91',
        widget=forms.Select(attrs={'class': 'country-code-select'}),
        required=False,
    )
    phone = forms.CharField(max_length=14, required=True, validators=[phone_validator],
        widget=forms.TextInput(attrs={'class': 'form-input phone-number-input', 'placeholder': '9XXXXXXXXX'}))

    whatsapp_country_code = forms.ChoiceField(
        choices=COUNTRY_CODES, initial='+91',
        widget=forms.Select(attrs={'class': 'country-code-select'}),
        required=False,
    )
    whatsapp_no = forms.CharField(max_length=14, required=False, validators=[phone_validator],
        widget=forms.TextInput(attrs={'class': 'form-input phone-number-input', 'placeholder': 'Same as phone or different'}),
        help_text='Leave blank to use same as phone')

    city = forms.CharField(max_length=100, required=True,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Your city'}))
    state = forms.CharField(max_length=100, required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Your state / province'}))
    bio = forms.CharField(required=False,
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 3,
                                     'placeholder': 'Tell clients about yourself and your expertise...'}))
    preferred_language = forms.ChoiceField(
        choices=[('en', 'English'), ('hi', 'Hindi')],
        initial='en',
        widget=forms.Select(attrs={'class': 'form-input'}),
        required=False,
    )

    class Meta:
        model = CustomUser
        fields = [
            'role', 'first_name', 'last_name', 'username', 'email',
            'phone_country_code', 'phone', 'whatsapp_country_code', 'whatsapp_no',
            'city', 'state', 'bio', 'preferred_language',
            'password1', 'password2',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Choose a username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Create password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Confirm password'})
        self.fields['email'].widget.attrs.update({'class': 'form-input'})

    def clean_role(self):
        role = self.cleaned_data.get('role')
        if role == 'admin':
            raise forms.ValidationError('Admin accounts cannot be created through registration.')
        return role

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower()
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('whatsapp_no') and cleaned.get('phone'):
            cleaned['whatsapp_no'] = cleaned['phone']
        if not cleaned.get('whatsapp_country_code') and cleaned.get('phone_country_code'):
            cleaned['whatsapp_country_code'] = cleaned['phone_country_code']
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name  = self.cleaned_data.get('last_name', '')
        user.email      = self.cleaned_data.get('email', '')
        cc   = self.cleaned_data.get('phone_country_code', '+91')
        ph   = self.cleaned_data.get('phone', '')
        user.phone = f"{cc}{ph}" if ph else ''
        user.phone_country_code = cc
        wcc  = self.cleaned_data.get('whatsapp_country_code', '+91')
        wph  = self.cleaned_data.get('whatsapp_no', '')
        user.whatsapp_no = f"{wcc}{wph}" if wph else user.phone
        user.whatsapp_country_code = wcc
        user.city       = self.cleaned_data.get('city', '')
        user.state      = self.cleaned_data.get('state', '')
        user.bio        = self.cleaned_data.get('bio', '')
        user.role       = self.cleaned_data.get('role', 'customer')
        user.preferred_language = self.cleaned_data.get('preferred_language', 'en')
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-input', 'placeholder': 'Username or email', 'autofocus': True,
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-input', 'placeholder': 'Password',
        })


class ProfileUpdateForm(forms.ModelForm):
    phone_country_code = forms.ChoiceField(
        choices=COUNTRY_CODES,
        widget=forms.Select(attrs={'class': 'country-code-select'}),
        required=False,
    )
    whatsapp_country_code = forms.ChoiceField(
        choices=COUNTRY_CODES,
        widget=forms.Select(attrs={'class': 'country-code-select'}),
        required=False,
    )

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'phone_country_code', 'phone',
            'whatsapp_country_code', 'whatsapp_no',
            'bio', 'avatar', 'city', 'state', 'location',
            'two_factor_enabled', 'preferred_language',
        ]
        widgets = {
            'bio':         forms.Textarea(attrs={'rows': 4, 'class': 'form-input'}),
            'first_name':  forms.TextInput(attrs={'class': 'form-input'}),
            'last_name':   forms.TextInput(attrs={'class': 'form-input'}),
            'email':       forms.EmailInput(attrs={'class': 'form-input'}),
            'phone':       forms.TextInput(attrs={'class': 'form-input phone-number-input', 'placeholder': '9XXXXXXXXX'}),
            'whatsapp_no': forms.TextInput(attrs={'class': 'form-input phone-number-input', 'placeholder': '9XXXXXXXXX'}),
            'city':        forms.TextInput(attrs={'class': 'form-input'}),
            'state':       forms.TextInput(attrs={'class': 'form-input'}),
            'location':    forms.TextInput(attrs={'class': 'form-input'}),
            'preferred_language': forms.Select(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            self.fields['phone_country_code'].initial = instance.phone_country_code or '+91'
            self.fields['whatsapp_country_code'].initial = instance.whatsapp_country_code or '+91'


class OTPVerifyForm(forms.Form):
    otp = forms.CharField(
        max_length=6, min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-input otp-input',
            'placeholder': '000000',
            'maxlength': '6',
            'inputmode': 'numeric',
            'pattern': '[0-9]{6}',
            'autocomplete': 'one-time-code',
            'autofocus': True,
        })
    )

    def clean_otp(self):
        otp = self.cleaned_data.get('otp', '').strip()
        if not otp.isdigit():
            raise forms.ValidationError('OTP must contain only digits.')
        return otp


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Current password'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-input', 'placeholder': 'New password'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Confirm new password'})
