from django.http import JsonResponse
from django.shortcuts import redirect


class FuncionarioOnlyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path or "/"

        if path.startswith("/admin/"):
            if not request.user.is_authenticated:
                return redirect("login")
            if not getattr(request.user, "is_superuser", False):
                return redirect("info_empresas")
            return self.get_response(request)

        # Public / always-allowed paths
        if (
            path == "/"
            or path == "/inicio/"
            or path.startswith("/info/")
            or path.startswith("/accounts/")
            or path.startswith("/static/")
            or path.startswith("/media/")
            or path in ("/login/", "/logout/")
            or path.startswith("/api/schema/")
            or path.startswith("/api/docs/")
            or path.startswith("/api/redoc/")
        ):
            return self.get_response(request)

        is_api = path.startswith("/api/")

        # Require authentication for private routes
        if not request.user.is_authenticated:
            if is_api:
                return JsonResponse({"error": "No autenticado"}, status=401)
            return redirect("login")

        # Require FUNCIONARIO_SENA role
        try:
            perfil = request.user.perfil
            is_funcionario = perfil.rol == "FUNCIONARIO_SENA"
        except Exception:
            is_funcionario = False

        if not is_funcionario:
            if is_api:
                return JsonResponse(
                    {"error": "Acceso restringido: solo funcionarios SENA"}, status=403
                )
            return redirect("info_empresas")

        return self.get_response(request)
