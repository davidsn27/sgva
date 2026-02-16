import csv

from django.contrib import admin
from django.http import HttpResponse

from .models import Aprendiz, Empresa, Perfil, Postulacion


def export_as_csv(modeladmin, request, queryset):
    meta = modeladmin.model._meta
    field_names = [field.name for field in meta.fields]
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f"attachment; filename={meta.verbose_name_plural}.csv"
    writer = csv.writer(response)
    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])
    return response


export_as_csv.short_description = "Exportar seleccionados a CSV"


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "nit",
        "estado",
        "capacidad_cupos",
        "telefono_contacto",
        "correo_contacto",
    )
    search_fields = ("nombre", "nit", "correo_contacto")
    list_filter = ("estado",)
    actions = [export_as_csv]


@admin.register(Aprendiz)
class AprendizAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo_identificacion", "numero_identificacion", "correo", "telefono", "estado", "empresa_actual")
    search_fields = ("nombre", "numero_identificacion", "correo", "telefono")
    list_filter = ("estado", "empresa_actual")
    actions = [export_as_csv]


@admin.register(Postulacion)
class PostulacionAdmin(admin.ModelAdmin):
    list_display = (
        "aprendiz",
        "empresa",
        "fecha_postulacion",
        "estado",
        "fecha_estado_actualizado",
    )
    search_fields = ("aprendiz__nombre", "empresa__nombre")
    list_filter = ("estado", "empresa")
    actions = [export_as_csv]


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("usuario", "rol", "aprendiz")
    search_fields = ("usuario__username", "rol")
    list_filter = ("rol",)
    actions = [export_as_csv]
