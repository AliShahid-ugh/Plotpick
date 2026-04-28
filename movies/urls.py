from django.urls import path
from . import views

app_name = "movies"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("home/", views.home, name="home"),
    path("movies/", views.movie_list, name="list"),
    path("movies/<int:pk>/", views.movie_detail, name="detail"),
    path("movies/<int:pk>/watchlist/toggle/", views.toggle_watchlist, name="toggle_watchlist"),
    path("movies/<int:pk>/review/", views.submit_review, name="submit_review"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("profile/", views.profile, name="profile"),
]
