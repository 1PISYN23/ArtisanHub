from rest_framework import serializers
from django.conf import settings
from django.utils.text import slugify
from .models import Shop


class ShopDetailSerizlier(serializers.ModelSerializer): 

    class Meta:
        model = Shop
        fields = ("id", "name", "slug", 
                  "description", "logo", "rating_cached", 
                  "reviews_count_cached", "created_at", "updated_at")
        read_only_fields = (
            "id", "slug", "rating_cached", "reviews_count_cached", 
            "created_at", "updated_at"
        )

class ShopListSerializer(ShopDetailSerizlier):

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if len(data["description"]) >= 100:
            data["description"] = data["description"][:100] + "..."
        return data


class MyShopSerializer(ShopDetailSerizlier):

    class Meta(ShopDetailSerizlier.Meta):
        fields = ShopDetailSerizlier.Meta.fields + ("owner", "stripe_account_id", "stripe_onboarding_complete")
        read_only_fields = ShopDetailSerizlier.Meta.read_only_fields + ("owner", "stripe_account_id", "stripe_onboarding_complete")


class ShopCreateUpdateSerlizer(serializers.ModelSerializer):

    class Meta:
        model = Shop
        fields = ("name", "description", "logo")


    def validate(self, attrs):
        request = self.context.get("request")

        if not request or not request.user:
            return attrs

        user = request.user

        if not getattr(user, "is_email_verified", False):
            raise serializers.ValidationError({
                    "error": "Ваш email не подтвержен."
                })  

        if self.instance is None:
            if hasattr(user, "shop"):
                raise serializers.ValidationError({
                    "error": "У вас уже есть созданный магазин."
                })

        return attrs


    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)
