from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views, viewsets, viewsets_analytics, viewsets_ratings, views_index

# Crear router para API REST
router = DefaultRouter()
router.register(r"aprendices", viewsets.AprendizViewSet, basename="aprendiz")
router.register(r"empresas", viewsets.EmpresaViewSet, basename="empresa")
router.register(r"postulaciones", viewsets.PostulacionViewSet, basename="postulacion")
router.register(
    r"historial", viewsets.HistorialPostulacionViewSet, basename="historial"
)
router.register(
    r"calificaciones",
    viewsets_ratings.CalificacionViewSet,
    basename="calificacion",
)
router.register(
    r"promedios",
    viewsets_ratings.PromedioCalificacionViewSet,
    basename="promedio",
)
router.register(r"analytics", viewsets_analytics.AnalyticsViewSet, basename="analytics")

urlpatterns = [
    # API REST
    path("api/", include(router.urls)),
    # Vista principal (index)
    path("", views_index.index_view, name="index"),
    # Vista de información (para usuarios autenticados)
    path("inicio/", views.inicio, name="inicio"),
    # Vistas tradicionales
    path("dashboard/", views.dashboard_reportes, name="dashboard_reportes"),
    path("empresas/", views.lista_empresas, name="lista_empresas"),
    path(
        "empresas/<int:empresa_id>/",
        views.detalle_empresa,
        name="detalle_empresa",
    ),
    path(
        "empresas/<int:empresa_id>/editar/",
        views.editar_empresa,
        name="editar_empresa",
    ),
    path("aprendices/", views.lista_aprendices, name="lista_aprendices"),
    path(
        "aprendices/<int:aprendiz_id>/",
        views.detalle_aprendiz,
        name="detalle_aprendiz",
    ),
    path(
        "aprendices/<int:aprendiz_id>/editar/",
        views.editar_aprendiz,
        name="editar_aprendiz",
    ),
    path(
        "postular/<int:aprendiz_id>/<int:empresa_id>/",
        views.postular,
        name="postular",
    ),
    path("registro/empresa/", views.registro_empresa, name="registro_empresa"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout_view"),
    path("oportunidades/", views.oportunidades, name="oportunidades"),
    path("api/oportunidades/", views.api_oportunidades, name="api_oportunidades"),
    path("api/postularse/", views.api_postularse, name="api_postularse"),
    path("mis-postulaciones/", views.mis_postulaciones, name="mis_postulaciones"),
    path(
        "postulaciones/",
        views.postulaciones_funcionario,
        name="postulaciones_funcionario",
    ),
    path(
        "postulacion/<int:id>/",
        views.detalle_postulacion_aprendiz,
        name="detalle_postulacion_aprendiz",
    ),
    path(
        "postulaciones-recibidas/",
        views.postulaciones_recibidas,
        name="postulaciones_recibidas",
    ),
    path(
        "postulacion-empresa/<int:id>/",
        views.detalle_postulacion_empresa,
        name="detalle_postulacion_empresa",
    ),
    path(
        "panel-funcionarios/",
        views.panel_funcionarios,
        name="panel_funcionarios",
    ),
    path(
        "registrar-aprendiz/",
        views.registrar_aprendiz_funcionario,
        name="registrar_aprendiz_funcionario",
    ),
    path("mi-perfil/", views.mi_perfil, name="mi_perfil"),
    # Páginas de información pública
    path("info/empresas/", views.info_empresas, name="info_empresas"),
    path("info/aprendices/", views.info_aprendices, name="info_aprendices"),
    path("info/funcionalidad/", views.info_funcionalidad, name="info_funcionalidad"),
    # Dashboard de estadísticas para funcionarios
    path("estadisticas/", views.dashboard_estadisticas, name="dashboard_estadisticas"),
    # Importación de datos
    path("importar-datos/", views.importar_datos, name="importar_datos"),
    path("procesar-importacion/", views.procesar_importacion, name="procesar_importacion"),
]
