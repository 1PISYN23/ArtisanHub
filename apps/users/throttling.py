from rest_framework.throttling import AnonRateThrottle


class PasswordResetAnon(AnonRateThrottle):
    scope = "password_reset_anon"

