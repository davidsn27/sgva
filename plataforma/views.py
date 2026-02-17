import json
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import (
    Aprendiz,
    Empresa,
    HistorialPostulacion,
    Perfil,
    Postulacion,
)


def marcar_vencida_y_actualizar(postulacion):
    """Marca postulación como CONTRATO_NO_REGISTRADO si está vencida.

    Verifica el estado actual para evitar escrituras innecesarias.
    """
    try:
        ahora = timezone.now()
        fecha_vencimiento = postulacion.fecha_postulacion + timedelta(days=15)
        dias_restantes = (fecha_vencimiento - ahora).days
        if dias_restantes < 0:
            aprendiz = postulacion.aprendiz
            changed = False
            # Actualizar estado de la postulacion si es necesario
            if postulacion.estado != "CONTRATO_NO_REGISTRADO":
                postulacion.estado = "CONTRATO_NO_REGISTRADO"
                postulacion.save()
                changed = True
            # Actualizar estado del aprendiz si es necesario
            if aprendiz.estado != "CONTRATO_NO_REGISTRADO":
                aprendiz.estado = "CONTRATO_NO_REGISTRADO"
                aprendiz.fecha_ultima_actividad = ahora
                aprendiz.save()
                changed = True
            return changed
    except Exception:
        # No propagar errores de esta verificacion para evitar romper la vista
        return False
    return False


def home(request):
    """Página de bienvenida pública"""
    return render(request, 'plataforma/home.html')


@login_required(login_url="login")
def inicio(request):
    """Vista principal del sistema"""
    try:
        # Verificar si el usuario tiene perfil
        perfil = getattr(request.user, "perfil", None)
        if not perfil:
            return redirect("mi_perfil")

        # Obtener estadísticas generales
        total_aprendices = Aprendiz.objects.count()
        total_empresas = Empresa.objects.count()
        total_postulaciones = Postulacion.objects.count()

        # Estadísticas por estado
        aprendices_disponibles = Aprendiz.objects.filter(estado="DISPONIBLE").count()
        aprendices_seleccionados = Aprendiz.objects.filter(estado="PROCESO_SELECCION_ABIERTO").count()
        aprendices_contratados = Aprendiz.objects.filter(estado="CONTRATADO").count()

        # Actividad reciente
        postulaciones_recientes = Postulacion.objects.order_by("-fecha_postulacion")[:5]
        aprendices_recientes = Aprendiz.objects.order_by("-fecha_registro")[:5]

        context = {
            "total_aprendices": total_aprendices,
            "total_empresas": total_empresas,
            "total_postulaciones": total_postulaciones,
            "aprendices_disponibles": aprendices_disponibles,
            "aprendices_seleccionados": aprendices_seleccionados,
            "aprendices_contratados": aprendices_contratados,
            "postulaciones_recientes": postulaciones_recientes,
            "aprendices_recientes": aprendices_recientes,
            "mostrar_boton_registro": True,
        }
        
        # DEPURACIÓN: Imprimir datos que se envían al template
        print("=== DATOS ENVIADOS AL TEMPLATE ===")
        print(f"total_aprendices: {total_aprendices}")
        print(f"total_empresas: {total_empresas}")
        print(f"total_postulaciones: {total_postulaciones}")
        print(f"aprendices_disponibles: {aprendices_disponibles}")
        print(f"aprendices_seleccionados: {aprendices_seleccionados}")
        print(f"aprendices_contratados: {aprendices_contratados}")
        print(f"postulaciones_recientes count: {len(postulaciones_recientes)}")
        print(f"aprendices_recientes count: {len(aprendices_recientes)}")
        print("=====================================")
        
        return render(request, "plataforma/inicio.html", context)
        
    except Exception as e:
        print(f"Error en vista inicio: {e}")
        return redirect("login")


@login_required(login_url="login")
def lista_empresas(request):
    """Lista todas las empresas del sistema con filtros y busqueda"""
    empresas = Empresa.objects.all().order_by("nombre")

    # Filtro por estado
    estado_filtro = request.GET.get("estado", "").strip()
    if estado_filtro:
        empresas = empresas.filter(estado=estado_filtro)

    # Busqueda por nombre o NIT
    busqueda = request.GET.get("q", "").strip()
    if busqueda and busqueda != "None":
        empresas = empresas.filter(
            Q(nombre__icontains=busqueda) | Q(nit__icontains=busqueda)
        )

    # Paginacion
    paginator = Paginator(empresas, 6)
    pagina = request.GET.get("pagina")
    empresas = paginator.get_page(pagina)

    return render(
        request,
        "plataforma/empresas.html",
        {
            "empresas": empresas,
            "estado_filtro": estado_filtro,
            "busqueda": busqueda,
        },
    )


@login_required(login_url="login")
def detalle_empresa(request, empresa_id):
    """Vista detalle de una empresa"""
    empresa = get_object_or_404(Empresa, pk=empresa_id)
    postulaciones = Postulacion.objects.filter(empresa=empresa)
    aprendices = Aprendiz.objects.filter(empresa_actual=empresa)

    return render(
        request,
        "plataforma/detalle_empresa.html",
        {
            "empresa": empresa,
            "postulaciones": postulaciones,
            "aprendices": aprendices,
        },
    )


