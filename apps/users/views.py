from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, OpenApiExample
from .throttling import PasswordResetAnon, VerificationAnon

from .service import VerificationCodeService

from .models import CustomUser
from .serializers import (
    CustomTokenObtainPairSerizlier,
    UserRegistrationSerializer,
    SendVerificationCodeSerizlier,
    VerifyCodeSerializer,
    VerifyVerificationCodeSerizlier,
    SendPasswordResetCodeSerializer,
    VerifyPasswordResetSerializer,
    ChangePasswordSerizlier,
    PasswordResetWithCodeSerizlier,
    UserProfileSerizlier,
    UpdateUserProfileSerizlier,
    LogoutSerializer
)


def _tokens_for(user):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


@extend_schema(
    summary="Вход в систему",
    description="Получение JWT токенов для аутентификации пользователя",
    tags=["auth"],
    request=CustomTokenObtainPairSerizlier,
    responses={
        200: OpenApiResponse(
            description="Успешная аутентификация"
        ),
        400: OpenApiResponse(
            description="Ошибка валидации данных"
        ),
        401: OpenApiResponse(
            description="Неверные учетные данные"
        )
    }
)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerizlier
    permission_classes = [AllowAny]


@extend_schema(
    summary="Обновление токена",
    description="Обновление access токена с помощью refresh токена",
    tags=["auth"],
    request=TokenRefreshSerializer,
    responses={

    }
)
class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer
    permission_classes = [AllowAny]


    def post(self, request, *args, **kwargs):
        pass


@extend_schema(
    summary="Регистрация пользователя",
    description="Регистрация пользователя",
    tags=["auth"],
    request=UserRegistrationSerializer,
    responses={
        201: OpenApiResponse(
            description="Успешная регистрая пользователя"
        ),
        400: OpenApiResponse(
            description="Ошибка валидации данных или регистрация не удалась"
        )
    }
)
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        tokens = _tokens_for(user)

        return Response({
            "tokens": tokens,
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name if user.first_name else None,
                "last_name": user.last_name if user.last_name else None,
                "phone": user.phone if user.phone else None,
                "avatar": user.avatar.url if user.avatar else None,
                "is_email_verified": user.is_email_verified,
            },
            "message": "Пользователь успешно зарегестрирован",
        }, status=status.HTTP_201_CREATED)



