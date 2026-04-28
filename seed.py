#!/usr/bin/env python
"""
seed.py — Populate LocalServe with realistic demo data.

Usage:
    python seed.py
    python seed.py --clear   # Clear existing data first

Creates:
  - 8 service categories
  - 1 admin user
  - 5 provider users
  - 5 customer users
  - 20+ services
  - 30+ reviews
"""
import os
import sys
import django
import random
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'localservice.settings')
django.setup()

from users.models import CustomUser
from services.models import Service, Category
from reviews.models import Review

CLEAR = '--clear' in sys.argv

# ── Data ──────────────────────────────────────────────────────────────────────

CATEGORIES = [
    ('Electrical', '', 'Wiring, repairs, installation, and electrical safety'),
    ('Plumbing', '', 'Pipe fitting, leaks, drainage, and water systems'),
    ('Carpentry', '', 'Furniture, woodwork, doors, and custom builds'),
    ('Cleaning', '', 'Deep cleaning, housekeeping, and sanitisation'),
    ('Tutoring', '', 'Academic help, coaching, and skill development'),
    ('Beauty & Wellness', '', 'Salon, spa, massage, and grooming at home'),
    ('Transportation', '', 'Driver, delivery, logistics, and moving services'),
    ('AC & Appliance', '', 'Air conditioning, refrigerators, and appliance repair'),
]

CITIES = [
    'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai',
    'Pune', 'Kolkata', 'Jaipur', 'Ahmedabad', 'Lucknow', 'Patna',
]

PROVIDERS = [
    ('rajesh_electric', 'Rajesh Kumar', 'rajesh@example.com', 'Mumbai'),
    ('priya_clean', 'Priya Sharma', 'priya@example.com', 'Delhi'),
    ('amit_carpenter', 'Amit Singh', 'amit@example.com', 'Bangalore'),
    ('sunita_tutor', 'Sunita Devi', 'sunita@example.com', 'Hyderabad'),
    ('mohan_ac', 'Mohan Patel', 'mohan@example.com', 'Pune'),
]

CUSTOMERS = [
    ('arun_kumar', 'Arun Kumar', 'arun@example.com'),
    ('meena_s', 'Meena Sharma', 'meena@example.com'),
    ('vikram_j', 'Vikram Joshi', 'vikram@example.com'),
    ('deepa_m', 'Deepa Mehta', 'deepa@example.com'),
    ('ravi_t', 'Ravi Tiwari', 'ravi@example.com'),
]

