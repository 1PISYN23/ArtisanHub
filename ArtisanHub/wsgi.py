"""
WSGI config for ArtisanHub project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ArtisanHub.settings')

# Безопасный запуск debugpy для мультипроцессорных серверов (Gunicorn)
if os.environ.get('DJANGO_DEBUGPY') == '1':
    import debugpy
    try:
        debugpy.listen(("0.0.0.0", 5678))
        print("💡 [DEBUG] debugpy успешно запущен на порту 5678")
    except RuntimeError:
        # Если порт уже занят главным процессом или другим воркером, просто пропускаем
        print("💡 [DEBUG] debugpy уже слушает этот порт (вызов из воркера)")

application = get_wsgi_application()
