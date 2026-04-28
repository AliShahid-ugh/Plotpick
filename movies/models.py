from django.conf import settings
from django.db import models


class Genre(models.Model):
    name = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.name


class Movie(models.Model):
    STATUS_NOW_SHOWING = "now_showing"
    STATUS_COMING_SOON = "coming_soon"
    STATUS_PENDING = "pending"
    STATUS_INACTIVE = "inactive"
    STATUS_CHOICES = [
        (STATUS_NOW_SHOWING, "Now Showing"),
        (STATUS_COMING_SOON, "Coming Soon"),
        (STATUS_PENDING, "Pending"),
        (STATUS_INACTIVE, "Inactive"),
    ]

    BADGE_NONE = ""
    BADGE_TRENDING = "trending"
    BADGE_NEW = "new"
    BADGE_VIP = "vip"
    BADGE_CHOICES = [
        (BADGE_NONE, "None"),
        (BADGE_TRENDING, "Trending"),
        (BADGE_NEW, "New"),
        (BADGE_VIP, "VIP"),
    ]

    title = models.CharField(max_length=200)
    synopsis = models.TextField(blank=True)
    genres = models.ManyToManyField(Genre, related_name="movies", blank=True)
    primary_genre = models.CharField(max_length=40, blank=True)
    runtime_minutes = models.PositiveIntegerField(default=120)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    star_rating = models.PositiveSmallIntegerField(default=4)
    cast = models.CharField(max_length=500, blank=True, help_text="Comma-separated names")
    poster = models.ImageField(upload_to="posters/", blank=True, null=True)
    backdrop = models.ImageField(upload_to="backdrops/", blank=True, null=True)
    release_year = models.PositiveIntegerField(default=2024)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_NOW_SHOWING)
    badge = models.CharField(max_length=16, choices=BADGE_CHOICES, blank=True, default=BADGE_NONE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def cast_list(self):
        return [c.strip() for c in self.cast.split(",") if c.strip()]

    @property
    def is_now_showing(self):
        return self.status == self.STATUS_NOW_SHOWING

    @property
    def is_coming_soon(self):
        return self.status == self.STATUS_COMING_SOON


class Cinema(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name


class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="showtimes")
    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE, related_name="showtimes")
    date = models.DateField()
    time = models.TimeField()
    is_sold_out = models.BooleanField(default=False)

    class Meta:
        ordering = ["date", "time"]

    def __str__(self):
        return f"{self.movie.title} @ {self.cinema.name} {self.date} {self.time.strftime('%I:%M %p')}"


class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    stars = models.PositiveSmallIntegerField(default=5)
    text = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("movie", "user")

    def __str__(self):
        return f"{self.user} → {self.movie} ({self.stars}★)"


class Watchlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="watchlist")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="watchlisted_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "movie")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} ♥ {self.movie}"