SERVICES_DATA = [
    ('Full Home Electrical Wiring', 'Electrical', 'Complete new home wiring, switchboard installation, earthing and safety checks. 15+ years experience. Licensed electrician.', 5000, 'fixed', 'Mumbai', True),
    ('Emergency Electrical Repair', 'Electrical', 'Fast 24/7 emergency electrical repairs. Short circuit, tripping, power failures fixed within 2 hours.', 800, 'fixed', 'Delhi', False),
    ('Solar Panel Installation', 'Electrical', 'Grid-tied and off-grid solar panel installation. Subsidy assistance, net metering setup, and annual maintenance contracts available.', 45000, 'fixed', 'Bangalore', True),
    ('Kitchen & Bathroom Plumbing', 'Plumbing', 'Complete plumbing solutions for kitchen and bathroom. Pipe replacement, tap fitting, shower installation.', 1200, 'fixed', 'Hyderabad', False),
    ('Drainage Unclogging', 'Plumbing', 'Blocked drain? We clear blockages using professional equipment. Same-day service available in city limits.', 500, 'fixed', 'Mumbai', False),
    ('Water Heater Installation', 'Plumbing', 'Geyser and water heater installation, repair, and replacement. All brands. ISI certified technician.', 700, 'fixed', 'Pune', False),
    ('Custom Furniture Design', 'Carpentry', 'Modular kitchen, wardrobes, beds, study tables — custom built to your exact specifications using premium wood.', 15000, 'negotiable', 'Bangalore', True),
    ('Door Frame Repair', 'Carpentry', 'Broken door, stuck hinges, damaged frames — quick and neat repairs. Residential and commercial.', 600, 'fixed', 'Chennai', False),
    ('Deep Home Cleaning', 'Cleaning', 'Full home deep cleaning: scrubbing, sanitising, kitchen degreasing, bathroom descaling. Eco-friendly products.', 2500, 'fixed', 'Mumbai', True),
    ('Office Cleaning Service', 'Cleaning', 'Regular or one-time office cleaning. Flexible schedule — before-hours or after-hours service available.', 1800, 'fixed', 'Delhi', False),
    ('Post-Construction Cleaning', 'Cleaning', 'Specialized cleaning after renovation or construction. Paint removal, dust elimination, floor polishing.', 4000, 'fixed', 'Pune', False),
    ('CBSE Maths Tutor (6-12)', 'Tutoring', 'Experienced CBSE Maths tutor. Classes 6-12, including board exam preparation. Home visits or online sessions.', 500, 'hourly', 'Hyderabad', True),
    ('English Communication Coach', 'Tutoring', 'Improve spoken and written English. Corporate professionals, students, IELTS/TOEFL preparation.', 600, 'hourly', 'Bangalore', False),
    ('JEE/NEET Physics Coaching', 'Tutoring', 'Expert JEE and NEET Physics coaching. Small batches (max 5 students). Proven results.', 800, 'hourly', 'Jaipur', True),
    ('Home Spa & Massage', 'Beauty & Wellness', 'Professional spa treatment at your home. Swedish massage, deep tissue, aromatherapy. Certified therapist.', 1500, 'fixed', 'Mumbai', True),
    ('Bridal Makeup Artist', 'Beauty & Wellness', 'Experienced bridal makeup artist. HD makeup, airbrush. Includes trial session. Packages available.', 8000, 'fixed', 'Delhi', True),
    ('Haircut & Grooming at Home', 'Beauty & Wellness', 'Professional hair cutting and styling at your doorstep. Saves salon time. Men, women, and kids.', 400, 'fixed', 'Chennai', False),
    ('Airport & Outstation Driver', 'Transportation', 'Reliable, punctual driver for airport drops, outstation trips. AC vehicle, experienced on highways.', 1200, 'daily', 'Mumbai', False),
    ('Goods Transport & Moving', 'Transportation', 'Home and office shifting service. Packing, loading, unloading, unpacking. Insured goods.', 3500, 'fixed', 'Bangalore', False),
    ('AC Service & Repair', 'AC & Appliance', 'Split and window AC servicing, gas filling, repair, and installation. All brands. AMC available.', 700, 'fixed', 'Mumbai', True),
    ('Refrigerator Repair', 'AC & Appliance', 'Fridge not cooling? Compressor issues, gas leaks, thermostat problems — all fixed same day.', 600, 'fixed', 'Hyderabad', False),
    ('Washing Machine Repair', 'AC & Appliance', 'Front load, top load washing machine repairs. Drum bearing, motor, PCB issues fixed.', 550, 'fixed', 'Pune', False),
]

REVIEW_COMMENTS = [
    ("Excellent work!", "Very professional and completed the job on time. Highly recommend!", 5),
    ("Great service", "Showed up on time, did a clean job. Will hire again.", 5),
    ("Good overall", "Did the work well but took a little longer than expected.", 4),
    ("Satisfied", "Decent service for the price. Nothing extraordinary but got the job done.", 3),
    ("Very knowledgeable", "Explained everything clearly and gave useful advice. Worth every rupee.", 5),
    ("Quick and efficient", "Fixed the issue in under an hour. Very efficient.", 5),
    ("Professional attitude", "Polite, professional, and cleaned up after the work. 5 stars.", 5),
    ("Reasonable pricing", "Fair price and good quality. Would recommend to friends.", 4),
    ("Needs improvement", "Work was okay but communication could be better.", 3),
    ("Outstanding!", "Went above and beyond. The best I've hired for this type of work.", 5),
]