@login_required(login_url="login")
def lista_aprendices(request):
    """Lista todos los aprendices del sistema con filtros y busqueda"""
    # Verificar si el usuario tiene perfil
    try:
        perfil = request.user.perfil
    except Exception as e:
        # Si no tiene perfil, redirigir a crear perfil
        print(f"Error al acceder al perfil: {e}")
        return redirect('mi_perfil')
    
    aprendices = Aprendiz.objects.all().order_by("nombre")
    
    # Depuración: mostrar total antes de filtros
    print(f"DEBUG: Total aprendices en BD: {Aprendiz.objects.count()}")
    print(f"DEBUG: Total aprendices antes de filtros: {aprendices.count()}")

    # Filtro por estado
    estado_filtro = request.GET.get("estado", "").strip()
    if estado_filtro:
        aprendices = aprendices.filter(estado=estado_filtro)

    # Filtro por empresa
    empresa_filtro = request.GET.get("empresa", "").strip()
    if empresa_filtro:
        aprendices = aprendices.filter(empresa_actual_id=empresa_filtro)

    # Filtro por número de ficha
    ficha_filtro = request.GET.get("ficha", "").strip()
    if ficha_filtro:
        aprendices = aprendices.filter(ficha__icontains=ficha_filtro)

    # Filtro por programa de formación
    programa_filtro = request.GET.get("programa", "").strip()
    if programa_filtro:
        aprendices = aprendices.filter(programa_formacion__icontains=programa_filtro)

    # Busqueda por nombre o correo
    busqueda = request.GET.get("q", "").strip()
    if busqueda and busqueda != "None":
        aprendices = aprendices.filter(
            Q(nombre__icontains=busqueda) | Q(correo__icontains=busqueda)
        )

    # Paginacion - 5 registros por página con opción de mostrar todos
    mostrar_todos = request.GET.get("todos") == "true"
    
    print(f"DEBUG: Después de filtros: {aprendices.count()}")
    print(f"DEBUG: mostrar_todos = {mostrar_todos}")
    
    if mostrar_todos:
        # Mostrar todos sin paginación
        aprendices = aprendices
        paginator = None
        print(f"DEBUG: Mostrando todos: {aprendices.count()}")
    else:
        # Paginación normal de 5 en 5
        paginator = Paginator(aprendices, 5)
        pagina = request.GET.get("pagina")
        aprendices = paginator.get_page(pagina)
        print(f"DEBUG: Paginación: {aprendices.paginator.count} total, {len(aprendices)} en esta página")

    # Agregar información de postulación a cada aprendiz
    for aprendiz in aprendices:
        # Obtener la postulación más reciente del aprendiz
        postulacion_reciente = (
            Postulacion.objects.filter(aprendiz=aprendiz)
            .order_by("-fecha_postulacion")
            .first()
        )
        aprendiz.postulacion_reciente = postulacion_reciente

        if postulacion_reciente:
            # Calcular días desde la postulación
            ahora = timezone.now()
            diferencia = ahora - postulacion_reciente.fecha_postulacion
            aprendiz.dias_desde_postulacion = diferencia.days

            # Calcular fecha de vencimiento (15 días)
            fecha_vencimiento = postulacion_reciente.fecha_postulacion + timedelta(
                days=15
            )
            aprendiz.fecha_vencimiento = fecha_vencimiento

            # Calcular días restantes
            dias_restantes = (fecha_vencimiento - ahora).days
            aprendiz.vencida = dias_restantes < 0
            # Usar valor absoluto si está vencida
            if dias_restantes < 0:
                aprendiz.dias_restantes = abs(dias_restantes)
            else:
                aprendiz.dias_restantes = dias_restantes
            # Calcular porcentaje para barra de progreso (0-100)
            if aprendiz.vencida:
                aprendiz.porcentaje_progreso = 100
                aprendiz.color_progreso = "danger"
                # Si la postulacion esta vencida, actualizar estados en BD
                try:
                    marcar_vencida_y_actualizar(postulacion_reciente)
                except Exception:
                    pass
            else:
                porcentaje = int((aprendiz.dias_restantes / 15) * 100)
                aprendiz.porcentaje_progreso = porcentaje
                if aprendiz.dias_restantes <= 3:
                    aprendiz.color_progreso = "danger"
                elif aprendiz.dias_restantes <= 7:
                    aprendiz.color_progreso = "warning"
                else:
                    aprendiz.color_progreso = "success"
        else:
            aprendiz.dias_desde_postulacion = None
            aprendiz.fecha_vencimiento = None
            aprendiz.dias_restantes = None
            aprendiz.vencida = False
            aprendiz.porcentaje_progreso = 0

    empresas = Empresa.objects.all()

    return render(
        request,
        "plataforma/aprendices.html",
        {
            "aprendices": aprendices,
            "empresas": empresas,
            "estado_filtro": estado_filtro,
            "empresa_filtro": empresa_filtro,
            "ficha_filtro": ficha_filtro,
            "programa_filtro": programa_filtro,
            "busqueda": busqueda,
            "mostrar_todos": mostrar_todos,
        },
    )


def detalle_aprendiz(request, aprendiz_id):
    """Vista detalle de un aprendiz"""
    aprendiz = get_object_or_404(Aprendiz, pk=aprendiz_id)
    postulaciones = Postulacion.objects.filter(aprendiz=aprendiz).order_by(
        "-fecha_postulacion"
    )

    # Agregar cálculo de días a cada postulación
    ahora = timezone.now()
    for postulacion in postulaciones:
        diferencia = ahora - postulacion.fecha_postulacion
        postulacion.dias_desde_postulacion = diferencia.days

        # Calcular fecha de vencimiento (15 días)
        fecha_vencimiento = postulacion.fecha_postulacion + timedelta(days=15)
        postulacion.fecha_vencimiento = fecha_vencimiento

        # Calcular días restantes
        dias_restantes = (fecha_vencimiento - ahora).days
        postulacion.vencida = dias_restantes < 0
        # Usar valor absoluto si está vencida
        if dias_restantes < 0:
            postulacion.dias_restantes = abs(dias_restantes)
        else:
            postulacion.dias_restantes = dias_restantes
        # Calcular porcentaje para barra de progreso
        if postulacion.vencida:
            postulacion.porcentaje_progreso = 100
            postulacion.color_progreso = "danger"
            # Persistir cambio si esta vencida
            try:
                marcar_vencida_y_actualizar(postulacion)
            except Exception:
                pass
        else:
            porcentaje = int((postulacion.dias_restantes / 15) * 100)
            postulacion.porcentaje_progreso = porcentaje
            if postulacion.dias_restantes <= 3:
                postulacion.color_progreso = "danger"
            elif postulacion.dias_restantes <= 7:
                postulacion.color_progreso = "warning"
            else:
                postulacion.color_progreso = "success"

    # Buscar postulacion activa (estados abiertos/pendientes)
    postulacion_activa = (
        Postulacion.objects.filter(
            aprendiz=aprendiz,
            estado__in=[
                "PROCESO_SELECCION_ABIERTO",
                "PENDIENTE",
                "CONTRATADO",
            ],
        )
        .order_by("-fecha_postulacion")
        .first()
    )

    # Determinar empresa del proceso
    if aprendiz.empresa_actual:
        empresa_proceso = aprendiz.empresa_actual
    elif postulacion_activa:
        empresa_proceso = postulacion_activa.empresa
    else:
        empresa_proceso = None

    return render(
        request,
        "plataforma/detalle_aprendiz.html",
        {
            "aprendiz": aprendiz,
            "postulaciones": postulaciones,
            "empresa_proceso": empresa_proceso,
            "postulacion_activa": postulacion_activa,
        },
    )


