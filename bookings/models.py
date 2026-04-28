from decimal import Decimal

from django.conf import settings
from django.db import models

from movies.models import Showtime


class SeatType(models.Model):
    TYPE_STANDARD = "standard"
    TYPE_PREMIUM = "premium"
    TYPE_VIP = "vip"
    TYPE_COUPLES = "couples"
    TYPE_CHOICES = [
        (TYPE_STANDARD, "Standard"),
        (TYPE_PREMIUM, "Premium"),
        (TYPE_VIP, "VIP Recliner"),
        (TYPE_COUPLES, "Couples Pod"),
    ]

    STOCK_AVAILABLE = "available"
    STOCK_LIMITED = "limited"
    STOCK_LOW = "low"
    STOCK_CHOICES = [
        (STOCK_AVAILABLE, "Available"),
        (STOCK_LIMITED, "Limited"),
        (STOCK_LOW, "Low Stock"),
    ]

    slug = models.CharField(max_length=32, choices=TYPE_CHOICES, unique=True)
    display_name = models.CharField(max_length=50)
    description = models.CharField(max_length=200, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    seat_count = models.PositiveIntegerField(default=24)
    stock_status = models.CharField(max_length=16, choices=STOCK_CHOICES, default=STOCK_AVAILABLE)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["price"]

    def __str__(self):
        return f"{self.display_name} (${self.price})"


class SubscriptionPlan(models.Model):
    NAME_FREE = "free"
    NAME_STANDARD = "standard"
    NAME_PREMIUM = "premium"
    NAME_CHOICES = [
        (NAME_FREE, "Free"),
        (NAME_STANDARD, "Standard"),
        (NAME_PREMIUM, "Premium"),
    ]

    slug = models.CharField(max_length=16, choices=NAME_CHOICES, unique=True)
    display_name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    trial_days = models.PositiveIntegerField(default=0)
    cinema_discount_pct = models.PositiveIntegerField(default=0)
    features = models.CharField(max_length=200, blank=True)
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["price"]

    def __str__(self):
        return self.display_name


class Seat(models.Model):
    CATEGORY_REGULAR = "regular"
    CATEGORY_PREMIUM = "premium"
    CATEGORY_VIP = "vip"
    CATEGORY_CHOICES = [
        (CATEGORY_REGULAR, "Regular"),
        (CATEGORY_PREMIUM, "Premium"),
        (CATEGORY_VIP, "VIP"),
    ]

    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE, related_name="seats")
    row = models.CharField(max_length=2)
    number = models.PositiveIntegerField()
    category = models.CharField(max_length=16, choices=CATEGORY_CHOICES, default=CATEGORY_REGULAR)
    is_reserved = models.BooleanField(default=False)

    class Meta:
        unique_together = ("showtime", "row", "number")
        ordering = ["row", "number"]

    def __str__(self):
        return f"{self.row}{self.number} ({self.get_category_display()})"

    @property
    def label(self):
        return f"{self.row}-{self.number}"

    @property
    def price(self):
        prices = {
            Seat.CATEGORY_REGULAR: Decimal("8.00"),
            Seat.CATEGORY_PREMIUM: Decimal("13.00"),
            Seat.CATEGORY_VIP: Decimal("22.00"),
        }
        return prices.get(self.category, Decimal("8.00"))


class Booking(models.Model):
    STATUS_UPCOMING = "upcoming"
    STATUS_PAST = "past"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_UPCOMING, "Upcoming"),
        (STATUS_PAST, "Past"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    showtime = models.ForeignKey(Showtime, on_delete=models.PROTECT, related_name="bookings")
    seats = models.ManyToManyField(Seat, related_name="bookings")
    subtotal = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_UPCOMING)
    reference = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reference} — {self.user} — {self.showtime}"

    @property
    def seat_labels(self):
        return ", ".join(s.label for s in self.seats.all())
