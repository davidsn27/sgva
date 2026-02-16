#!/usr/bin/env python
"""
Script para instalar automáticamente todas las dependencias del requirements.txt
Ejecutar: python install_dependencies.py
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Ejecuta un comando y muestra el resultado"""
    print(f"\n🔧 {description}")
    print(f"Comando: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        print(f"✅ Éxito: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr}")
        return False


def main():
    print("🚀 Instalador de dependencias SGVA")
    print("=" * 50)
    
    # Verificar si estamos en el entorno virtual
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Advertencia: No se detecta entorno virtual activo")
        print("   Considera activar el entorno virtual primero:")
        print("   source venv/bin/activate  # Linux/Mac")
        print("   venv\\Scripts\\activate   # Windows")
        print()
    
    # Actualizar pip
    run_command("python -m pip install --upgrade pip", "Actualizando pip")
    
    # Instalar dependencias desde requirements.txt
    if os.path.exists("requirements.txt"):
        success = run_command(
            "pip install -r requirements.txt", 
            "Instalando dependencias desde requirements.txt"
        )
        if success:
            print("\n✅ Todas las dependencias se instalaron correctamente")
        else:
            print("\n❌ Hubo errores al instalar algunas dependencias")
    else:
        print("❌ No se encuentra el archivo requirements.txt")
        return 1
    
    # Verificar instalación de pandas específicamente
    print("\n🔍 Verificando instalación de pandas...")
    try:
        import pandas
        print(f"✅ pandas {pandas.__version__} instalado correctamente")
    except ImportError:
        print("❌ pandas no está instalado. Instalando manualmente...")
        run_command(
            "pip install pandas==2.2.3 openpyxl==3.1.5 xlrd==2.0.1",
            "Instalando pandas y dependencias de Excel manualmente"
        )
    
    # Verificar otras dependencias críticas
    critical_packages = [
        ("django", "Django"),
        ("celery", "Celery"),
        ("redis", "Redis"),
        ("gunicorn", "Gunicorn"),
        ("whitenoise", "WhiteNoise"),
        ("djangorestframework", "Django REST Framework"),
        ("django-allauth", "Django Allauth"),
        ("psycopg2-binary", "PostgreSQL adapter")
    ]
    
    print("\n🔍 Verificando paquetes críticos...")
    for package, name in critical_packages:
        try:
            __import__(package)
            print(f"✅ {name} instalado")
        except ImportError:
            print(f"❌ {name} NO instalado")
    
    print("\n🎉 Proceso completado!")
    print("Si todo está en ✅, puedes ejecutar:")
    print("  python manage.py runserver")
    print("  python manage.py migrate")
    print("  python manage.py collectstatic")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
