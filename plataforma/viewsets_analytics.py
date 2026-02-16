"""
ViewSets para analytics
"""

from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from plataforma.models import Aprendiz, Empresa, Postulacion
from plataforma.models_analytics import EstadisticaDiaria


@extend_schema(exclude=True)
class AnalyticsViewSet(viewsets.ViewSet):
    """
    ViewSet para analytics y dashboard
    GET /api/analytics/resumen/ - Resumen general
    GET /api/analytics/postulaciones-por-estado/ - Gráfico estados
    GET /api/analytics/tendencia/ - Tendencia temporal
    GET /api/analytics/top-empresas/ - Empresas top
    """

    permission_classes = [IsAdminUser]

    @action(detail=False, methods=["get"])
    def resumen(self, request):
        """Resumen general de KPIs"""
        hoy = timezone.now().date()
        hace_30_dias = hoy - timedelta(days=30)

        total_aprendices = Aprendiz.objects.count()
        total_empresas = Empresa.objects.count()
        total_postulaciones = Postulacion.objects.count()

        postulaciones_mes = Postulacion.objects.filter(
            fecha_postulacion__date__gte=hace_30_dias
        ).count()

        seleccionados = Postulacion.objects.filter(
            estado__in=["PROCESO_SELECCION_ABIERTO", "SELECCIONADO"]
        ).count()
        rechazados = Postulacion.objects.filter(
            estado__in=["CONTRATO_NO_REGISTRADO", "RECHAZADO"]
        ).count()
        pendientes = Postulacion.objects.filter(estado="PENDIENTE").count()

        tasa_conversion = (
            (seleccionados / total_postulaciones * 100)
            if total_postulaciones > 0
            else 0
        )

        return Response(
            {
                "usuarios": {
                    "total_aprendices": total_aprendices,
                    "total_empresas": total_empresas,
                    "aprendices_activos": Aprendiz.objects.exclude(
                        estado="INHABILITADO_POR_ACTUALIZACION"
                    ).count(),
                    "empresas_activas": Empresa.objects.filter(
                        estado="DISPONIBLE"
                    ).count(),
                },
                "postulaciones": {
                    "total": total_postulaciones,
                    "este_mes": postulaciones_mes,
                    "seleccionados": seleccionados,
                    "rechazados": rechazados,
                    "pendientes": pendientes,
                    "tasa_conversion": round(tasa_conversion, 2),
                },
                "fecha_reporte": hoy.isoformat(),
            }
        )

    @action(detail=False, methods=["get"])
    def postulaciones_por_estado(self, request):
        """Distribución de postulaciones por estado"""
        estados = Postulacion.objects.values("estado").annotate(count=Count("id"))

        return Response(
            {
                "estados": [
                    {
                        "estado": item["estado"],
                        "cantidad": item["count"],
                        "porcentaje": round(
                            (item["count"] / Postulacion.objects.count() * 100),
                            2,
                        ),
                    }
                    for item in estados
                ]
            }
        )

    @action(detail=False, methods=["get"])
    def tendencia(self, request):
        """Tendencia de postulaciones últimos 30 días"""
        dias = int(request.query_params.get("dias", 30))
        hace_x_dias = timezone.now().date() - timedelta(days=dias)

        estadisticas = EstadisticaDiaria.objects.filter(
            fecha__gte=hace_x_dias
        ).order_by("fecha")

        return Response(
            {
                "tendencia": [
                    {
                        "fecha": stat.fecha.isoformat(),
                        "total_postulaciones": stat.total_postulaciones,
                        "postulaciones_nuevas": stat.postulaciones_nuevas,
                        "postulaciones_seleccionadas": stat.postulaciones_seleccionadas,
                        "tasa_conversion": float(stat.tasa_conversion),
                    }
                    for stat in estadisticas
                ]
            }
        )

    @action(detail=False, methods=["get"])
    def top_empresas(self, request):
        """Top 10 empresas por cantidad de postulaciones"""
        top_empresas = Empresa.objects.annotate(
            total_postulaciones=Count("postulacion"),
            seleccionados=Count(
                "postulacion",
                filter=Q(
                    postulacion__estado__in=[
                        "PROCESO_SELECCION_ABIERTO",
                        "SELECCIONADO",
                    ]
                ),
            ),
        ).order_by("-total_postulaciones")[:10]

        return Response(
            {
                "top_empresas": [
                    {
                        "id": emp.id,
                        "nombre": emp.nombre,
                        "total_postulaciones": emp.total_postulaciones,
                        "seleccionados": emp.seleccionados,
                        "tasa_aceptacion": (
                            round(
                                (emp.seleccionados / emp.total_postulaciones * 100),
                                2,
                            )
                            if emp.total_postulaciones > 0
                            else 0
                        ),
                    }
                    for emp in top_empresas
                ]
            }
        )

    @action(detail=False, methods=["get"])
    def aprendices_exitosos(self, request):
        """Top 10 aprendices con más postulaciones seleccionadas"""
        top_aprendices = (
            Aprendiz.objects.annotate(
                total_postulaciones=Count("postulacion"),
                seleccionados=Count(
                    "postulacion",
                    filter=Q(
                        postulacion__estado__in=[
                            "PROCESO_SELECCION_ABIERTO",
                            "SELECCIONADO",
                        ]
                    ),
                ),
            )
            .filter(seleccionados__gt=0)
            .order_by("-seleccionados")[:10]
        )

        return Response(
            {
                "aprendices_exitosos": [
                    {
                        "id": apr.id,
                        "nombre": f"{apr.nombres} {apr.apellidos}",
                        "total_postulaciones": apr.total_postulaciones,
                        "seleccionados": apr.seleccionados,
                        "tasa_exito": (
                            round(
                                (apr.seleccionados / apr.total_postulaciones * 100),
                                2,
                            )
                            if apr.total_postulaciones > 0
                            else 0
                        ),
                    }
                    for apr in top_aprendices
                ]
            }
        )

    @action(detail=False, methods=["get"])
    def salud_sistema(self, request):
        """Estado general de salud del sistema"""
        total_usuarios = Aprendiz.objects.count() + Empresa.objects.count()
        total_transacciones = Postulacion.objects.count()
        usuarios_activos_7_dias = (
            Aprendiz.objects.filter(
                fecha_ultima_actividad__gte=timezone.now() - timedelta(days=7)
            ).count()
            + Empresa.objects.filter(
                # Asumiendo que la empresa tenga similar campo
            ).count()
        )

        return Response(
            {
                "total_usuarios": total_usuarios,
                "usuarios_activos_7_dias": usuarios_activos_7_dias,
                "total_transacciones": total_transacciones,
                "salud": (
                    "Verde"
                    if usuarios_activos_7_dias > total_usuarios * 0.3
                    else "Amarilla"
                ),
                "timestamp": timezone.now().isoformat(),
            }
        )
