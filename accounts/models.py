from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CUSTOMER = "customer"
    ROLE_ADMIN = "admin"
    ROLE_CHOICES = [
        (ROLE_CUSTOMER, "Customer"),
        (ROLE_ADMIN, "Admin"),
    ]

    full_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default=ROLE_CUSTOMER)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.full_name or self.email

    @property
    def display_name(self):
        if self.full_name:
            return self.full_name.split(" ")[0]
        return self.username or self.email.split("@")[0]

    @property
    def initial(self):
        return self.display_name[:1].upper() if self.display_name else "U"