def postular(request, aprendiz_id, empresa_id):
    """Registra la postulacion de un aprendiz a una empresa"""
    aprendiz = get_object_or_404(Aprendiz, pk=aprendiz_id)
    empresa = get_object_or_404(Empresa, pk=empresa_id)

    # Validar que la empresa esté disponible
    if empresa.estado != "DISPONIBLE":
        msg = "Esta empresa no está disponible para postulaciones."
        messages.error(request, msg)
        return redirect("lista_empresas")

    # Validar que el aprendiz esté disponible
    if aprendiz.estado != "DISPONIBLE":
        msg = (
            "No puedes postularte porque tu estado es "
            "'En proceso de selección' o no estás disponible. "
            "Espera a que se actualice tu estado para postularte "
            "a otra empresa."
        )
        messages.error(request, msg)
        return redirect("lista_empresas")

    # Validar que no exista postulación previa a esta empresa
    postulacion_existente = Postulacion.objects.filter(
        aprendiz=aprendiz, empresa=empresa
    ).first()
    if postulacion_existente:
        msg = "Ya te has postulado a esta empresa. " "No puedes volver a postularte."
        messages.warning(request, msg)
        return redirect("lista_empresas")

    # Validar que el aprendiz no tenga postulaciones activas
    # (PENDIENTE, PROCESO_SELECCION_ABIERTO o CONTRATADO)
    postulaciones_activas = Postulacion.objects.filter(
        aprendiz=aprendiz,
        estado__in=["PENDIENTE", "PROCESO_SELECCION_ABIERTO", "CONTRATADO"],
    )
    if postulaciones_activas.exists():
        msg = (
            "No puedes postularte a más de una empresa hasta que tu "
            "postulación actual sea resuelta."
        )
        messages.error(request, msg)
        return redirect("lista_empresas")

    # Crear postulación
    Postulacion.objects.create(
        aprendiz=aprendiz,
        empresa=empresa,
        fecha_postulacion=timezone.now(),
        estado="PENDIENTE",
    )

    aprendiz.estado = "PROCESO_SELECCION"
    aprendiz.fecha_ultima_actividad = timezone.now()
    aprendiz.save()

    msg = (
        f"Postulación de {aprendiz.nombre} a {empresa.nombre} "
        "registrada exitosamente."
    )
    messages.success(request, msg)
    return redirect("lista_empresas")


# ===== NUEVAS VISTAS: EDICION, REPORTES Y AUTENTICACION =====


@login_required(login_url="login")
def editar_empresa(request, empresa_id):
    """Edita los datos de una empresa"""
    empresa = get_object_or_404(Empresa, pk=empresa_id)

    if request.method == "POST":
        empresa.nombre = request.POST.get("nombre", empresa.nombre)
        empresa.nit = request.POST.get("nit", empresa.nit)
        empresa.estado = request.POST.get("estado", empresa.estado)
        empresa.direccion = request.POST.get("direccion", empresa.direccion)
        empresa.descripcion = request.POST.get("descripcion", empresa.descripcion)
        empresa.telefono_contacto = request.POST.get(
            "telefono_contacto", empresa.telefono_contacto
        )
        empresa.correo_contacto = request.POST.get(
            "correo_contacto", empresa.correo_contacto
        )

        capacidad_cupos_raw = request.POST.get("capacidad_cupos", empresa.capacidad_cupos)
        try:
            capacidad_cupos_int = int(capacidad_cupos_raw)
            if capacidad_cupos_int < 0:
                capacidad_cupos_int = 0
            empresa.capacidad_cupos = capacidad_cupos_int
        except (TypeError, ValueError):
            pass

        empresa.observacion = request.POST.get("observacion", empresa.observacion)

        try:
            empresa.save()
        except IntegrityError:
            messages.error(request, "El NIT ya está registrado en otra empresa")
            return render(request, "plataforma/editar_empresa.html", {"empresa": empresa})

        msg = f"Empresa {empresa.nombre} actualizada correctamente"
        messages.success(request, msg)
        return redirect("detalle_empresa", empresa_id=empresa.id)

    context = {"empresa": empresa}
    return render(request, "plataforma/editar_empresa.html", context)


def editar_aprendiz(request, aprendiz_id):
    """Edita los datos de un aprendiz"""
    aprendiz = get_object_or_404(Aprendiz, pk=aprendiz_id)

    if request.method == "POST":
        aprendiz.nombre = request.POST.get("nombre", aprendiz.nombre)
        aprendiz.correo = request.POST.get("correo", aprendiz.correo)
        aprendiz.telefono = request.POST.get("telefono", aprendiz.telefono)
        aprendiz.tipo_identificacion = request.POST.get("tipo_identificacion", aprendiz.tipo_identificacion)
        aprendiz.numero_identificacion = request.POST.get("numero_identificacion", aprendiz.numero_identificacion)
        aprendiz.direccion = request.POST.get("direccion", aprendiz.direccion)
        aprendiz.ficha = request.POST.get("ficha", aprendiz.ficha)
        pf = request.POST.get("programa_formacion", aprendiz.programa_formacion)
        aprendiz.programa_formacion = pf
        aprendiz.estado = request.POST.get("estado", aprendiz.estado)

        empresa_id = request.POST.get("empresa_actual")
        if empresa_id:
            aprendiz.empresa_actual_id = empresa_id
        else:
            aprendiz.empresa_actual = None

        aprendiz.save()

        msg = f"Aprendiz {aprendiz.nombre} actualizado correctamente"
        messages.success(request, msg)
        return redirect("detalle_aprendiz", aprendiz_id=aprendiz.id)

    empresas = Empresa.objects.all()
    return render(
        request,
        "plataforma/editar_aprendiz.html",
        {"aprendiz": aprendiz, "empresas": empresas},
    )


def dashboard_reportes(request):
    """Redirige a la página de postulaciones"""
    
    if not request.user.is_authenticated:
        return redirect("login")
    
    # Redirigir a la página de todas las postulaciones
    return redirect("mis_postulaciones")


# ============== VISTAS DE AUTENTICACION ==============


def registro(request):
    """Muestra la pagina para elegir tipo de registro"""
    return render(request, "plataforma/registro_tipo.html")


def registro_tipo(request):
    """Muestra la pagina para elegir tipo de registro (alias)"""
    return render(request, "plataforma/registro_tipo.html")


