# LocalServe — Setup Guide

## 1. Requirements

```bash
pip install -r requirements.txt
```

## 2. Create `.env` file

```
SECRET_KEY=your-very-long-random-secret-key-here
DEBUG=True
DB_NAME=localservice_db
DB_USER=root
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=3306
ANTHROPIC_API_KEY=your-anthropic-key-here
```

Generate a secret key:
```python
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

## 3. Create MySQL Database

```sql
CREATE DATABASE localservice_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 4. Run Migrations

```bash
python manage.py migrate
```

## 5. Create Admin Account (YOU ONLY — no one else can be admin)

```bash
python create_admin.py
```
- Enter your chosen username, email, and password
- **Only you can do this** — admin cannot be created via website registration

## 6. Seed Demo Data (Optional — for testing)

```bash
python seed.py
```
This creates 8 categories, 5 providers, 5 customers, 20+ services, and reviews.

To clear and re-seed:
```bash
python seed.py --clear
```

## 7. Run the Server

```bash
python manage.py runserver
```

Visit: http://localhost:8000

---

## Key URLs

| URL | Purpose |
|-----|---------|
| `/` | Home page |
| `/users/login/` | Login |
| `/users/register/` | Register (customer or provider only) |
| `/adminpanel/` | Admin dashboard (admin only) |
| `/users/profile/` | Your profile |
| `/services/` | Browse services |
| `/search/` | Search services |
| `/ai-recommend/` | AI recommendations |

---

## New Features in This Version

### ✅ Fixed
- Categories now show correctly (run seed.py)
- Admin login works (run create_admin.py)
- Admin cannot be registered via website — only via create_admin.py

### ✨ New Features
- **Country code picker** on all phone fields (20+ countries)
- **Language switcher** — English / Hindi (Profile → Settings)
- **Profile tabs** — Overview, Activity, Security, Account Settings
- **Password change** page at `/users/profile/password/`
- **Profile dropdown menu** in navbar (click your username)
- **Contact buttons** — WhatsApp, Call, Email on provider profiles
- **View count** — now excludes admin views (only real customer views counted)
- **Admin registration blocked** — form rejects admin role

---

## Notes on Phone Numbers
- Enter country code from dropdown (e.g., +91 for India)
- Enter number WITHOUT country code (e.g., `9876543210`)
- System stores full number (e.g., `+919876543210`)
- WhatsApp links use this full number automatically
