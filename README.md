# PlotPick

> The Plot You Love, The Seat You Want.

A full-stack movie ticket booking and streaming platform built with Django + SQLite. Frontend is vanilla HTML/CSS/JS styled to match the PlotPick Figma design system (dark theme, `#E63946` accent, Montserrat + Inter typography).

## Tech stack

- **Backend:** Django 4.x (Python)
- **Database:** SQLite (Django default)
- **Frontend:** Django templates, HTML, CSS (vanilla, no framework), JavaScript
- **Version control:** Git / GitHub
- **Project management:** Jira

## Feature summary

### Customer-facing site
- Landing page (guest) with hero, Now Showing / Coming Soon, How It Works
- Login, Register (with password strength meter), Forgot Password
- Movie Listing with search + genre filter chips
- Movie Detail with synopsis, cast, showtimes, reviews, watchlist toggle
- Select Showtime (date strip + time chips + cinema dropdown)
- Seat Selection (live grid with Regular / Premium / VIP, reserved seats)
- Payment / Checkout with order summary
- Booking confirmation + downloadable ticket
- My Bookings (Upcoming / Past / Cancelled tabs)
- Watchlist
- Profile

### Admin panel (`/admin-panel/`)
- Admin login (separate from Django's built-in admin)
- Dashboard — stats, revenue chart, budget, recent bookings, quick actions
- Movies — list, add, edit, delete, search (breadcrumbed workflow)
- Pricing — streaming subscription plans + cinema seat pricing + edit mode
- Revenue — date filter, monthly bar chart, detailed breakdown
- Settings — profile card, change password, system toggles

## Quick start

```bash
# 1. Install Python 3.10+ if you don't have it
#    Windows:  https://www.python.org/downloads/  (check "Add Python to PATH")

# 2. Create a virtual environment
python -m venv venv

# 3. Activate it
#    Windows (PowerShell):
venv\Scripts\activate
#    Windows (Git Bash):
source venv/Scripts/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run migrations
python manage.py makemigrations
python manage.py migrate

# 6. Seed sample data (movies, cinemas, showtimes, seats, admin user)
python manage.py seed

# 7. Start the dev server
python manage.py runserver
```

Then open:
- Customer site: http://127.0.0.1:8000/
- Admin panel: http://127.0.0.1:8000/admin-panel/login/
- Django built-in admin: http://127.0.0.1:8000/django-admin/

## Seeded credentials

| Role     | Email                  | Password    |
|----------|------------------------|-------------|
| Admin    | admin@plotpick.com     | admin123    |
| Customer | aliza@plotpick.com     | demo12345   |

## Project structure

```
plotpick/            # Django project
accounts/            # User model + auth flows
movies/              # Movie, Genre, Cinema, Showtime, Review, Watchlist
bookings/            # Booking, Seat, SeatType, SubscriptionPlan
adminpanel/          # Admin dashboard views + site settings
templates/           # All HTML templates
static/
  css/               # styles.css (customer) + admin.css
  js/                # main.js
```

## Design reference

Frontend mirrors the Figma frames in `PlotPick SDA Project BSCS 4C_phase 2 -3.pdf` (customer) and `PlotPick SDA Project BSCS 4C-phase4-5.pdf` (admin). Design tokens live at the top of `static/css/styles.css`.
