from django.urls import path
from . import views

app_name = "bookings"

urlpatterns = [
    path("movie/<int:movie_id>/showtime/", views.select_showtime, name="select_showtime"),
    path("showtime/<int:showtime_id>/seats/", views.seat_selection, name="seat_selection"),
    path("showtime/<int:showtime_id>/payment/", views.payment, name="payment"),
    path("<str:reference>/confirmation/", views.confirmation, name="confirmation"),
    path("<str:reference>/ticket/", views.ticket, name="ticket"),
    path("my/", views.my_bookings, name="my_bookings"),
]
