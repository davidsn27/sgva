from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


# ------------------------
# PERFIL DE USUARIO
# ------------------------
class Perfil(models.Model):
    ROLES = [
        ("ESTUDIANTE", "Estudiante"),
        ("TRABAJADOR", "Trabajador/Admin"),
        ("FUNCIONARIO_SENA", "Funcionario SENA"),
    ]

    usuario = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="perfil"
    )
    rol = models.CharField(max_length=20, choices=ROLES, default="ESTUDIANTE")
    aprendiz = models.OneToOneField(
        "Aprendiz", on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"{self.usuario.username} - {self.rol}"


# ------------------------
# EMPRESA
# ------------------------
class Empresa(models.Model):
    ESTADOS = [
        ("DISPONIBLE", "Disponible"),
        ("PROCESO_SELECCION", "Proceso de seleccion abierto"),
        ("CONTRATO_NULO", "Contrato nulo"),
        ("CONTRATADO", "Contratado"),
    ]

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="empresa",
    )
    nit = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, default="")
    direccion = models.CharField(max_length=300, blank=True, default="")
    estado = models.CharField(
        max_length=30,
        choices=ESTADOS,
        default="DISPONIBLE",
        blank=False,
        null=False,
    )
    capacidad_cupos = models.PositiveIntegerField(
        default=0, help_text="Numero de cupos disponibles para aprendices"
    )
    telefono_contacto = models.CharField(
        max_length=30,
        blank=True,
        default="",
        help_text="Teléfono de contacto de la empresa",
    )
    correo_contacto = models.EmailField(
        blank=True, default="", help_text="Correo de contacto de la empresa"
    )
    observacion = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.nit})"

    @property
    def estado_badge(self):
        return "success" if self.estado == "DISPONIBLE" else "secondary"

    def cupos_disponibles(self):
        """Calcula cupos disponibles restando postulaciones aceptadas"""
        postulaciones_aceptadas = self.postulacion_set.filter(estado="CONTRATADO").count()
        return max(0, self.capacidad_cupos - postulaciones_aceptadas)

    def tiene_cupos(self):
        """Retorna True si hay cupos disponibles"""
        return self.cupos_disponibles() > 0


# ------------------------
# APRENDIZ
# ------------------------
class Aprendiz(models.Model):

    ESTADOS = [
        ("DISPONIBLE", "Disponible"),
        ("PROCESO_SELECCION", "Proceso de selección"),
        ("PROCESO_SELECCION_ABIERTO", "Proceso de selección abierto"),
        ("CONTRATO_NO_REGISTRADO", "Contrato no registrado"),
        ("CONTRATADO", "Contratado"),
        ("INHABILITADO_POR_ACTUALIZACION", "Inhabilitado por actualización"),
    ]

    nombre = models.CharField(max_length=200)
    tipo_identificacion = models.CharField(
        max_length=20,
        choices=[
            ("CC", "Cédula de Ciudadanía"),
            ("TI", "Tarjeta de Identidad"),
            ("CE", "Cédula de Extranjería"),
            ("PA", "Pasaporte"),
        ],
        default="CC",
        blank=True,
    )
    numero_identificacion = models.CharField(max_length=50, blank=True, default="")
    direccion = models.CharField(max_length=200, blank=True, default="")
    ficha = models.CharField(
        max_length=20,
        blank=True,
        default="",
        help_text="Número de ficha del aprendiz",
    )
    programa_formacion = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text="Programa de formación del aprendiz",
    )

    correo = models.EmailField(unique=True)

    telefono = models.CharField(max_length=20)

    estado = models.CharField(
        max_length=30,
        choices=ESTADOS,
        default="DISPONIBLE",
        blank=False,
        null=False,
    )

    empresa_actual = models.ForeignKey(
        Empresa, null=True, blank=True, on_delete=models.SET_NULL
    )

    observacion = models.TextField(blank=True)
    fecha_ultima_actividad = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.nombre} - {self.correo}"

    @property
    def estado_badge(self):
        """Retorna la clase de color para el badge del estado"""
        colores = {
            "DISPONIBLE": "success",
            "PROCESO_SELECCION": "warning",
            "PROCESO_SELECCION_ABIERTO": "info",
            "CONTRATO_NO_REGISTRADO": "danger",
            "CONTRATADO": "primary",
            "INHABILITADO_POR_ACTUALIZACION": "secondary",
        }
        return colores.get(self.estado, "secondary")


