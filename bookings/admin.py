from django.contrib import admin

from .models import Booking, Seat, SeatType, SubscriptionPlan


admin.site.register(SeatType)
admin.site.register(SubscriptionPlan)
admin.site.register(Seat)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("reference", "user", "showtime", "total", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("reference", "user__email")
