from django.db import models
from django.utils.text import slugify


class Catalog(models.Model):
    name = models.CharField(max_length=64, verbose_name="Название")
    slug = models.SlugField(max_length=64, unique=True, allow_unicode=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="children", blank=True, null=True)
    image = models.ImageField(upload_to="catalog/images/", blank=True, null=True)
    priority = models.IntegerField(default=0, verbose_name="Приоритет")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = "Элемент каталога"
        verbose_name_plural = "Элементы каталога"
        ordering = ["-priority", "name"]


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


    def __str__(self):
        return self.name