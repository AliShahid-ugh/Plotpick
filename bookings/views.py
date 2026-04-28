import secrets
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from movies.models import Cinema, Movie, Showtime

from .models import Booking, Seat, SeatType


def _generate_reference():
    return "PP-" + secrets.token_hex(4).upper()


@login_required
def select_showtime(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    cinemas = Cinema.objects.all()
    showtimes = movie.showtimes.select_related("cinema").all()

    dates = sorted({st.date for st in showtimes})
    selected_date = request.GET.get("date")
    selected_cinema = request.GET.get("cinema")

    filtered = showtimes
    if selected_cinema:
        filtered = filtered.filter(cinema_id=selected_cinema)
    if selected_date:
        filtered = filtered.filter(date=selected_date)

    return render(
        request,
        "customer/select_showtime.html",
        {
            "movie": movie,
            "cinemas": cinemas,
            "dates": dates,
            "showtimes": filtered,
            "selected_date": selected_date,
            "selected_cinema": int(selected_cinema) if selected_cinema else None,
        },
    )


@login_required
def seat_selection(request, showtime_id):
    showtime = get_object_or_404(Showtime.objects.select_related("movie", "cinema"), pk=showtime_id)
    seats = list(showtime.seats.all().order_by("row", "number"))

    # Group by row for template rendering
    rows = {}
    for seat in seats:
        rows.setdefault(seat.row, []).append(seat)
    row_data = [{"label": r, "seats": sorted(s, key=lambda x: x.number)} for r, s in sorted(rows.items())]

    return render(
        request,
        "customer/seat_selection.html",
        {
            "showtime": showtime,
            "movie": showtime.movie,
            "row_data": row_data,
        },
    )


@login_required
@require_POST
def payment(request, showtime_id):
    showtime = get_object_or_404(Showtime.objects.select_related("movie", "cinema"), pk=showtime_id)
    seat_ids = request.POST.getlist("seats")
    if not seat_ids:
        messages.error(request, "Please select at least one seat.")
        return redirect("bookings:seat_selection", showtime_id=showtime_id)

    seats = list(Seat.objects.filter(pk__in=seat_ids, showtime=showtime, is_reserved=False))
    if len(seats) != len(seat_ids):
        messages.error(request, "One or more seats are no longer available.")
        return redirect("bookings:seat_selection", showtime_id=showtime_id)

    subtotal = sum((s.price for s in seats), Decimal("0"))
    discount = Decimal("0")
    total = subtotal - discount

    if request.POST.get("confirm") == "1":
        with transaction.atomic():
            booking = Booking.objects.create(
                user=request.user,
                showtime=showtime,
                subtotal=subtotal,
                discount=discount,
                total=total,
                reference=_generate_reference(),
                status=Booking.STATUS_UPCOMING,
            )
            booking.seats.set(seats)
            Seat.objects.filter(pk__in=[s.pk for s in seats]).update(is_reserved=True)
        messages.success(request, "Payment successful! Your booking is confirmed.")
        return redirect("bookings:confirmation", reference=booking.reference)

    return render(
        request,
        "customer/payment.html",
        {
            "showtime": showtime,
            "movie": showtime.movie,
            "seats": seats,
            "subtotal": subtotal,
            "discount": discount,
            "total": total,
        },
    )


@login_required
def confirmation(request, reference):
    booking = get_object_or_404(Booking, reference=reference, user=request.user)
    return render(request, "customer/confirmation.html", {"booking": booking})


@login_required
def ticket(request, reference):
    booking = get_object_or_404(Booking, reference=reference, user=request.user)
    return render(request, "customer/ticket.html", {"booking": booking})


@login_required
def my_bookings(request):
    tab = request.GET.get("tab", "upcoming")
    qs = Booking.objects.filter(user=request.user).select_related("showtime__movie", "showtime__cinema")
    if tab == "past":
        bookings = qs.filter(status=Booking.STATUS_PAST)
    elif tab == "cancelled":
        bookings = qs.filter(status=Booking.STATUS_CANCELLED)
    else:
        bookings = qs.filter(status=Booking.STATUS_UPCOMING)
    return render(
        request,
        "customer/my_bookings.html",
        {"bookings": bookings, "active_tab": tab},
    )
