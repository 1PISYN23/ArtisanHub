from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Shop(models.Model):
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shop"
    )
    slug = models.SlugField(max_length=84, unique=True, allow_unicode=True)
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(max_length=528, blank=True)
    logo = models.ImageField(upload_to="shop_logos/", blank=True, null=True)

    stripe_account_id = models.CharField(max_length=255, blank=True)
    stripe_onboarding_complete = models.BooleanField(default=False)

    rating_cached = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    reviews_count_cached = models.PositiveBigIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = "Магазины"


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)
        

    def __str__(self):
        return f"{self.name} - {self.owner}"
    

