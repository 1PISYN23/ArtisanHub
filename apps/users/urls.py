from django.urls import path
from .views import (
    CustomTokenObtainPairView,
    TokenRefreshView,
    RegisterView,
    send_verification_code_view,
    verify_verification_code_view,
    send_password_reset_code_view,
    verifiy_password_reset_code,
    password_reset_with_code_view,
    change_password_view,
    logout_view,
    deactivate_accoint_view,
    UserProfileView,
)


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", logout_view, name="logout"),
    path("deactivate-account/", deactivate_accoint_view, name="deactivate_account"),
    path("send-verification-code/", send_verification_code_view, name="send_verification_code"),
    path("verify-verification-code/", verify_verification_code_view, name="verify_verification_code"),
    path("send-password-reset-code/", send_password_reset_code_view, name="send_password_reset_code"),
    path("verify-password-reset-code/", verifiy_password_reset_code, name="verify_password_reset_code"),
    path("password-reset/", password_reset_with_code_view, name="password_reset_with_code"),
    path("change-password/", change_password_view, name="change_password"),
    path("profile/", UserProfileView.as_view(), name="profile"),
]