@extend_schema(
    summary="Отправка кода регистрации",
    description="Отправка кода регистрации для верификации email. Код действителен 5 минут.",
    tags=["verification"],
    request=SendVerificationCodeSerizlier,
    responses={
        200: OpenApiResponse(
            description="Успешная отправка кода на email"
        ),
        400: OpenApiResponse(
            description="Ошибка валидации данных"
        ),
        500: OpenApiResponse(
            description="Ошибка при отправке кода на email"
        )
    }
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@throttle_classes([VerificationAnon])
def send_verification_code_view(request):
    serializer = SendVerificationCodeSerizlier(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data["email"]

    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return Response({
            "error": "Ошибка валидации данных"
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        VerificationCodeService.send_verification_code(user)

        return Response({
            "message": "Код подтверждения для регистрации отправлен на email",
            "expires_in": 300,
        }, status=status.HTTP_200_OK)
    except Exception:
        return Response({
            "error": "Ошибки при отправке кода на email"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@extend_schema(
    summary="Проверка кода верификации почты",
    description="Проверка кода верификации почты, после проверки у пользователя ставится флаг верифицированной почты.",
    tags=["verification"],
    request=VerifyVerificationCodeSerizlier,
    responses={
        200: OpenApiResponse(
            description="Успешная верификация почты."
        ),
        400: OpenApiResponse(
            description="Ошибка валидации."
        )
    }
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def verify_verification_code_view(request):
    serizlier = VerifyVerificationCodeSerizlier(data=request.data)

    if not serizlier.is_valid():
        return Response(serizlier.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "message": "Вы успешно подтвердили почту."
    }, status=status.HTTP_200_OK)


@extend_schema(
    summary="Код для сброса пароля",
    description="Отправка кода подтверждения на email для смены пароля (без доступа к лк). Код действителен 5 минут.",
    tags=["verification"],
    request=SendPasswordResetCodeSerializer,
    responses={
        200: OpenApiResponse(
            description="Код успешно отправлен на почту"
        ),
        400: OpenApiResponse(
            description="Ошибка валидации данных"
        ),
        500: OpenApiResponse(
            description="Ошибка отправки кода на почту"
        )
    }
)
@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([PasswordResetAnon])
def send_password_reset_code_view(request):
    serializer = SendPasswordResetCodeSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    email = serializer.validated_data["email"]

    try:
        user = CustomUser.objects.get(email=email)
    except CustomUser.DoesNotExist:
        return Response({
            "error": "Ошибка валидации данных"
        }, status=status.HTTP_400_BAD_REQUEST)


    try:
        VerificationCodeService.send_password_reset_code(user)

        return Response({
            "message": "Код для сброса пароля успешно отправлен.",
            "expires_in": 300,
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "error": "Неудалось отправить код",
            "details": str(e),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Проверка кода смены пароля",
    description="Проверка кода подтверждения для смены пароля. После успешной проверки создается флаг верификации на 10 минут, который позволяет сменить пароль.",
    tags=["verification"],
    request=VerifyPasswordResetSerializer,
    responses={
        200: OpenApiResponse(
            description="Код подтверждения для смены пароля верен",
        ),
        400: OpenApiResponse(
            description="Ошибка валидации данных"
        )
    }
)
@api_view(["POST"])
@permission_classes([AllowAny])
def verifiy_password_reset_code(request):
    serializer = VerifyPasswordResetSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "message": "Код подтверждения для смены пароля верен."
    }, status=status.HTTP_200_OK)


@extend_schema(
    summary="Смена пароля",
    description="Смена пароля после подтверждения email. Смена пароля для неавтризованных пользователей",
    tags=["auth"],
    request=PasswordResetWithCodeSerizlier,
    responses={
        200: OpenApiResponse(
            description="Успешное изменени пароля"
        ),
        400: OpenApiResponse(
            description="Ошибка валидации данных"
        )
    }
)
@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_with_code_view(request):
    serializer = PasswordResetWithCodeSerizlier(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.save()

    tokens = _tokens_for(user)

    return Response({
        "message": "Вы успешно изменили пароль.",
        "tokens": tokens,
    }, status=status.HTTP_200_OK)


@extend_schema(
    summary="Смена пароля для авторизованных пользователей",
    description="Смена пароля для авторизованного пользователя. Требуется указать старый пароль, новый пароль и подтверждение нового пароля.",
    tags=["auth"],
    request=ChangePasswordSerizlier,
    responses={
        200: OpenApiResponse(
            description="Успешное изменение пароля"
        ),
        400: OpenApiResponse(
            description="Ошибка валидации данных"
        )
    }
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    serializer = ChangePasswordSerizlier(data=request.data, context={"request": request})

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()

    return Response({
        "message": "Пароль успешно изменен!"
    }, status=status.HTTP_200_OK)


@extend_schema_view(
    get=extend_schema(
        summary="Профиль пользователя",
        description="Получение информации о профиле пользователя",
        tags=["auth"],
        request=UserProfileSerizlier,
        responses={
            200: OpenApiResponse(
                description="Информация о профиле пользователя"
            ),
            400: OpenApiResponse(
                description="Профиль пользователя не найден"
            ),
            401: OpenApiResponse(
                description="Необходима аутентификация"
            )
        }
    ),
    put=extend_schema(
        summary="Обновление профиля пользователя",
        description="Полное обновление профиля пользователя",
        tags=["auth"],
        request=UpdateUserProfileSerizlier,
        responses={
            200: OpenApiResponse(
                description="Профиль пользователя успешно обновлен",
                response=UserProfileSerizlier,
                examples=[
                    OpenApiExample(
                        "Пример усешного ответа",
                        value={
                            "id": 1,
                            "email": "email@gmail.com",
                            "first_name": "Name",
                            "last_name": "Familiya",
                            "phone": "",
                            "avatar": "url",
                            "is_email_verified": "False",
                            "date_joined": "10.01.2026",
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Ошибка валидации данных или пользователь не найден"
            ),
            404: OpenApiResponse(
                description="Пользователь не найден"
            )
        }
    ),
    patch=extend_schema(
        summary="Обновление профиля пользователя",
        description="Частичное обновление профиля пользователя",
        tags=["auth"],
        request=UpdateUserProfileSerizlier,
        responses={
            200: OpenApiResponse(
                description="Профиль пользователя успешно обновлен",
                response=UserProfileSerizlier,
            ),
            400: OpenApiResponse(
                description="Ошибка валидации данных или пользователь не найден"
            ),
            404: OpenApiResponse(
                description="Пользователь не найден"
            )
        }
    )
)
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerizlier
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


    def get_serializer_class(self):
        if self.request.method in ["PATCH", "PUT"]:
            return UpdateUserProfileSerizlier
        return UserProfileSerizlier


@extend_schema(
    summary="Выход из системы",
    description="ершение сессии пользователя и блокировка refresh токена",
    tags=["auth"],
    request=LogoutSerializer,
    responses={
        205: OpenApiResponse(
            description="Успешный выход из системы"
        ),
        400: OpenApiResponse(
            description="Ошибка при выходе из системы"
        ),
        401: OpenApiResponse(
            description="Необходима аутентификация"
        )
    }
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    serializer = LogoutSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        refresh_token = serializer.validated_data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response({
            "message": "Успешный выход из системы!"
        }, status=status.HTTP_205_RESET_CONTENT)
    except Exception:
        return Response({
            "error": "Ошибка при выходе из системы!"
        }, status=status.HTTP_400_BAD_REQUEST)
    


@extend_schema(
    summary="Деактивация аккаунта.",
    description="Деактивирует аккаунт текущего пользователя. После деактивации пользователь не сможет войти в систему.",
    tags=["auth"],
    responses={
        200: OpenApiResponse(
            description="Аккаунт успешно деактивирован",
            examples=[
                OpenApiExample(
                    name="Успешная деактивация",
                    value={
                        "message": "Аккаунт успешно деактивирован"
                    }
                )
            ]
        ),
        401: OpenApiResponse(
            description="Необходима аутентификация"
        )
    }
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def deactivate_accoint_view(request):
    user = request.user

    user.is_active = False 
    user.save()

    try:
        from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

        outstanding_tokens = OutstandingToken.objects.filter(user=user)
        for outstanding_token in outstanding_tokens:
            try:
                refresh_token = RefreshToken(outstanding_token)
                refresh_token.blacklist()
            except Exception:
                pass
    except Exception:
        pass

    return Response({
        "message": "Аккаунт успешно деактивирован"
    }, status=status.HTTP_200_OK)



# + такой вопрос, я могу прописать отдельный endpont на изменение профиля пользователя и сделать также функционально, или оставить так как есть? 