def registro_empresa(request):
    """Registra una nueva empresa en el sistema"""
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")
        nombre = request.POST.get("nombre")
        nit = request.POST.get("nit")
        direccion = request.POST.get("direccion", "")
        descripcion = request.POST.get("descripcion", "")
        telefono_contacto = request.POST.get("telefono_contacto", "")
        correo_contacto = request.POST.get("correo_contacto", "")
        capacidad_cupos = request.POST.get("capacidad_cupos", 0)

        # Validaciones
        if not all([username, email, password, nombre, nit]):
            messages.error(request, "Los campos requeridos deben estar completos")
            return render(request, "plataforma/registro_empresa.html")

        if password != password_confirm:
            messages.error(request, "Las contrasenas no coinciden")
            return render(request, "plataforma/registro_empresa.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Este usuario ya existe")
            return render(request, "plataforma/registro_empresa.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Este correo ya esta registrado")
            return render(request, "plataforma/registro_empresa.html")

        if Empresa.objects.filter(nit=nit).exists():
            messages.error(request, "Este NIT ya esta registrado")
            return render(request, "plataforma/registro_empresa.html")

        # Crear usuario
        usuario = User.objects.create_user(
            username=username, email=email, password=password
        )

        # Crear empresa
        try:
            capacidad_cupos = int(capacidad_cupos)
            if capacidad_cupos < 1:
                capacidad_cupos = 1
        except (TypeError, ValueError):
            capacidad_cupos = 1

        empresa = Empresa.objects.create(
            usuario=usuario,
            nombre=nombre,
            nit=nit,
            direccion=direccion,
            descripcion=descripcion,
            telefono_contacto=telefono_contacto,
            correo_contacto=correo_contacto,
            estado="DISPONIBLE",
            capacidad_cupos=capacidad_cupos,
            observacion="Empresa creada recientemente",
        )

        # Crear perfil de trabajador
        Perfil.objects.create(usuario=usuario, rol="TRABAJADOR")

        return redirect("login")

    return render(request, "plataforma/registro_empresa.html")


def login_view(request):
    """Inicia sesion en el sistema"""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        usuario = authenticate(request, username=username, password=password)

        if usuario is not None:
            login(request, usuario)

            # Redirigir según rol
            try:
                perfil = usuario.perfil
                if perfil.rol == "ESTUDIANTE":
                    return redirect("dashboard")
            except:
                pass

            return redirect("inicio")  # Ahora apunta a /panel/
        else:
            messages.error(request, "Usuario o contrasena invalidos")
            return render(request, "plataforma/login.html")

    return render(request, "plataforma/login.html")


def logout_view(request):
    """Cierra sesion del usuario"""
    logout(request)
    return render(request, "plataforma/logout_success.html")


# ============ NUEVAS VISTAS PARA OPORTUNIDADES DE EMPLEO ============


def oportunidades(request):
    """Muestra las oportunidades de empleo disponibles para aprendices"""
    if not request.user.is_authenticated:
        return redirect("login")

    return render(request, "plataforma/oportunidades.html")


@require_http_methods(["GET"])
@login_required
def api_oportunidades(request):
    """API para obtener todas las oportunidades de empleo"""
    empresas = Empresa.objects.filter(estado="DISPONIBLE").order_by("nombre")

    data = []
    for empresa in empresas:
        data.append(
            {
                "id": empresa.id,
                "nombre": empresa.nombre,
                "descripcion": empresa.descripcion or "Sin descripcion",
                "direccion": empresa.direccion or "No especificada",
                "nit": empresa.nit,
                "estado": empresa.estado,
                "estado_label": "Activa",
                "capacidad_cupos": empresa.capacidad_cupos,
                "cupos_disponibles": empresa.cupos_disponibles(),
                "telefono": empresa.telefono_contacto or "No disponible",
                "correo": empresa.correo_contacto or "No disponible",
            }
        )

    return JsonResponse(data, safe=False)


@require_http_methods(["POST"])
@login_required
def api_postularse(request):
    """API para postularse a una empresa"""
    try:
        data = json.loads(request.body)
        empresa_id = data.get("empresa_id")

        # Validar que existe la empresa
        empresa = get_object_or_404(Empresa, id=empresa_id, estado="DISPONIBLE")

        # Verificar que el usuario es un estudiante
        try:
            perfil = request.user.perfil
            if perfil.rol != "ESTUDIANTE":
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Solo los estudiantes pueden postularse",
                    }
                )

            aprendiz = perfil.aprendiz
        except:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Debes completar tu perfil de aprendiz",
                }
            )

        # Verificar que hay cupos disponibles
        if not empresa.tiene_cupos():
            return JsonResponse(
                {
                    "success": False,
                    "message": "Esta empresa ya no tiene cupos disponibles",
                }
            )

        # Verificar que no se ha postulado antes
        postulacion_existente = Postulacion.objects.filter(
            aprendiz=aprendiz, empresa=empresa
        ).first()

        if postulacion_existente:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Ya te has postulado a esta empresa",
                }
            )

        # Verificar que no tiene una postulación activa
        postulacion_activa = Postulacion.objects.filter(
            aprendiz=aprendiz,
            estado__in=[
                "PENDIENTE",
                "PROCESO_SELECCION_ABIERTO",
                "CONTRATADO",
            ],
        ).first()

        if postulacion_activa:
            return JsonResponse(
                {
                    "success": False,
                    "message": f"Ya tienes una postulación activa en {postulacion_activa.empresa.nombre}. Solo puedes postularte a una empresa a la vez.",
                }
            )

        # Verificar regla de 15 días HÁBILES entre postulaciones
        ultima_postulacion = (
            Postulacion.objects.filter(aprendiz=aprendiz)
            .order_by("-fecha_postulacion")
            .first()
        )
        if ultima_postulacion:
            hoy = timezone.now()
            fecha_ultima_post = ultima_postulacion.fecha_postulacion

            dias_habiles_pasados = 0
            fecha_temp = fecha_ultima_post
            while fecha_temp.date() < hoy.date():
                fecha_temp += timedelta(days=1)
                if fecha_temp.weekday() < 5:  # Lunes a Viernes
                    dias_habiles_pasados += 1

            if dias_habiles_pasados < 15:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Solo puedes hacer una postulación cada 15 días hábiles. Intenta de nuevo más tarde.",
                    }
                )

        # Crear la postulacion
        postulacion = Postulacion.objects.create(
            aprendiz=aprendiz,
            empresa=empresa,
            estado="PENDIENTE",
            fecha_postulacion=timezone.now(),
            fecha_estado_actualizado=timezone.now(),
        )

        # Crear historial de estado
        HistorialPostulacion.objects.create(
            postulacion=postulacion,
            estado_anterior="",
            estado_nuevo="PENDIENTE",
            usuario=request.user,
            comentario="Postulacion enviada",
        )

        # Actualizar estado del aprendiz y asignar empresa temporalmente
        aprendiz.estado = "PROCESO_SELECCION"
        aprendiz.empresa_actual = empresa
        aprendiz.fecha_ultima_actividad = timezone.now()
        aprendiz.save()

        return JsonResponse(
            {
                "success": True,
                "message": "Postulacion registrada exitosamente!",
            }
        )

    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"Error: {str(e)}"}, status=400
        )


