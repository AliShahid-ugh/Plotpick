from django.contrib import admin

from .models import Cinema, Genre, Movie, Review, Showtime, Watchlist


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "primary_genre", "release_year", "status", "rating")
    list_filter = ("status", "primary_genre")
    search_fields = ("title", "cast")
    filter_horizontal = ("genres",)


admin.site.register(Genre)
admin.site.register(Cinema)
admin.site.register(Showtime)
admin.site.register(Review)
admin.site.register(Watchlist)
