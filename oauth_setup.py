"""
Configuración de OAuth2 con Google y Microsoft
"""

from allauth.socialaccount.models import SocialApp
from django.contrib.auth.models import User


def crear_oauth_providers():
    """
    Crear proveedores OAuth en la BD
    Ejecutar después de migrate: python manage.py shell < crear_oauth.py
    """

    # GOOGLE OAUTH
    google_app, created = SocialApp.objects.get_or_create(
        provider="google",
        name="Google",
        defaults={
            "client_id": "TU_GOOGLE_CLIENT_ID.apps.googleusercontent.com",
            "secret": "TU_GOOGLE_SECRET",
        },
    )

    if created:
        print("✅ Google OAuth creado")
        from django.contrib.sites.models import Site

        site = Site.objects.get_current()
        google_app.sites.add(site)
    else:
        print("ℹ️  Google OAuth ya existe")

    # MICROSOFT OAUTH
    microsoft_app, created = SocialApp.objects.get_or_create(
        provider="microsoft-graph",
        name="Microsoft",
        defaults={
            "client_id": "TU_MICROSOFT_CLIENT_ID",
            "secret": "TU_MICROSOFT_SECRET",
        },
    )

    if created:
        print("✅ Microsoft OAuth creado")
        from django.contrib.sites.models import Site

        site = Site.objects.get_current()
        microsoft_app.sites.add(site)
    else:
        print("ℹ️  Microsoft OAuth ya existe")

    print("\n📝 PRÓXIMOS PASOS:")
    print("1. Ir a https://console.cloud.google.com para Google")
    print("2. Ir a https://portal.azure.com para Microsoft")
    print("3. Actualizar los valores en admin: http://localhost:8000/admin/")