# ========================
# MIS POSTULACIONES - APRENDIZ
# ========================
@login_required(login_url="login")
def mis_postulaciones(request):
    """Vista para que aprendices vean sus postulaciones"""
    if not request.user.is_authenticated:
        return redirect("login")

    try:
        perfil = request.user.perfil
        if perfil.rol != "ESTUDIANTE":
            return redirect("index")

        aprendiz = perfil.aprendiz
        postulaciones = Postulacion.objects.filter(aprendiz=aprendiz).order_by(
            "-fecha_postulacion"
        )

        # Contar postulaciones por estado
        pendientes = postulaciones.filter(estado="PENDIENTE").count()
        seleccionados = postulaciones.filter(estado="PROCESO_SELECCION_ABIERTO").count()
        rechazados = postulaciones.filter(estado="CONTRATO_NO_REGISTRADO").count()
        contratados = postulaciones.filter(estado="CONTRATADO").count()

        return render(
            request,
            "plataforma/mis_postulaciones.html",
            {
                "postulaciones": postulaciones,
                "pendientes": pendientes,
                "seleccionados": seleccionados,
                "rechazados": rechazados,
                "contratos_nulos": contratados,
                "aprendiz": aprendiz,
            },
        )
    except:
        return redirect("login")


# ========================
# DETALLE DE POSTULACIÓN - APRENDIZ
# ========================
@login_required(login_url="login")
def detalle_postulacion_aprendiz(request, id):
    """Detalle de postulación para aprendiz con observaciones"""
    try:
        postulacion = Postulacion.objects.get(id=id)

        if postulacion.aprendiz.correo != request.user.email:
            return redirect("mis_postulaciones")

        historial = HistorialPostulacion.objects.filter(postulacion=postulacion)

        if request.method == "POST":
            observacion = request.POST.get("observacion", "").strip()

            if observacion:
                postulacion.observacion_aprendiz = observacion
                postulacion.aprendiz_dio_respuesta = True
                postulacion.save()

                # Crear historial
                HistorialPostulacion.objects.create(
                    postulacion=postulacion,
                    estado_anterior=postulacion.estado,
                    estado_nuevo=postulacion.estado,
                    usuario=request.user,
                    comentario=f"Aprendiz agregó observación: {observacion}",
                )

                # Si ambas partes respondieron, cambiar a disponible
                if postulacion.ambas_partes_respondieron():
                    postulacion.estado = "DISPONIBLE"
                    postulacion.save()
                    HistorialPostulacion.objects.create(
                        postulacion=postulacion,
                        estado_anterior="PENDIENTE",
                        estado_nuevo="DISPONIBLE",
                        usuario=None,
                        comentario="Ambas partes respondieron - Estado cambiado a DISPONIBLE",
                    )
                    postulacion.aprendiz.estado = "DISPONIBLE"
                    postulacion.aprendiz.save()

                return redirect("detalle_postulacion_aprendiz", id=id)

        return render(
            request,
            "plataforma/detalle_postulacion_aprendiz.html",
            {
                "postulacion": postulacion,
                "historial": historial,
            },
        )
    except Postulacion.DoesNotExist:
        return redirect("mis_postulaciones")


# ========================
# POSTULACIONES RECIBIDAS - EMPRESA
# ========================
@login_required(login_url="login")
def postulaciones_recibidas(request):
    """Vista para empresas ver postulaciones recibidas"""
    empresa = getattr(request.user, "empresa", None)
    if not empresa:
        return redirect("info_empresas")

    postulaciones = Postulacion.objects.filter(empresa=empresa).order_by(
        "-fecha_postulacion"
    )

    # Contar postulaciones por estado
    pendientes = postulaciones.filter(estado="PENDIENTE").count()
    seleccionados = postulaciones.filter(estado="PROCESO_SELECCION_ABIERTO").count()
    rechazados = postulaciones.filter(estado="CONTRATO_NO_REGISTRADO").count()
    contratados = postulaciones.filter(estado="CONTRATADO").count()

    return render(
        request,
        "plataforma/postulaciones_recibidas.html",
        {
            "postulaciones": postulaciones,
            "pendientes": pendientes,
            "seleccionados": seleccionados,
            "rechazados": rechazados,
            "contratos_nulos": contratados,
            "empresa": empresa,
        },
    )


# ========================
# DETALLE DE POSTULACIÓN - EMPRESA
# ========================
@login_required(login_url="login")
def detalle_postulacion_empresa(request, id):
    """Detalle de postulación para empresa con cambio de estado y observaciones"""
    try:
        postulacion = Postulacion.objects.get(id=id)

        # Permitir acceso si es la empresa dueña O si es funcionario SENA
        es_funcionario = False
        try:
            if request.user.perfil.rol == "FUNCIONARIO_SENA":
                es_funcionario = True
        except Exception:
            pass

        if postulacion.empresa.usuario != request.user and not es_funcionario:
            return redirect("postulaciones_recibidas")

        historial = HistorialPostulacion.objects.filter(postulacion=postulacion)

        if request.method == "POST":
            accion = request.POST.get("accion")
            observacion = request.POST.get("observacion", "").strip()

            estado_anterior = postulacion.estado

            if accion == "seleccionar":
                postulacion.estado = "PROCESO_SELECCION_ABIERTO"
                postulacion.empresa_dio_respuesta = True
                if observacion:
                    postulacion.observacion_empresa = observacion

                # Actualizar aprendiz
                postulacion.aprendiz.estado = "PROCESO_SELECCION_ABIERTO"
                postulacion.aprendiz.empresa_actual = postulacion.empresa
                postulacion.aprendiz.save()

            elif accion == "rechazar":
                postulacion.estado = "CONTRATO_NO_REGISTRADO"
                postulacion.empresa_dio_respuesta = True
                if observacion:
                    postulacion.observacion_empresa = observacion

                # Actualizar aprendiz
                postulacion.aprendiz.estado = "CONTRATO_NO_REGISTRADO"
                postulacion.aprendiz.save()

            elif accion == "contratar":
                postulacion.estado = "CONTRATADO"
                postulacion.empresa_dio_respuesta = True
                if observacion:
                    postulacion.observacion_empresa = observacion

                postulacion.aprendiz.estado = "CONTRATADO"
                postulacion.aprendiz.save()

            elif accion == "observacion":
                postulacion.observacion_empresa = observacion
                postulacion.empresa_dio_respuesta = True

            postulacion.fecha_estado_actualizado = timezone.now()
            postulacion.save()

            # Crear historial
            comentario = f"Empresa {accion}"
            if observacion:
                comentario += f": {observacion}"

            HistorialPostulacion.objects.create(
                postulacion=postulacion,
                estado_anterior=estado_anterior,
                estado_nuevo=postulacion.estado,
                usuario=request.user,
                comentario=comentario,
            )

            # Si ambas partes respondieron, cambiar a disponible
            if (
                postulacion.ambas_partes_respondieron()
                and postulacion.estado == "CONTRATO_NO_REGISTRADO"
            ):
                postulacion.estado = "DISPONIBLE"
                postulacion.save()
                HistorialPostulacion.objects.create(
                    postulacion=postulacion,
                    estado_anterior="CONTRATO_NO_REGISTRADO",
                    estado_nuevo="DISPONIBLE",
                    usuario=None,
                    comentario="Ambas partes respondieron - Estado cambiado a DISPONIBLE",
                )
                postulacion.aprendiz.estado = "DISPONIBLE"
                postulacion.aprendiz.empresa_actual = None
                postulacion.aprendiz.save()

            return redirect("detalle_postulacion_empresa", id=id)

        return render(
            request,
            "plataforma/detalle_postulacion_empresa.html",
            {
                "postulacion": postulacion,
                "historial": historial,
            },
        )
    except Postulacion.DoesNotExist:
        return redirect("postulaciones_recibidas")


