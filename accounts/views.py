from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .forms import ForgotPasswordForm, LoginForm, RegisterForm


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect("movies:home")

    if request.method == "POST":
        form = LoginForm(request.POST, request=request)
        if form.is_valid():
            login(request, form.user)
            messages.success(request, "Welcome back!")
            next_url = request.GET.get("next") or request.POST.get("next")
            return redirect(next_url or reverse("movies:home"))
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})


@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.user.is_authenticated:
        return redirect("movies:home")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created. Welcome to PlotPick!")
            return redirect("movies:home")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


@require_http_methods(["GET", "POST"])
def forgot_password_view(request):
    sent = False
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            sent = True
    else:
        form = ForgotPasswordForm()
    return render(request, "accounts/forgot_password.html", {"form": form, "sent": sent})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("movies:landing")
