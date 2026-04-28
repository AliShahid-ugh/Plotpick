from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("", include("movies.urls", namespace="movies")),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("bookings/", include("bookings.urls", namespace="bookings")),
    path("admin-panel/", include("adminpanel.urls", namespace="adminpanel")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