# ========================
# PANEL FUNCIONARIOS SENA
# ========================
@login_required(login_url="login")
def panel_funcionarios(request):
    """Panel principal para funcionarios SENA"""
    try:
        perfil = getattr(request.user, "perfil", None)
        if not perfil or perfil.rol != "FUNCIONARIO_SENA":
            return redirect("index")

        # Estadísticas generales
        total_aprendices = Aprendiz.objects.count()
        total_empresas = Empresa.objects.count()
        total_postulaciones = Postulacion.objects.count()

        # Estadísticas por estado
        aprendices_disponibles = Aprendiz.objects.filter(estado="DISPONIBLE").count()
        aprendices_seleccionados = Aprendiz.objects.filter(
            estado="PROCESO_SELECCION_ABIERTO"
        ).count()

        return render(
            request,
            "plataforma/panel_funcionarios.html",
            {
                "total_aprendices": total_aprendices,
                "total_empresas": total_empresas,
                "total_postulaciones": total_postulaciones,
                "aprendices_disponibles": aprendices_disponibles,
                "aprendices_seleccionados": aprendices_seleccionados,
                "mostrar_boton_registro": True,
            },
        )
    except Exception as e:
        return redirect("login")


# ========================
# REGISTRAR APRENDICES - FUNCIONARIOS SENA
# ========================
@login_required(login_url="login")
@login_required(login_url="login")
def registro_aprendiz(request):
    """Muestra el formulario de registro para aprendices"""
    return render(request, "plataforma/registro_aprendiz.html")


def registrar_aprendiz_funcionario(request):
    """Vista para que funcionarios SENA registren aprendices"""
    try:
        perfil = request.user.perfil
        if perfil.rol != "FUNCIONARIO_SENA":
            return redirect("index")

        if request.method == "POST":
            nombre = request.POST.get("nombre", "").strip()
            numero_identificacion = request.POST.get(
                "numero_identificacion", ""
            ).strip()
            tipo_identificacion = request.POST.get("tipo_identificacion", "").strip()
            correo = request.POST.get("correo", "").strip()
            telefono = request.POST.get("telefono", "").strip()
            direccion = request.POST.get("direccion", "").strip()
            ficha = request.POST.get("ficha", "").strip()
            programa_formacion = request.POST.get("programa_formacion", "").strip()

            password = request.POST.get("password", "").strip()
            password_confirm = request.POST.get("password_confirm", "").strip()

            # Validar campos obligatorios
            if not all(
                [
                    nombre,
                    numero_identificacion,
                    tipo_identificacion,
                    correo,
                    telefono,
                    ficha,
                    programa_formacion,
                    password,
                    password_confirm,
                ]
            ):
                messages.error(request, "Completa todos los campos obligatorios")
                return render(request, "plataforma/registrar_aprendiz_funcionario.html")

            if password != password_confirm:
                messages.error(request, "Las contraseñas no coinciden")
                return render(request, "plataforma/registrar_aprendiz_funcionario.html")

            # Validar que no exista usuario con ese username (cedula)
            if User.objects.filter(username=numero_identificacion).exists():
                messages.error(
                    request,
                    "Ya existe un usuario con ese número de identificación",
                )
                return render(request, "plataforma/registrar_aprendiz_funcionario.html")

            # Validar que no exista aprendiz con mismo correo
            if Aprendiz.objects.filter(correo=correo).exists():
                messages.error(request, "El correo ya está registrado")
                return render(request, "plataforma/registrar_aprendiz_funcionario.html")

            # Crear usuario Django para el aprendiz
            usuario = User.objects.create_user(
                username=numero_identificacion,
                email=correo,
                password=password,
                first_name=nombre,
            )

            # Crear aprendiz y asociar usuario
            aprendiz = Aprendiz.objects.create(
                nombre=nombre,
                correo=correo,
                telefono=telefono,
                tipo_identificacion=tipo_identificacion,
                numero_identificacion=numero_identificacion,
                direccion=direccion,
                ficha=ficha,
                programa_formacion=programa_formacion,
                estado="DISPONIBLE",
            )

            # Crear perfil para el usuario
            Perfil.objects.create(usuario=usuario, rol="ESTUDIANTE", aprendiz=aprendiz)

            messages.success(
                request,
                f"Aprendiz {nombre} registrado exitosamente. Usuario: {numero_identificacion}",
            )
            return redirect("registrar_aprendiz_funcionario")

        return render(request, "plataforma/registrar_aprendiz_funcionario.html")
    except:
        return redirect("login")


# ========================
# PERFIL DE USUARIO
# ========================
@login_required(login_url="login")
def mi_perfil(request):
    """Ver y editar perfil del usuario"""
    perfil = request.user.perfil

    if request.method == "POST":
        # Actualizar información del usuario
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.save()

        # Actualizar información según el rol
        if perfil.rol == "ESTUDIANTE" and perfil.aprendiz:
            telefono = request.POST.get("telefono", "").strip()
            perfil.aprendiz.telefono = telefono
            perfil.aprendiz.save()

        elif perfil.rol == "TRABAJADOR":
            try:
                empresa = request.user.empresa
                empresa.descripcion = request.POST.get("descripcion", "").strip()
                empresa.direccion = request.POST.get("direccion", "").strip()
                empresa.save()
            except:
                pass

        messages.success(request, "Perfil actualizado exitosamente")
        return redirect("mi_perfil")

    context = {
        "perfil": perfil,
    }

    if perfil.rol == "ESTUDIANTE" and perfil.aprendiz:
        context["aprendiz"] = perfil.aprendiz
    elif perfil.rol == "TRABAJADOR":
        try:
            context["empresa"] = request.user.empresa
        except:
            pass

    return render(request, "plataforma/mi_perfil.html", context)


