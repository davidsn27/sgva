#!/usr/bin/env python
"""
Script para crear datos básicos de prueba para SGVA
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sgva.settings')
django.setup()

from plataforma.models import Aprendiz, Empresa
from django.contrib.auth.models import User
from django.utils import timezone

def crear_datos_prueba():
    """Crear datos básicos de prueba"""
    print("🚀 Creando datos básicos de prueba...")
    
    try:
        # Crear empresas
        if not Empresa.objects.exists():
            empresas = [
                Empresa(
                    nit='900123456-1',
                    nombre='Tecnología y Soluciones SAS',
                    direccion='Cra 45 #123-45, Bogotá',
                    telefono_contacto='3101234567',
                    correo_contacto='contacto@tecsoluciones.com',
                    capacidad_cupos=15,
                    estado='DISPONIBLE',
                    descripcion='Empresa líder en soluciones tecnológicas.',
                    observacion='Especializada en desarrollo de software.'
                ),
                Empresa(
                    nit='800987654-2',
                    nombre='Alimentos del Campo Ltda.',
                    direccion='Av 6 #12-34, Ibagué',
                    telefono_contacto='3119876543',
                    correo_contacto='info@alimentoscampo.com',
                    capacidad_cupos=20,
                    estado='DISPONIBLE',
                    descripcion='Productora de alimentos orgánicos.',
                    observacion='Certificación orgánica y procesos de calidad.'
                ),
                Empresa(
                    nit='900456789-3',
                    nombre='Construcciones del Futuro S.A.',
                    direccion='Cl 34 #56-78, Medellín',
                    telefono_contacto='3124567890',
                    correo_contacto='contacto@construccionesfuturo.com',
                    capacidad_cupos=10,
                    estado='DISPONIBLE',
                    descripcion='Construcción sostenible y eco-amigable.',
                    observacion='Líder en construcción verde.'
                )
            ]
            
            for empresa in empresas:
                empresa.save()
                print(f"✅ Empresa creada: {empresa.nombre}")
        else:
            print("ℹ️ Las empresas ya existen")
        
        # Crear aprendices
        if not Aprendiz.objects.exists():
            aprendices = [
                Aprendiz(
                    tipo_identificacion='CC',
                    numero_identificacion='123456789',
                    nombre='Carlos Andrés',
                    correo='carlos.rodriguez@email.com',
                    telefono='3111234567',
                    direccion='Cra 45 #12-34, Bogotá',
                    programa_formacion='ANÁLISIS Y DESARROLLO DE SOFTWARE',
                    ficha='2283679',
                    estado='DISPONIBLE'
                ),
                Aprendiz(
                    tipo_identificacion='CC',
                    numero_identificacion='987654321',
                    nombre='Laura Sofía',
                    correo='laura.martinez@email.com',
                    telefono='3129876543',
                    direccion='Cl 20 #45-67, Ibagué',
                    programa_formacion='CONTADURÍA PÚBLICA',
                    ficha='2283680',
                    estado='DISPONIBLE'
                ),
                Aprendiz(
                    tipo_identificacion='CC',
                    numero_identificacion='456789123',
                    nombre='David Esteban',
                    correo='david.gomez@email.com',
                    telefono='3145678901',
                    direccion='Av 5 #89-10, Medellín',
                    programa_formacion='ELECTROMECÁNICA',
                    ficha='2283681',
                    estado='CONTRATADO'
                ),
                Aprendiz(
                    tipo_identificacion='CC',
                    numero_identificacion='789123456',
                    nombre='Ana María',
                    correo='ana.hernandez@email.com',
                    telefono='3132345678',
                    direccion='Cra 8 #34-56, Cali',
                    programa_formacion='ENFERMERÍA',
                    ficha='2283682',
                    estado='DISPONIBLE'
                )
            ]
            
            for aprendiz in aprendices:
                aprendiz.save()
                
                # Crear usuario para el aprendiz
                username = f"aprendiz_{aprendiz.numero_identificacion[-6:]}"
                if not User.objects.filter(username=username).exists():
                    user = User.objects.create_user(
                        username=username,
                        email=aprendiz.correo,
                        password='aprendiz123',
                        first_name=aprendiz.nombre,
                        last_name=''
                    )
                    
                    # Crear perfil
                    from plataforma.models import Perfil
                    Perfil.objects.create(
                        usuario=user,
                        rol='ESTUDIANTE',
                        aprendiz=aprendiz
                    )
                
                print(f"✅ Aprendiz creado: {aprendiz.nombre}")
        else:
            print("ℹ️ Los aprendices ya existen")
        
        print("\n✅ Datos de prueba creados exitosamente!")
        print(f"📊 Estadísticas:")
        print(f"   • Empresas: {Empresa.objects.count()}")
        print(f"   • Aprendices: {Aprendiz.objects.count()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    crear_datos_prueba()
