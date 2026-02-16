"""
Contexto de Sentry para SGVA
"""

import sentry_sdk


def crear_sentry_context(user, contexto_adicional=None):
    """
    Crear contexto personalizado para Sentry

    Uso:
    crear_sentry_context(request.user, {
        'postulacion_id': 123,
        'accion': 'crear_postulacion'
    })
    """
    with sentry_sdk.push_scope() as scope:
        # Usuario
        if user and user.is_authenticated:
            scope.set_user(
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                }
            )

        # Contexto adicional
        if contexto_adicional:
            scope.set_context("custom", contexto_adicional)


def capture_exception_con_contexto(exception, contexto=None):
    """Capturar excepción con contexto personalizado"""
    with sentry_sdk.push_scope() as scope:
        if contexto:
            scope.set_context("exception_context", contexto)
        sentry_sdk.capture_exception(exception)


# Ejemplos de uso en vistas
def ejemplo_uso_en_vista(request):
    """
    Ejemplo de cómo usar Sentry en vistas

    Uso:
        try:
            # Tu código aquí
            resultado = hacer_algo()
        except Exception as e:
            capture_exception_con_contexto(e, {
                'usuario': request.user.username,
                'url': request.path,
                'metodo': request.method,
            })
            raise
    """
    pass
