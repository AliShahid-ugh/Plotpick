from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login, logout
from django.db.models import Avg, Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from accounts.forms import AdminLoginForm, PasswordChangeForm
from accounts.models import User
from bookings.models import Booking, SeatType, SubscriptionPlan
from movies.models import Movie

from .decorators import admin_required
from .models import SiteSettings


@require_http_methods(["GET", "POST"])
def admin_login(request):
    if request.method == "POST":
        form = AdminLoginForm(request.POST, request=request)
        if form.is_valid():
            login(request, form.user)
            return redirect("adminpanel:dashboard")
    else:
        form = AdminLoginForm()
    return render(request, "admin_panel/login.html", {"form": form})


def admin_logout(request):
    logout(request)
    return redirect("adminpanel:login")


@admin_required
def dashboard(request):
    today = timezone.now().date()
    total_revenue = Booking.objects.aggregate(total=Sum("total"))["total"] or Decimal("0")
    tickets_sold = sum(b.seats.count() for b in Booking.objects.all()) if Booking.objects.exists() else 0
    active_movies = Movie.objects.filter(status=Movie.STATUS_NOW_SHOWING).count()
    users_today = User.objects.filter(date_joined__date=today).count()

    revenue_chart = [
        {"label": "Jan", "value": 6500},
        {"label": "Feb", "value": 9200},
        {"label": "Mar", "value": 4100},
        {"label": "Apr", "value": 14500},
        {"label": "May", "value": 10800},
        {"label": "Jun", "value": 13500},
    ]

    recent_bookings = Booking.objects.select_related("showtime__movie").order_by("-created_at")[:5]

    settings_obj = SiteSettings.load()

    return render(
        request,
        "admin_panel/dashboard.html",
        {
            "active_nav": "dashboard",
            "total_revenue": total_revenue,
            "tickets_sold": tickets_sold,
            "active_movies": active_movies,
            "users_today": users_today,
            "revenue_chart": revenue_chart,
            "recent_bookings": recent_bookings,
            "today": today,
            "budget_allocated": settings_obj.budget_allocated,
            "budget_used": settings_obj.budget_used,
        },
    )


@admin_required
def movies_list(request):
    movies = Movie.objects.all()
    stats = {
        "total": movies.count(),
        "active": movies.filter(status=Movie.STATUS_NOW_SHOWING).count(),
        "genres": Movie.objects.exclude(primary_genre="").values("primary_genre").distinct().count() or 8,
        "avg_rating": round((movies.aggregate(a=Avg("rating"))["a"] or 0), 1),
    }
    return render(
        request,
        "admin_panel/movies.html",
        {
            "active_nav": "movies",
            "movies": movies,
            "stats": stats,
        },
    )


