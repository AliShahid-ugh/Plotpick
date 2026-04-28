from django.db import models


class SiteSettings(models.Model):
    enable_email_notifications = models.BooleanField(default=True)
    maintenance_mode = models.BooleanField(default=False)
    allow_guest_browsing = models.BooleanField(default=True)
    budget_allocated = models.DecimalField(max_digits=12, decimal_places=2, default=50000)
    budget_used = models.DecimalField(max_digits=12, decimal_places=2, default=38200)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Site Settings"

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
