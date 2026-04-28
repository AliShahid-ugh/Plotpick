from functools import wraps

from django.http import HttpResponseRedirect
from django.urls import reverse


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return HttpResponseRedirect(reverse("adminpanel:login"))
        if not (user.is_staff or getattr(user, "role", "") == "admin"):
            return HttpResponseRedirect(reverse("adminpanel:login"))
        return view_func(request, *args, **kwargs)

    return _wrapped