@admin_required
@require_http_methods(["GET", "POST"])
def movies_add(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        genre = request.POST.get("genre", "").strip()
        year = request.POST.get("year", "").strip()
        status = request.POST.get("status", "").strip().lower().replace(" ", "_")
        valid_statuses = {s[0] for s in Movie.STATUS_CHOICES}
        if status not in valid_statuses:
            status = Movie.STATUS_NOW_SHOWING
        if title:
            Movie.objects.create(
                title=title,
                primary_genre=genre,
                release_year=int(year) if year.isdigit() else 2024,
                status=status,
            )
            messages.success(request, f"Added {title}")
            return redirect("adminpanel:movies_add")
        messages.error(request, "Title is required")
    movies = Movie.objects.all()
    return render(
        request,
        "admin_panel/movies_add.html",
        {"active_nav": "movies", "movies": movies, "last_added_minutes": 30},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def movies_edit(request):
    if request.method == "POST":
        old_title = request.POST.get("old_title", "").strip()
        movie = Movie.objects.filter(title__iexact=old_title).first()
        if not movie:
            messages.error(request, f"No movie found with title '{old_title}'")
        else:
            new_title = request.POST.get("new_title", "").strip()
            new_genre = request.POST.get("new_genre", "").strip()
            new_year = request.POST.get("new_year", "").strip()
            new_status = request.POST.get("new_status", "").strip().lower().replace(" ", "_")
            if new_title:
                movie.title = new_title
            if new_genre:
                movie.primary_genre = new_genre
            if new_year.isdigit():
                movie.release_year = int(new_year)
            if new_status in {s[0] for s in Movie.STATUS_CHOICES}:
                movie.status = new_status
            movie.save()
            messages.success(request, f"Updated {movie.title}")
            return redirect("adminpanel:movies_edit")
    return render(
        request,
        "admin_panel/movies_edit.html",
        {"active_nav": "movies", "last_edited_minutes": 3},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def movies_delete(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        movie = Movie.objects.filter(title__iexact=title).first()
        if movie:
            movie.delete()
            messages.success(request, f"Deleted {title}")
        else:
            messages.error(request, f"No movie found with title '{title}'")
        return redirect("adminpanel:movies_delete")
    return render(
        request,
        "admin_panel/movies_delete.html",
        {"active_nav": "movies", "last_deleted_minutes": 30},
    )


@admin_required
def movies_search(request):
    title = request.GET.get("title", "").strip()
    genre = request.GET.get("genre", "").strip()
    movie_id = request.GET.get("id", "").strip()
    year = request.GET.get("year", "").strip()
    status = request.GET.get("status", "").strip().lower().replace(" ", "_")

    qs = Movie.objects.all()
    searched = any([title, genre, movie_id, year, status])
    if title:
        qs = qs.filter(title__icontains=title)
    if genre:
        qs = qs.filter(primary_genre__icontains=genre)
    if movie_id.isdigit():
        qs = qs.filter(pk=int(movie_id))
    if year.isdigit():
        qs = qs.filter(release_year=int(year))
    if status:
        qs = qs.filter(status=status)

    return render(
        request,
        "admin_panel/movies_search.html",
        {
            "active_nav": "movies",
            "movies": qs if searched else Movie.objects.all(),
            "searched": searched,
            "last_deleted_minutes": 30,
        },
    )


@admin_required
def pricing(request):
    plans = SubscriptionPlan.objects.all()
    seat_types = SeatType.objects.all()
    overview = {
        "paid_subscribers": 8260,
        "seats_booked": 3410,
        "avg_seat_revenue": Decimal("14.20"),
        "upgrade_rate": "11.4%",
    }
    return render(
        request,
        "admin_panel/pricing.html",
        {"active_nav": "pricing", "plans": plans, "seat_types": seat_types, "overview": overview},
    )


@admin_required
@require_http_methods(["GET", "POST"])
def pricing_edit(request):
    if request.method == "POST":
        for plan in SubscriptionPlan.objects.all():
            price = request.POST.get(f"plan_{plan.slug}_price")
            trial = request.POST.get(f"plan_{plan.slug}_trial")
            discount = request.POST.get(f"plan_{plan.slug}_discount")
            features = request.POST.get(f"plan_{plan.slug}_features")
            active = request.POST.get(f"plan_{plan.slug}_active") == "on"
            if price is not None:
                try:
                    plan.price = Decimal(price)
                except Exception:
                    pass
            if trial and trial.isdigit():
                plan.trial_days = int(trial)
            if discount and discount.replace(".", "", 1).isdigit():
                plan.cinema_discount_pct = int(float(discount))
            if features is not None:
                plan.features = features
            plan.is_active = active
            plan.save()

        for seat in SeatType.objects.all():
            price = request.POST.get(f"seat_{seat.slug}_price")
            count = request.POST.get(f"seat_{seat.slug}_count")
            desc = request.POST.get(f"seat_{seat.slug}_desc")
            active = request.POST.get(f"seat_{seat.slug}_active") == "on"
            if price:
                try:
                    seat.price = Decimal(price)
                except Exception:
                    pass
            if count and count.isdigit():
                seat.seat_count = int(count)
            if desc is not None:
                seat.description = desc
            seat.is_active = active
            seat.save()
        messages.success(request, "Pricing updated.")
        return redirect("adminpanel:pricing")

    plans = SubscriptionPlan.objects.all()
    seat_types = SeatType.objects.all()
    return render(
        request,
        "admin_panel/pricing_edit.html",
        {"active_nav": "pricing", "plans": plans, "seat_types": seat_types},
    )


@admin_required
def revenue(request):
    total_revenue = Booking.objects.aggregate(total=Sum("total"))["total"] or Decimal("48200")
    total_bookings = Booking.objects.count() or 1247
    top_movie = (
        Booking.objects.values("showtime__movie__title")
        .annotate(n=Count("id"))
        .order_by("-n")
        .first()
    )
    top_movie_title = top_movie["showtime__movie__title"] if top_movie else "Inception"

    monthly = [
        {"label": m, "value": v}
        for m, v in zip(
            ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            [3800, 6200, 5800, 4100, 2900, 1500, 4500, 3200, 6000, 6500, 5400, 6800],
        )
    ]

    breakdown = [
        {"movie": "Inception", "date": "Apr 20", "tickets": 2, "revenue": 24.00, "avg": 12.00},
        {"movie": "Dune II", "date": "Apr 21", "tickets": 3, "revenue": 36.00, "avg": 12.00},
        {"movie": "The Batman", "date": "Apr 22", "tickets": 1, "revenue": 12.00, "avg": 12.00},
        {"movie": "Oppenheimer", "date": "Apr 23", "tickets": 4, "revenue": 48.00, "avg": 12.00},
    ]

    return render(
        request,
        "admin_panel/revenue.html",
        {
            "active_nav": "revenue",
            "total_revenue": total_revenue,
            "total_bookings": total_bookings,
            "top_movie_title": top_movie_title,
            "monthly": monthly,
            "breakdown": breakdown,
        },
    )


@admin_required
@require_http_methods(["GET", "POST"])
def settings_view(request):
    site = SiteSettings.load()
    password_form = PasswordChangeForm(request.user)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "toggle":
            site.enable_email_notifications = request.POST.get("enable_email_notifications") == "on"
            site.maintenance_mode = request.POST.get("maintenance_mode") == "on"
            site.allow_guest_browsing = request.POST.get("allow_guest_browsing") == "on"
            site.save()
            messages.success(request, "Settings saved.")
            return redirect("adminpanel:settings")
        elif action == "password":
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                request.user.set_password(password_form.cleaned_data["new_password"])
                request.user.save()
                return redirect("adminpanel:password_updated")

    return render(
        request,
        "admin_panel/settings.html",
        {
            "active_nav": "settings",
            "site": site,
            "password_form": password_form,
        },
    )


@admin_required
def password_updated(request):
    return render(request, "admin_panel/password_updated.html")
