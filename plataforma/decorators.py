"""
Decoradores personalizados para la plataforma SGVA
"""

from django.http import JsonResponse
from django.shortcuts import redirect


def funcionario_sena_required(view_func):
    """
    Decorador que restringe el acceso solo a funcionarios SENA
    NOTA: Este decorador ya no se usa, pero se mantiene por compatibilidad
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        try:
            perfil = request.user.perfil
            if perfil.rol != "FUNCIONARIO_SENA":
                # Redirigir a información de empresas en lugar de acceso denegado
                return redirect('info_empresas')
        except Exception:
            # Redirigir a información de empresas en lugar de acceso denegado
            return redirect('info_empresas')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def trabajador_required(view_func):
    """
    Decorador que restringe el acceso solo a usuarios trabajadores (empresas)
    NOTA: Este decorador ya no se usa, pero se mantiene por compatibilidad
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        try:
            perfil = request.user.perfil
            if perfil.rol != "TRABAJADOR":
                return redirect('info_empresas')
        except Exception:
            return redirect('info_empresas')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def api_trabajador_required(view_func):
    """
    Decorador para APIs que restringe el acceso solo a usuarios trabajadores (empresas)
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'No autenticado'}, status=401)
        
        try:
            perfil = request.user.perfil
            if perfil.rol != "TRABAJADOR":
                return JsonResponse({'error': 'Acceso restringido: solo trabajadores'}, status=403)
        except Exception:
            return JsonResponse({'error': 'Perfil no encontrado'}, status=403)
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def estudiante_required(view_func):
    """
    Decorador para APIs que restringe el acceso solo a funcionarios SENA
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'No autenticado'}, status=401)
        
        try:
            perfil = request.user.perfil
            if perfil.rol != "FUNCIONARIO_SENA":
                return JsonResponse({'error': 'Acceso denegado. Solo funcionarios SENA'}, status=403)
        except Exception:
            return JsonResponse({'error': 'Perfil no encontrado'}, status=403)
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