# ------------------------
# POSTULACIÓN
# ------------------------
class Postulacion(models.Model):
    ESTADOS = [
        ("PENDIENTE", "En proceso de selección"),
        ("PROCESO_SELECCION_ABIERTO", "Proceso de selección abierto"),
        ("SELECCIONADO", "Seleccionado"),
        ("RECHAZADO", "Rechazado"),
        ("CONTRATO_NO_REGISTRADO", "Contrato no registrado"),
        ("CONTRATADO", "Contratado"),
        ("DISPONIBLE", "Disponible"),
    ]

    aprendiz = models.ForeignKey(Aprendiz, on_delete=models.CASCADE)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    fecha_postulacion = models.DateTimeField(default=timezone.now)
    estado = models.CharField(max_length=30, choices=ESTADOS, default="PENDIENTE")
    observacion_aprendiz = models.TextField(
        blank=True, default="", help_text="Observación del aprendiz"
    )
    observacion_empresa = models.TextField(
        blank=True, default="", help_text="Observación de la empresa"
    )
    fecha_estado_actualizado = models.DateTimeField(
        null=True, blank=True, help_text="Fecha del último cambio de estado"
    )
    aprendiz_dio_respuesta = models.BooleanField(
        default=False, help_text="¿El aprendiz dejó observación?"
    )
    empresa_dio_respuesta = models.BooleanField(
        default=False, help_text="¿La empresa dejó observación?"
    )

    class Meta:
        unique_together = ("aprendiz", "empresa")

    def __str__(self):
        return f"{self.aprendiz} → {self.empresa} ({self.estado})"

    @property
    def estado_badge(self):
        colores = {
            "PENDIENTE": "warning",
            "PROCESO_SELECCION_ABIERTO": "info",
            "CONTRATO_NO_REGISTRADO": "danger",
            "CONTRATADO": "success",
            "DISPONIBLE": "secondary",
        }
        return colores.get(self.estado, "secondary")

    def puede_hacer_nueva_postulacion(self):
        """
        Verifica si el aprendiz puede hacer una nueva postulación
        (máximo 1 cada 15 días)
        """
        from datetime import timedelta

        hace_15_dias = timezone.now() - timedelta(days=15)
        postulaciones_recientes = Postulacion.objects.filter(
            aprendiz=self.aprendiz, fecha_postulacion__gte=hace_15_dias
        ).exclude(id=self.id)
        return postulaciones_recientes.count() == 0

    def tiene_postulacion_activa(self):
        """
        Verifica si el aprendiz tiene una postulación activa
        (PENDIENTE o SELECCIONADO)
        """
        postulaciones_activas = Postulacion.objects.filter(
            aprendiz=self.aprendiz,
            estado__in=["PENDIENTE", "PROCESO_SELECCION_ABIERTO", "SELECCIONADO"],
        ).exclude(id=self.id)
        return postulaciones_activas.count() > 0

    def ambas_partes_respondieron(self):
        """
        Verifica si empresa y aprendiz han dejado observaciones
        """
        return self.aprendiz_dio_respuesta and self.empresa_dio_respuesta

    def fecha_vencimiento(self):
        """
        Calcula la fecha de vencimiento de la postulación
        (15 días hábiles después)
        """
        from datetime import timedelta

        if not self.fecha_postulacion:
            return None

        dias_habiles_a_sumar = 15
        fecha_actual = self.fecha_postulacion
        dias_sumados = 0

        while dias_sumados < dias_habiles_a_sumar:
            fecha_actual += timedelta(days=1)
            # weekday() -> Lunes=0, ..., Sábado=5, Domingo=6
            if fecha_actual.weekday() < 5:  # Es un día de L a V
                dias_sumados += 1

        return fecha_actual


# ------------------------
# HISTORIAL DE ESTADOS DE POSTULACIÓN
# ------------------------
class HistorialPostulacion(models.Model):
    """Registra los cambios de estado en una postulación"""

    postulacion = models.ForeignKey(
        Postulacion, on_delete=models.CASCADE, related_name="historial"
    )

    estado_anterior = models.CharField(max_length=20, blank=True)
    estado_nuevo = models.CharField(max_length=20)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    comentario = models.TextField(blank=True)

    def __str__(self):
        return f"{self.postulacion} | " f"{self.estado_anterior} → {self.estado_nuevo}"

    class Meta:
        ordering = ["-fecha_cambio"]


# ------------------------
# SOLICITUD
# ------------------------
class Solicitud(models.Model):

    ESTADOS = [
        ("DISPONIBLE", "Disponible"),
        ("SELECCION", "En seleccion"),
        ("CONTRATO_APROB", "Contrato aprobado"),
        ("PROC_SEL_APROB", "Proceso seleccion aprobado"),
        ("DESPACHADO", "Despachado"),
        ("RECHAZADO", "Rechazado"),
    ]

    nombre = models.CharField(max_length=200)

    estado = models.CharField(
        max_length=30,
        choices=ESTADOS,
        default="DISPONIBLE",
    )

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


