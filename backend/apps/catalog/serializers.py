from rest_framework import serializers
from .models import Catalog


class CatalogSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Catalog
        fields = ("id", "name", "slug", "parent", "image", "priority", "created_at", "updated_at")
        read_only_fields = ("id", "name", "slug", "image", "priority", "created_at", "updated_at")


    def get_image(self, obj):
        if obj.image:
            request = self.context.get("request")
            if request:
                try:
                    url = request.build_absolute_uri(obj.image.url)
                    from django.conf import settings
                    force_https_domains = getattr(settings, "FORCE_HTTPS_DOMAINS", [])
                    if force_https_domains and any(domain in url for domain in force_https_domains):
                        url = url.replace("http://", "https://", 1)
                    return url
                except Exception as e:
                    scheme = "https" if request.is_secure() else "http"
                    host = request.get_host()
                    return f"{scheme}://{host}{obj.image.url}"
            from django.conf import settings
            base_url = getattr(settings, "BASE_URL", "http://localhost:8000")
            return f"{base_url.rstrip("/")}{obj.image.url}"
        return None
            