def info_empresas(request):
    """Vista de información pública sobre empresas"""
    return render(request, "plataforma/info_empresas.html")


def info_aprendices(request):
    """Vista de información pública sobre aprendices"""
    return render(request, "plataforma/info_aprendices.html")


def info_funcionalidad(request):
    """Vista de información pública sobre la plataforma"""
    return render(request, "plataforma/info_funcionalidad.html")


@login_required(login_url="login")
def postulaciones_funcionario(request):
    estado = request.GET.get("estado")

    postulaciones = Postulacion.objects.select_related("aprendiz", "empresa").order_by(
        "-fecha_postulacion"
    )
    if estado:
        postulaciones = postulaciones.filter(estado=estado)

    pendientes = Postulacion.objects.filter(estado="PENDIENTE").count()
    seleccionados = Postulacion.objects.filter(estado="PROCESO_SELECCION_ABIERTO").count()
    contrato_no_registrado = Postulacion.objects.filter(
        estado="CONTRATO_NO_REGISTRADO"
    ).count()
    contratados = Postulacion.objects.filter(estado="CONTRATADO").count()

    return render(
        request,
        "plataforma/postulaciones_funcionario.html",
        {
            "postulaciones": postulaciones,
            "pendientes": pendientes,
            "seleccionados": seleccionados,
            "contrato_no_registrado": contrato_no_registrado,
            "contratados": contratados,
            "estado_actual": estado or "",
        },
    )