# ------------------------
# HISTORIAL DE ESTADOS
# ------------------------
class HistorialEstado(models.Model):

    solicitud = models.ForeignKey(
        Solicitud,
        on_delete=models.CASCADE,
        related_name="historial",
    )

    estado_anterior = models.CharField(max_length=30)
    estado_nuevo = models.CharField(max_length=30)

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    fecha = models.DateTimeField(auto_now_add=True)

    observacion = models.TextField(blank=True)

    def __str__(self):
        return f"{self.solicitud} | " f"{self.estado_anterior} → {self.estado_nuevo}"


# ------------------------
# CARTA DE FECHAS
# ------------------------
class CartaFechas(models.Model):
    """Carta de fechas y parámetros para solicitud de contrato"""
    
    ESTADOS = [
        ("PENDIENTE", "Pendiente de aprobación"),
        ("APROBADA", "Aprobada"),
        ("RECHAZADA", "Rechazada"),
        ("COMPLETADA", "Contrato completado"),
    ]
    
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name="cartas_fechas")
    aprendiz = models.ForeignKey(Aprendiz, on_delete=models.CASCADE, related_name="cartas_fechas")
    
    # Fechas del contrato
    fecha_inicio_propuesta = models.DateField()
    fecha_fin_propuesta = models.DateField()
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    
    # Parámetros del contrato
    salario_propuesto = models.DecimalField(max_digits=10, decimal_places=2, help_text="Salario mensual propuesto")
    tipo_contrato = models.CharField(
        max_length=50,
        choices=[
            ("PRACTICA", "Práctica"),
            ("CONTRATO_APRENDIZAJE", "Contrato de aprendizaje"),
            ("CONTRATO_TERMINO_FIJO", "Contrato a término fijo"),
            ("CONTRATO_INDEFINIDO", "Contrato indefinido"),
        ],
        default="CONTRATO_APRENDIZAJE"
    )
    
    # Información adicional
    cargo_ofrecido = models.CharField(max_length=200, help_text="Cargo o puesto ofrecido")
    descripcion_actividades = models.TextField(help_text="Descripción de las actividades a realizar")
    lugar_trabajo = models.CharField(max_length=200, help_text="Lugar o sede de trabajo")
    horario_trabajo = models.CharField(max_length=100, help_text="Horario de trabajo")
    
    # Beneficios adicionales
    beneficios = models.TextField(blank=True, help_text="Beneficios adicionales ofrecidos")
    seguro_medico = models.BooleanField(default=False, help_text="Incluye seguro médico")
    transporte = models.BooleanField(default=False, help_text="Incluye auxilio de transporte")
    alimentacion = models.BooleanField(default=False, help_text="Incluye auxilio de alimentación")
    
    # Estado y aprobación
    estado = models.CharField(max_length=30, choices=ESTADOS, default="PENDIENTE")
    
    # Aprobación del funcionario SENA
    funcionario_aprobacion = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="cartas_aprobadas"
    )
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    comentarios_aprobacion = models.TextField(blank=True, help_text="Comentarios del funcionario al aprobar/rechazar")
    
    # Aceptación del aprendiz
    aprendiz_acepta = models.BooleanField(null=True, blank=True, help_text="El aprendiz aceptó la propuesta")
    fecha_aceptacion_aprendiz = models.DateTimeField(null=True, blank=True)
    comentarios_aprendiz = models.TextField(blank=True, help_text="Comentarios del aprendiz")
    
    # Documentos adjuntos
    carta_propuesta = models.FileField(
        upload_to='cartas_contrato/', 
        blank=True, 
        null=True,
        help_text="Carta de propuesta oficial de la empresa"
    )
    documento_empresa = models.FileField(
        upload_to='documentos_empresa/', 
        blank=True, 
        null=True,
        help_text="Documentación adicional de la empresa"
    )
    
    # Auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Carta de Fechas"
        verbose_name_plural = "Cartas de Fechas"
        ordering = ['-fecha_solicitud']
    
    def __str__(self):
        return f"Carta de fechas: {self.empresa.nombre} → {self.aprendiz.nombre}"
    
    @property
    def duracion_dias(self):
        """Calcula la duración del contrato en días"""
        if self.fecha_inicio_propuesta and self.fecha_fin_propuesta:
            return (self.fecha_fin_propuesta - self.fecha_inicio_propuesta).days
        return None
    
    @property
    def duracion_meses(self):
        """Calcula la duración del contrato en meses (aproximado)"""
        dias = self.duracion_dias
        if dias:
            return round(dias / 30.44, 1)  # Promedio de días por mes
        return None
    
    def puede_ser_editada(self):
        """Verifica si la carta puede ser editada"""
        return self.estado == 'PENDIENTE'
    
    def esta_aprobada(self):
        """Verifica si la carta está aprobada"""
        return self.estado == 'APROBADA'
    
    def esta_completada(self):
        """Verifica si el contrato está completado"""
        return self.estado == 'COMPLETADA'
