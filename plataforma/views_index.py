from django.shortcuts import render

def index_view(request):
    """Vista principal del sistema SGVA"""
    return render(request, 'plataforma/index.html')