@login_required(login_url="login")
def dashboard_estadisticas(request):
    """Dashboard de estadísticas generales para funcionarios SENA"""
    from django.db.models import Count, Q
    from django.utils import timezone
    from datetime import timedelta
    
    # Obtener parámetros de filtro
    filter_type = request.GET.get('filter', '')
    filter_value = request.GET.get('value', '')
    
    # Estadísticas generales
    total_aprendices = Aprendiz.objects.count()
    total_empresas = Empresa.objects.count()
    total_postulaciones = Postulacion.objects.count()
    
    # Aplicar filtros si existen
    if filter_type == 'aprendices' and filter_value:
        total_aprendices = Aprendiz.objects.filter(estado=filter_value).count()
    elif filter_type == 'empresas' and filter_value:
        total_empresas = Empresa.objects.filter(estado=filter_value).count()
    elif filter_type == 'postulaciones' and filter_value:
        total_postulaciones = Postulacion.objects.filter(estado=filter_value).count()
    
    # Estadísticas de aprendices por estado
    aprendices_por_estado = Aprendiz.objects.values('estado').annotate(
        count=Count('id')
    ).order_by('estado')
    
    # Estados de aprendices para estadísticas generales
    estados_aprendices = [
        {
            'key': 'DISPONIBLE',
            'label': 'Disponible',
            'count': Aprendiz.objects.filter(estado='DISPONIBLE').count()
        },
        {
            'key': 'PROCESO_SELECCION',
            'label': 'Proceso de selección',
            'count': Aprendiz.objects.filter(estado='PROCESO_SELECCION').count()
        },
        {
            'key': 'PROCESO_SELECCION_ABIERTO',
            'label': 'Proceso de selección abierto',
            'count': Aprendiz.objects.filter(estado='PROCESO_SELECCION_ABIERTO').count()
        },
        {
            'key': 'CONTRATO_NO_REGISTRADO',
            'label': 'Contrato no registrado',
            'count': Aprendiz.objects.filter(estado='CONTRATO_NO_REGISTRADO').count()
        },
        {
            'key': 'CONTRATADO',
            'label': 'Contratado',
            'count': Aprendiz.objects.filter(estado='CONTRATADO').count()
        },
        {
            'key': 'INHABILITADO_POR_ACTUALIZACION',
            'label': 'Inhabilitado por actualización',
            'count': Aprendiz.objects.filter(estado='INHABILITADO_POR_ACTUALIZACION').count()
        }
    ]
    
    # Estadísticas de empresas por estado
    empresas_por_estado = Empresa.objects.values('estado').annotate(
        count=Count('id')
    ).order_by('estado')
    
    # Estadísticas de postulaciones por estado
    postulaciones_por_estado = Postulacion.objects.values('estado').annotate(
        count=Count('id')
    ).order_by('estado')
    
    # Estados de postulaciones para estadísticas generales
    estados_postulaciones = [
        {
            'key': 'PENDIENTE',
            'label': 'En proceso de selección',
            'count': Postulacion.objects.filter(estado='PENDIENTE').count()
        },
        {
            'key': 'PROCESO_SELECCION_ABIERTO',
            'label': 'Proceso de selección abierto',
            'count': Postulacion.objects.filter(estado='PROCESO_SELECCION_ABIERTO').count()
        },
        {
            'key': 'CONTRATO_NO_REGISTRADO',
            'label': 'Contrato no registrado',
            'count': Postulacion.objects.filter(estado='CONTRATO_NO_REGISTRADO').count()
        },
        {
            'key': 'CONTRATADO',
            'label': 'Contratado',
            'count': Postulacion.objects.filter(estado='CONTRATADO').count()
        },
        {
            'key': 'RECHAZADA',
            'label': 'Rechazada',
            'count': Postulacion.objects.filter(estado='RECHAZADA').count()
        },
        {
            'key': 'DISPONIBLE',
            'label': 'Disponible',
            'count': Postulacion.objects.filter(estado='DISPONIBLE').count()
        }
    ]
    
    # Estadísticas del último mes
    hace_30_dias = timezone.now() - timedelta(days=30)
    postulaciones_ultimo_mes = Postulacion.objects.filter(
        fecha_postulacion__gte=hace_30_dias
    ).count()
    
    # Top 5 empresas con más postulaciones
    top_empresas = Empresa.objects.annotate(
        total_postulaciones=Count('postulacion')
    ).order_by('-total_postulaciones')[:5]
    
    # Top 5 aprendices con más postulaciones aceptadas
    top_aprendices = Aprendiz.objects.annotate(
        postulaciones_aceptadas=Count(
            'postulacion', 
            filter=Q(postulacion__estado='CONTRATADO')
        )
    ).filter(postulaciones_aceptadas__gt=0).order_by('-postulaciones_aceptadas')[:5]
    
    # Datos adicionales para listas filtrables
    todos_aprendices = Aprendiz.objects.all().order_by('nombre')
    todas_postulaciones = Postulacion.objects.all().order_by('-fecha_postulacion')
    
    # Calcular estadísticas adicionales
    aprendices_disponibles = Aprendiz.objects.filter(estado='DISPONIBLE').count()
    aprendices_proceso = Aprendiz.objects.filter(
        estado__in=['PROCESO_SELECCION', 'PROCESO_SELECCION_ABIERTO']
    ).count()
    aprendices_contratados = Aprendiz.objects.filter(estado='CONTRATADO').count()
    empresas_activas = Empresa.objects.filter(estado='ACTIVA').count()
    postulaciones_pendientes = Postulacion.objects.filter(estado='PENDIENTE').count()
    
    # Postulaciones por mes (últimos 6 meses)
    from collections import defaultdict
    postulaciones_mes = defaultdict(int)
    hace_6_meses = timezone.now() - timedelta(days=180)
    
    postulaciones_recientes = Postulacion.objects.filter(
        fecha_postulacion__gte=hace_6_meses
    ).extra({
        'month': "strftime('%%Y-%%m', fecha_postulacion)"
    }).values('month').annotate(count=Count('id')).order_by('month')
    
    for p in postulaciones_recientes:
        month_names = {
            '01': 'Ene', '02': 'Feb', '03': 'Mar', '04': 'Abr',
            '05': 'May', '06': 'Jun', '07': 'Jul', '08': 'Ago',
            '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dic'
        }
        month_key = p['month']
        month_display = f"{month_names.get(month_key[5:], month_key[5:])}"
        postulaciones_mes[month_display] = p['count']
    
    # Calcular tasas
    tasa_contratacion = 0
    if total_postulaciones > 0:
        tasa_contratacion = round((aprendices_contratados / total_postulaciones) * 100, 1)
    
    tasa_seleccion = 0
    if total_aprendices > 0:
        tasa_seleccion = round((aprendices_proceso / total_aprendices) * 100, 1)
    
    tasa_postulacion = 0
    if total_aprendices > 0:
        aprendices_con_postulacion = Aprendiz.objects.filter(
            postulacion__isnull=False
        ).distinct().count()
        tasa_postulacion = round((aprendices_con_postulacion / total_aprendices) * 100, 1)
    
    tasa_retencion = 85  # Simulado - podría calcularse con datos históricos
    
    # Actividad reciente (últimas 10 acciones)
    actividades_recientes = []
    
    # Últimos aprendices creados
    ultimos_aprendices = Aprendiz.objects.order_by('-fecha_ultima_actividad')[:5]
    for aprendiz in ultimos_aprendices:
        actividades_recientes.append({
            'fecha': aprendiz.fecha_ultima_actividad,
            'usuario': aprendiz.nombre,
            'descripcion': 'Actualización de perfil de aprendiz',
            'tipo': 'APRENDIZ'
        })
    
    # Últimas postulaciones
    ultimas_postulaciones = Postulacion.objects.order_by('-fecha_postulacion')[:5]
    for postulacion in ultimas_postulaciones:
        actividades_recientes.append({
            'fecha': postulacion.fecha_postulacion,
            'usuario': f"{postulacion.aprendiz.nombre} - {postulacion.empresa.nombre}",
            'descripcion': 'Postulación a empresa',
            'tipo': 'POSTULACION'
        })
    
    # Ordenar actividades por fecha
    actividades_recientes.sort(key=lambda x: x['fecha'], reverse=True)
    actividades_recientes = actividades_recientes[:10]

    context = {
        'total_aprendices': total_aprendices,
        'total_empresas': total_empresas,
        'total_postulaciones': total_postulaciones,
        'aprendices_contratados': aprendices_contratados,
        'aprendices_disponibles': aprendices_disponibles,
        'aprendices_proceso': aprendices_proceso,
        'empresas_activas': empresas_activas,
        'postulaciones_pendientes': postulaciones_pendientes,
        'aprendices_por_estado': aprendices_por_estado,
        'empresas_por_estado': empresas_por_estado,
        'postulaciones_por_estado': postulaciones_por_estado,
        'estados_aprendices': estados_aprendices,
        'estados_postulaciones': estados_postulaciones,
        'postulaciones_ultimo_mes': postulaciones_ultimo_mes,
        'postulaciones_mes': dict(postulaciones_mes),
        'top_empresas': top_empresas,
        'top_aprendices': top_aprendices,
        'todos_aprendices': todos_aprendices,
        'todas_postulaciones': todas_postulaciones,
        'actividades_recientes': actividades_recientes,
        'tasa_contratacion': tasa_contratacion,
        'tasa_seleccion': tasa_seleccion,
        'tasa_postulacion': tasa_postulacion,
        'tasa_retencion': tasa_retencion,
        'ultima_actualizacion': timezone.now(),
    }
    
    return render(request, 'plataforma/dashboard_simple.html', context)


@login_required(login_url="login")
def importar_datos(request):
    """Vista principal para importación de datos"""
    return render(request, 'plataforma/importar_datos.html')


@login_required(login_url="login")
def procesar_importacion(request):
    """Procesa la importación de archivos"""
    from .importacion_datos import ImportadorDatos
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    tipo_importacion = request.POST.get('tipo_importacion')
    archivo = request.FILES.get('archivo')
    
    if not archivo:
        return JsonResponse({'error': 'No se ha subido ningún archivo'}, status=400)
    
    if not archivo.name.endswith(('.xlsx', '.xls', '.csv')):
        return JsonResponse({'error': 'Formato de archivo no válido. Use Excel (.xlsx, .xls) o CSV (.csv)'}, status=400)
    
    importador = ImportadorDatos()
    
    try:
        if tipo_importacion == 'aprendices':
            resultado = importador.importar_aprendices(archivo)
        elif tipo_importacion == 'empresas':
            resultado = importador.importar_empresas(archivo)
        elif tipo_importacion == 'postulaciones':
            resultado = importador.importar_postulaciones(archivo)
        else:
            return JsonResponse({'error': 'Tipo de importación no válido'}, status=400)
        
        resumen = importador.get_resumen()
        
        return JsonResponse({
            'exito': resultado,
            'resumen': resumen
        })
        
    except Exception as e:
        import traceback
        print("=== ERROR EN IMPORTACIÓN ===")
        print(traceback.format_exc())
        print("==========================")
        return JsonResponse({'error': f'Error en la importación: {str(e)}'}, status=500)


# Vista de acceso denegado eliminada - ya no se necesita
