from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password

from django.conf import settings
from django.core.exceptions import ValidationError

from .models import CustomUser
from .service import VerificationCodeService
from .tasks import send_email_code_verification, send_welcome_email


class CustomTokenObtainPairSerizlier(TokenObtainPairSerializer):

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            email = email.lower().strip()
            attrs["email"] = email

            try:
                user = CustomUser.objects.get(email=email)

                if not user.is_active:
                    raise serializers.ValidationError(
                        "Аккаунт удален, обратитесь пожалуйста в техническую поддержку."
                    )

                if not user.check_password(password):
                    raise serializers.ValidationError(
                        "Неверный email или пароль."
                    )

            except CustomUser.DoesNotExist:
                raise serializers.ValidationError(
                    "Неверный email или пароль."
                )

            refresh = self.get_token(user)

            data = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name if user.first_name else None,
                    "last_name": user.last_name if user.last_name else None,
                    "phone": user.phone if user.phone else None,
                    "avatar": user.avatar.url if user.avatar else None,
                    "is_email_verified": user.is_email_verified,
                }
            }

            return data

        else:
            raise serializers.ValidationError(
                "Необходимо указать email и пароль."
            )


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, min_length=8)


    class Meta:
        model = CustomUser
        fields = ["email", "first_name", "last_name", "phone", "password", "password_confirm"]


    def validate_email(self, value):
        if value:
            value = value.lower().strip()
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует."
            )
        return value


    def validate(self, attrs):
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")

        if password != password_confirm:
            raise serializers.ValidationError(
                "Пароли не совпадают."
            )
        return attrs


    def create(self, validated_data):
        validated_data.pop("password_confirm")

        user = CustomUser.objects.create_user(**validated_data)

        send_welcome_email.delay(user.id)

        return user



class VerifyVerificationCodeSerizlier(serializers.Serializer):
    code = serializers.CharField(required=True, min_length=6, max_length=6)

    def validate(self, attrs):
        code = attrs.get("code")

        user = self.context.get("request").user

        try:
            VerificationCodeService.verify_verification_code(user, code)
        except ValidationError as e:
            raise serializers.ValidationError({"code": str(e)})

        return attrs


class ChangePasswordSerizlier(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, min_length=8)
    new_password = serializers.CharField(write_only=True, min_length=8, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True, min_length=8)


    def validate_old_password(self, value):
        user = self.context.get("request").user

        if not user.check_password(value):
            raise serializers.ValidationError("Неверный текущий пароль.")
        return value


    def validate(self, attrs):
        new_password = attrs.get("new_password")
        new_password_confirm = attrs.get("new_password_confirm")

        if new_password != new_password_confirm:
            raise serializers.ValidationError("Пароли не совпадают.")
        
        return attrs


    def save(self):
        user = self.context.get("request").user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class SendPasswordResetCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, help_text="Email адрес для отправки кода смены пароля")

    def validate_email(self, value):
        if value:
            value = value.lower().strip()

        if not CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email не найден.")

        return value
   

class VerifyPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True, min_length=6, max_length=6)


    def validate_email(self, value):
        if value:
            value = value.lower().strip()

        if not CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError({
                "code": "Неверный код"
            })
        return value
    

    def validate(self, attrs):
        email = attrs.get("email")
        code = attrs.get("code")

        user = CustomUser.objects.get(email=email)

        try:
            VerificationCodeService.verify_password_reset_code(user, code)
        except ValidationError as e:
            raise serializers.ValidationError({"code": str(e)})

        return attrs


class PasswordResetWithCodeSerizlier(serializers.Serializer):
    email = serializers.EmailField(required=True, help_text="Email адрес")
    new_password = serializers.CharField(write_only=True, min_length=8, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True, min_length=8)


    def validate_email(self, value):
        if value:
            value = value.lower().strip()
        if not CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email не найден.")
        return value


    def validate(self, attrs):
        new_password = attrs.get("new_password")
        new_password_confirm = attrs.get("new_password_confirm")
        email = attrs.get("email")

        if new_password != new_password_confirm:
            raise serializers.ValidationError("Пароли не совпадают.")

        try:   # Мб убрать и сделать без исключения? Так как есть validate_email? 
            user = CustomUser.objects.get(email=email)  
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError(
                {"code": "Неверный код."}
            )

        if not VerificationCodeService.check_password_reset_verified(user):
            raise serializers.ValidationError(
                "Email не подтверждён. Сначала подтвердите email с помощью кода."
            )
        
        return attrs


    def save(self):
        email = self.validated_data["email"]
        new_password = self.validated_data["new_password"]
        user = CustomUser.objects.get(email=email)

        VerificationCodeService.consume_password_reset(user)

        user.set_password(new_password)
        user.save()

        return user

    

class UserProfileSerizlier(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "email", "first_name", "last_name", "phone", "avatar", "is_email_verified", "date_joined"]
        read_only_fields = ["id", "email", "is_email_verified", "date_joined"]


class UpdateUserProfileSerizlier(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "phone", "avatar"]


    def update(self, instance, validated_data):
        for attrs, value in validated_data.items():
            setattr(instance, attrs, value)
        instance.save()
        return instance


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True, help_text="Refresh токен для блокировки")