#!/usr/bin/env python
"""
create_admin.py — Create THE admin account for LocalServe.
Only ONE admin can exist. Admin cannot self-register.

Usage:
    python create_admin.py

Or with env vars:
    ADMIN_USER=admin ADMIN_PASS=yourpassword ADMIN_EMAIL=admin@example.com python create_admin.py
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'localservice.settings')
django.setup()

from users.models import CustomUser


def create_admin():
    # Check if admin already exists
    existing_admin = CustomUser.objects.filter(role='admin').first()
    if existing_admin:
        print(f'⚠️  Admin user "{existing_admin.username}" already exists.')
        overwrite = input('Update password and re-confirm as admin? [y/N]: ').strip().lower()
        if overwrite != 'y':
            print('Aborted. Admin already set up.')
            return
        # Update existing admin
        username = existing_admin.username
        email = existing_admin.email
        user = existing_admin
    else:
        username = os.environ.get('ADMIN_USER') or input('Admin username [admin]: ').strip() or 'admin'
        email = os.environ.get('ADMIN_EMAIL') or input('Admin email [admin@localserve.com]: ').strip() or 'admin@localserve.com'
        user = None

    if os.environ.get('ADMIN_PASS'):
        password = os.environ['ADMIN_PASS']
    else:
        import getpass
        password = getpass.getpass('Admin password (min 8 chars): ')
        confirm  = getpass.getpass('Confirm password: ')
        if password != confirm:
            print('❌ Passwords do not match.')
            sys.exit(1)
        if len(password) < 8:
            print('❌ Password must be at least 8 characters.')
            sys.exit(1)

    if user:
        user.set_password(password)
        user.role = 'admin'
        user.is_staff = True
        user.is_superuser = True
        user.is_verified = True
        user.is_active = True
        user.save()
        print(f'✅ Admin user "{user.username}" updated successfully.')
    else:
        if CustomUser.objects.filter(username=username).exists():
            print(f'❌ Username "{username}" already taken. Choose a different one.')
            sys.exit(1)
        user = CustomUser.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            role='admin',
            is_verified=True,
        )
        print(f'✅ Admin user "{username}" created successfully!')

    print(f'   Email:    {user.email}')
    print(f'   Username: {user.username}')
    print(f'   Role:     {user.role}')
    print()
    print(f'   🔑 Login URL:  http://localhost:8000/users/login/')
    print(f'   🛠  Admin panel: http://localhost:8000/adminpanel/')
    print()
    print('⚠️  Keep this login secret. Admin cannot be self-registered.')


if __name__ == '__main__':
    create_admin()