def run():
    if CLEAR:
        print('🗑️  Clearing existing data...')
        Review.objects.all().delete()
        Service.objects.all().delete()
        Category.objects.all().delete()
        CustomUser.objects.filter(is_superuser=False).delete()
        print('   Done.\n')

    # Categories
    print('📁 Creating categories...')
    cats = {}
    for name, icon, desc in CATEGORIES:
        cat, _ = Category.objects.get_or_create(name=name, defaults={'icon': icon, 'description': desc})
        cats[name] = cat
        print(f'   {icon} {name}')

    # Admin
    print('\n👑 Creating admin...')
    if not CustomUser.objects.filter(username='admin').exists():
        CustomUser.objects.create_superuser(
            username='admin', email='admin@localserve.com',
            password='Admin@123', role='admin', is_verified=True,
            city='Mumbai'
        )
        print('   admin / Admin@123')
    else:
        print('   admin already exists')

    # Providers
    print('\n🔧 Creating providers...')
    providers = []
    for uname, fullname, email, city in PROVIDERS:
        first, *last = fullname.split()
        phone_num = f'9{random.randint(100000000, 999999999)}'
        user, created = CustomUser.objects.get_or_create(
            username=uname,
            defaults={
                'email': email, 'role': 'provider',
                'first_name': first, 'last_name': ' '.join(last),
                'city': city, 'is_verified': True,
                'phone': f'+91{phone_num}',
                'phone_country_code': '+91',
                'whatsapp_no': f'+91{phone_num}',
                'whatsapp_country_code': '+91',
                'phone_verified': True,
                'bio': f'Experienced professional with over {random.randint(5,20)} years of service. Available in {city} and nearby areas.',
            }
        )
        if created:
            user.set_password('Provider@123')
            user.save()
        providers.append(user)
        print(f'   {uname} / Provider@123')

    # Customers
    print('\n🛒 Creating customers...')
    customers = []
    for uname, fullname, email in CUSTOMERS:
        first, *last = fullname.split()
        user, created = CustomUser.objects.get_or_create(
            username=uname,
            defaults={
                'email': email, 'role': 'customer',
                'first_name': first, 'last_name': ' '.join(last),
                'city': random.choice(CITIES),
            }
        )
        if created:
            user.set_password('Customer@123')
            user.save()
        customers.append(user)
        print(f'   {uname} / Customer@123')

    # Services
    print('\n🔧 Creating services...')
    services = []
    provider_idx = 0
    for title, cat_name, desc, price, price_type, city, is_featured in SERVICES_DATA:
        provider = providers[provider_idx % len(providers)]
        provider_idx += 1
        cat = cats.get(cat_name)
        if not cat:
            continue
        svc, created = Service.objects.get_or_create(
            title=title,
            defaults={
                'provider': provider,
                'category': cat,
                'description': desc,
                'price': Decimal(price),
                'price_type': price_type,
                'city': city,
                'state': random.choice(['Maharashtra', 'Delhi', 'Karnataka', 'Telangana', 'Rajasthan']),
                'phone': provider.phone or f'+91 9{random.randint(100000000, 999999999)}',
                'email': provider.email,
                'is_active': True,
                'is_featured': is_featured,
                'views_count': random.randint(5, 280),
            }
        )
        if created:
            services.append(svc)
            print(f'   ✓ {title[:50]}')

    # Reviews
    print('\n⭐ Creating reviews...')
    review_count = 0
    for service in services:
        num_reviews = random.randint(0, min(len(customers), 4))
        reviewers = random.sample(customers, num_reviews)
        for customer in reviewers:
            if Review.objects.filter(service=service, reviewer=customer).exists():
                continue
            title_r, comment, rating = random.choice(REVIEW_COMMENTS)
            # Small random variation in rating
            actual_rating = max(1, min(5, rating + random.choice([-1, 0, 0, 0, 1])))
            Review.objects.create(
                service=service,
                reviewer=customer,
                rating=actual_rating,
                title=title_r,
                comment=comment,
                is_verified=random.choice([True, False]),
            )
            review_count += 1

    print(f'\n✅ Seed complete!')
    print(f'   Categories : {Category.objects.count()}')
    print(f'   Users      : {CustomUser.objects.count()} total')
    print(f'   Services   : {Service.objects.count()}')
    print(f'   Reviews    : {Review.objects.count()}')
    print(f'\n🔑 Login credentials:')
    print(f'   Admin    → admin / Admin@123       → /adminpanel/')
    print(f'   Provider → rajesh_electric / Provider@123')
    print(f'   Customer → arun_kumar / Customer@123')
    print(f'\n🌐 Start server: python manage.py runserver')


if __name__ == '__main__':
    run()
