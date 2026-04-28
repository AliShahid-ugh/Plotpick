from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .models import Genre, Movie, Review, Watchlist


GENRES = ["All", "Action", "Drama", "Horror", "Romance", "Sci-Fi", "Comedy", "Trending"]


def landing(request):
    if request.user.is_authenticated and request.user.role != "admin":
        return redirect("movies:home")
    now_showing = Movie.objects.filter(status=Movie.STATUS_NOW_SHOWING)[:6]
    coming_soon = Movie.objects.filter(status=Movie.STATUS_COMING_SOON)[:6]
    return render(
        request,
        "customer/landing.html",
        {
            "now_showing": now_showing,
            "coming_soon": coming_soon,
            "is_guest": True,
        },
    )


@login_required
def home(request):
    now_showing = Movie.objects.filter(status=Movie.STATUS_NOW_SHOWING)[:6]
    coming_soon = Movie.objects.filter(status=Movie.STATUS_COMING_SOON)[:6]
    recommendations = Movie.objects.filter(badge=Movie.BADGE_TRENDING)[:4]
    watchlist_ids = set(
        Watchlist.objects.filter(user=request.user).values_list("movie_id", flat=True)
    )
    return render(
        request,
        "customer/home.html",
        {
            "now_showing": now_showing,
            "coming_soon": coming_soon,
            "recommendations": recommendations,
            "watchlist_ids": watchlist_ids,
        },
    )


def movie_list(request):
    genre = request.GET.get("genre", "All")
    query = request.GET.get("q", "").strip()

    movies = Movie.objects.exclude(status=Movie.STATUS_INACTIVE)
    if genre and genre != "All":
        if genre == "Trending":
            movies = movies.filter(badge=Movie.BADGE_TRENDING)
        else:
            movies = movies.filter(Q(primary_genre__iexact=genre) | Q(genres__name__iexact=genre)).distinct()
    if query:
        movies = movies.filter(Q(title__icontains=query) | Q(primary_genre__icontains=query))

    watchlist_ids = set()
    if request.user.is_authenticated:
        watchlist_ids = set(
            Watchlist.objects.filter(user=request.user).values_list("movie_id", flat=True)
        )

    return render(
        request,
        "customer/movie_list.html",
        {
            "movies": movies,
            "genres": GENRES,
            "active_genre": genre,
            "search_query": query,
            "watchlist_ids": watchlist_ids,
            "is_guest": not request.user.is_authenticated,
        },
    )


def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    showtimes = movie.showtimes.all()[:12]
    reviews = movie.reviews.select_related("user")[:10]

    in_watchlist = False
    user_review = None
    if request.user.is_authenticated:
        in_watchlist = Watchlist.objects.filter(user=request.user, movie=movie).exists()
        user_review = movie.reviews.filter(user=request.user).first()

    return render(
        request,
        "customer/movie_detail.html",
        {
            "movie": movie,
            "showtimes": showtimes,
            "reviews": reviews,
            "in_watchlist": in_watchlist,
            "user_review": user_review,
            "is_guest": not request.user.is_authenticated,
        },
    )


@login_required
@require_POST
def toggle_watchlist(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    item, created = Watchlist.objects.get_or_create(user=request.user, movie=movie)
    if not created:
        item.delete()
        messages.info(request, f"Removed {movie.title} from your watchlist.")
    else:
        messages.success(request, f"Added {movie.title} to your watchlist.")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", reverse("movies:detail", args=[pk])))


@login_required
@require_POST
def submit_review(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    stars = int(request.POST.get("stars", 5))
    text = request.POST.get("text", "").strip()
    stars = max(1, min(5, stars))

    review, _ = Review.objects.update_or_create(
        movie=movie,
        user=request.user,
        defaults={"stars": stars, "text": text[:500]},
    )
    messages.success(request, "Thanks for your review!")
    return redirect("movies:detail", pk=pk)


@login_required
def watchlist(request):
    items = Watchlist.objects.filter(user=request.user).select_related("movie")
    return render(request, "customer/watchlist.html", {"items": items})


@login_required
def profile(request):
    review_count = Review.objects.filter(user=request.user).count()
    booking_count = request.user.bookings.count() if hasattr(request.user, "bookings") else 0
    watchlist_count = Watchlist.objects.filter(user=request.user).count()
    return render(
        request,
        "customer/profile.html",
        {
            "review_count": review_count,
            "booking_count": booking_count,
            "watchlist_count": watchlist_count,
        },
    )
