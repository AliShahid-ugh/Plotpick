from django.urls import path
from . import views

app_name = "adminpanel"

urlpatterns = [
    path("login/", views.admin_login, name="login"),
    path("logout/", views.admin_logout, name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("movies/", views.movies_list, name="movies"),
    path("movies/add/", views.movies_add, name="movies_add"),
    path("movies/edit/", views.movies_edit, name="movies_edit"),
    path("movies/delete/", views.movies_delete, name="movies_delete"),
    path("movies/search/", views.movies_search, name="movies_search"),
    path("pricing/", views.pricing, name="pricing"),
    path("pricing/edit/", views.pricing_edit, name="pricing_edit"),
    path("revenue/", views.revenue, name="revenue"),
    path("settings/", views.settings_view, name="settings"),
    path("settings/password/", views.password_updated, name="password_updated"),
]
