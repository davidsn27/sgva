"""
Módulo para importación de datos desde archivos Excel/CSV
"""

import pandas as pd
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Aprendiz, Empresa, Perfil, Postulacion


class ImportadorDatos:
    """Clase para manejar la importación de datos desde archivos Excel/CSV"""
    
    def __init__(self):
        self.errores = []
        self.exito = []
    
    def importar_aprendices(self, archivo):
        """
        Importa aprendices desde archivo Excel/CSV
        Formato esperado: nombres, apellidos, tipo_documento, numero_documento, 
                        email, telefono, estado, programa_formacion
        """
        try:
            # Leer archivo
            if archivo.name.endswith('.xlsx'):
                df = pd.read_excel(archivo)
            else:
                df = pd.read_csv(archivo)
            
            # Validar columnas requeridas
            columnas_requeridas = ['nombres', 'apellidos', 'tipo_documento', 'numero_documento', 'email']
            if not all(col in df.columns for col in columnas_requeridas):
                self.errores.append("Faltan columnas requeridas en el archivo")
                return False
            
            # Procesar cada fila
            for index, row in df.iterrows():
                try:
                    # Verificar si ya existe
                    if Aprendiz.objects.filter(numero_documento=str(row['numero_documento'])).exists():
                        self.errores.append(f"Fila {index+1}: El aprendiz con documento {row['numero_documento']} ya existe")
                        continue
                    
                    # Crear usuario Django
                    username = f"{row['nombres'].split()[0].lower()}_{row['apellidos'].split()[0].lower()}_{row['numero_documento']}"
                    user = User.objects.create_user(
                        username=username,
                        email=row['email'],
                        password=f"temp_{row['numero_documento']}"  # Contraseña temporal
                    )
                    
                    # Crear perfil
                    perfil = Perfil.objects.create(
                        usuario=user,
                        rol="ESTUDIANTE"
                    )
                    
                    # Crear aprendiz
                    aprendiz = Aprendiz.objects.create(
                        usuario=user,
                        perfil=perfil,
                        nombres=row['nombres'],
                        apellidos=row['apellidos'],
                        tipo_documento=row.get('tipo_documento', 'CC'),
                        numero_documento=str(row['numero_documento']),
                        email=row['email'],
                        telefono=row.get('telefono', ''),
                        estado=row.get('estado', 'ACTIVO'),
                        programa_formacion=row.get('programa_formacion', ''),
                        fecha_ultima_actividad=timezone.now()
                    )
                    
                    self.exito.append(f"Aprendiz {aprendiz.nombres} {aprendiz.apellidos} importado correctamente")
                    
                except Exception as e:
                    self.errores.append(f"Fila {index+1}: Error al procesar - {str(e)}")
            
            return len(self.errores) == 0
            
        except Exception as e:
            self.errores.append(f"Error al leer el archivo: {str(e)}")
            return False
    
    def importar_empresas(self, archivo):
        """
        Importa empresas desde archivo Excel/CSV
        Formato esperado: nit, nombre, descripcion, direccion, telefono, email, estado, cupos
        """
        try:
            # Leer archivo
            if archivo.name.endswith('.xlsx'):
                df = pd.read_excel(archivo)
            else:
                df = pd.read_csv(archivo)
            
            # Validar columnas requeridas
            columnas_requeridas = ['nit', 'nombre']
            if not all(col in df.columns for col in columnas_requeridas):
                self.errores.append("Faltan columnas requeridas en el archivo")
                return False
            
            # Procesar cada fila
            for index, row in df.iterrows():
                try:
                    # Verificar si ya existe
                    if Empresa.objects.filter(nit=str(row['nit'])).exists():
                        self.errores.append(f"Fila {index+1}: La empresa con NIT {row['nit']} ya existe")
                        continue
                    
                    # Crear usuario Django para la empresa
                    username = f"empresa_{str(row['nit']).replace('.', '').replace('-', '')}"
                    email = row.get('email', f"contacto@{str(row['nit']).replace('.', '')}.com")
                    
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=f"temp_{row['nit']}"  # Contraseña temporal
                    )
                    
                    # Crear empresa
                    empresa = Empresa.objects.create(
                        usuario=user,
                        nit=str(row['nit']),
                        nombre=row['nombre'],
                        descripcion=row.get('descripcion', ''),
                        direccion=row.get('direccion', ''),
                        telefono=row.get('telefono', ''),
                        email=row.get('email', ''),
                        estado=row.get('estado', 'DISPONIBLE'),
                        cupos=int(row.get('cupos', 5))
                    )
                    
                    self.exito.append(f"Empresa {empresa.nombre} importada correctamente")
                    
                except Exception as e:
                    self.errores.append(f"Fila {index+1}: Error al procesar - {str(e)}")
            
            return len(self.errores) == 0
            
        except Exception as e:
            self.errores.append(f"Error al leer el archivo: {str(e)}")
            return False
    
    def importar_postulaciones(self, archivo):
        """
        Importa postulaciones desde archivo Excel/CSV
        Formato esperado: numero_documento_aprendiz, nit_empresa, fecha_postulacion, estado
        """
        try:
            # Leer archivo
            if archivo.name.endswith('.xlsx'):
                df = pd.read_excel(archivo)
            else:
                df = pd.read_csv(archivo)
            
            # Validar columnas requeridas
            columnas_requeridas = ['numero_documento_aprendiz', 'nit_empresa']
            if not all(col in df.columns for col in columnas_requeridas):
                self.errores.append("Faltan columnas requeridas en el archivo")
                return False
            
            # Procesar cada fila
            for index, row in df.iterrows():
                try:
                    # Buscar aprendiz
                    try:
                        aprendiz = Aprendiz.objects.get(numero_documento=str(row['numero_documento_aprendiz']))
                    except Aprendiz.DoesNotExist:
                        self.errores.append(f"Fila {index+1}: Aprendiz con documento {row['numero_documento_aprendiz']} no encontrado")
                        continue
                    
                    # Buscar empresa
                    try:
                        empresa = Empresa.objects.get(nit=str(row['nit_empresa']))
                    except Empresa.DoesNotExist:
                        self.errores.append(f"Fila {index+1}: Empresa con NIT {row['nit_empresa']} no encontrada")
                        continue
                    
                    # Verificar si ya existe la postulación
                    if Postulacion.objects.filter(aprendiz=aprendiz, empresa=empresa).exists():
                        self.errores.append(f"Fila {index+1}: Ya existe una postulación para este aprendiz y empresa")
                        continue
                    
                    # Crear postulación
                    fecha_postulacion = timezone.now()
                    if 'fecha_postulacion' in row and pd.notna(row['fecha_postulacion']):
                        fecha_postulacion = pd.to_datetime(row['fecha_postulacion']).to_pydatetime()
                    
                    Postulacion.objects.create(
                        aprendiz=aprendiz,
                        empresa=empresa,
                        fecha_postulacion=fecha_postulacion,
                        estado=row.get('estado', 'PENDIENTE')
                    )
                    
                    self.exito.append(f"Postulación de {aprendiz.nombres} a {empresa.nombre} importada correctamente")
                    
                except Exception as e:
                    self.errores.append(f"Fila {index+1}: Error al procesar - {str(e)}")
            
            return len(self.errores) == 0
            
        except Exception as e:
            self.errores.append(f"Error al leer el archivo: {str(e)}")
            return False
    
    def limpiar_mensajes(self):
        """Limpia los mensajes de error y éxito"""
        self.errores = []
        self.exito = []
    
    def get_resumen(self):
        """Devuelve un resumen de la importación"""
        return {
            'errores': self.errores,
            'exito': self.exito,
            'total_errores': len(self.errores),
            'total_exito': len(self.exito)
        }
