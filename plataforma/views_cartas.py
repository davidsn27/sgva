from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Count
from .models import CartaFechas, Aprendiz
from .decorators import funcionario_sena_required, trabajador_required as trabajador_empresa_required, estudiante_required

# ========================
# CARTAS DE FECHAS
# ========================


@trabajador_empresa_required
def lista_cartas_contrato(request):
    """Lista las cartas de fechas de la empresa"""
    try:
        empresa = request.user.empresa
    except Exception:
        messages.error(request, "No tienes una empresa asociada")
        return redirect("inicio")
    
    # Obtener cartas de la empresa
    cartas = CartaFechas.objects.filter(empresa=empresa).order_by('-fecha_solicitud')
    
    # Filtros
    estado_filtro = request.GET.get("estado", "").strip()
    if estado_filtro:
        cartas = cartas.filter(estado=estado_filtro)
    
    # Paginación
    paginator = Paginator(cartas, 10)
    pagina = request.GET.get("pagina")
    cartas = paginator.get_page(pagina)
    
    context = {
        'cartas': cartas,
        'empresa': empresa,
        'estados_cartas': CartaFechas.ESTADOS,
    }
    
    return render(request, 'plataforma/cartas_contrato/lista_cartas.html', context)


@trabajador_empresa_required
def crear_carta_contrato(request, aprendiz_id):
    """Crea una nueva carta de contrato para un aprendiz"""
    try:
        empresa = request.user.empresa
    except Exception:
        messages.error(request, "No tienes una empresa asociada")
        return redirect("inicio")
    
    aprendiz = get_object_or_404(Aprendiz, id=aprendiz_id)
    
    # Verificar si ya existe una carta pendiente
    carta_existente = CartaFechas.objects.filter(
        empresa=empresa, 
        aprendiz=aprendiz, 
        estado='PENDIENTE'
    ).first()
    
    if carta_existente:
        messages.warning(request, f"Ya tienes una carta pendiente para {aprendiz.nombre}")
        return redirect("detalle_carta_contrato", carta_existente.id)
    
    if request.method == "POST":
        # Procesar formulario
        carta = CartaFechas(
            empresa=empresa,
            aprendiz=aprendiz,
            fecha_inicio_propuesta=request.POST.get("fecha_inicio"),
            fecha_fin_propuesta=request.POST.get("fecha_fin"),
            salario_propuesto=request.POST.get("salario_propuesto"),
            tipo_contrato=request.POST.get("tipo_contrato"),
            cargo_ofrecido=request.POST.get("cargo_ofrecido"),
            descripcion_actividades=request.POST.get("descripcion_actividades"),
            lugar_trabajo=request.POST.get("lugar_trabajo"),
            horario_trabajo=request.POST.get("horario_trabajo"),
            beneficios=request.POST.get("beneficios", ""),
            seguro_medico=request.POST.get("seguro_medico") == "on",
            transporte=request.POST.get("transporte") == "on",
            alimentacion=request.POST.get("alimentacion") == "on",
        )
        
        # Guardar archivos si se subieron
        if 'carta_propuesta' in request.FILES:
            carta.carta_propuesta = request.FILES['carta_propuesta']
        if 'documento_empresa' in request.FILES:
            carta.documento_empresa = request.FILES['documento_empresa']
        
        carta.save()
        
        messages.success(request, f"Carta de contrato enviada para {aprendiz.nombre}")
        return redirect("lista_cartas_contrato")
    
    context = {
        'aprendiz': aprendiz,
        'empresa': empresa,
        'tipos_contrato': CartaFechas._meta.get_field('tipo_contrato').choices,
    }
    
    return render(request, 'plataforma/cartas_contrato/crear_carta.html', context)


@trabajador_empresa_required
def detalle_carta_contrato(request, carta_id):
    """Muestra los detalles de una carta de contrato"""
    try:
        empresa = request.user.empresa
    except Exception:
        messages.error(request, "No tienes una empresa asociada")
        return redirect("inicio")
    
    carta = get_object_or_404(CartaFechas, id=carta_id, empresa=empresa)
    
    context = {
        'carta': carta,
        'empresa': empresa,
    }
    
    return render(request, 'plataforma/cartas_contrato/detalle_carta.html', context)


@trabajador_empresa_required
def editar_carta_contrato(request, carta_id):
    """Edita una carta de contrato (solo si está pendiente)"""
    try:
        empresa = request.user.empresa
    except Exception:
        messages.error(request, "No tienes una empresa asociada")
        return redirect("inicio")
    
    carta = get_object_or_404(CartaFechas, id=carta_id, empresa=empresa)
    
    if not carta.puede_ser_editada():
        messages.error(request, "Esta carta no puede ser editada")
        return redirect("detalle_carta_contrato", carta.id)
    
    if request.method == "POST":
        # Actualizar carta
        carta.fecha_inicio_propuesta = request.POST.get("fecha_inicio")
        carta.fecha_fin_propuesta = request.POST.get("fecha_fin")
        carta.salario_propuesto = request.POST.get("salario_propuesto")
        carta.tipo_contrato = request.POST.get("tipo_contrato")
        carta.cargo_ofrecido = request.POST.get("cargo_ofrecido")
        carta.descripcion_actividades = request.POST.get("descripcion_actividades")
        carta.lugar_trabajo = request.POST.get("lugar_trabajo")
        carta.horario_trabajo = request.POST.get("horario_trabajo")
        carta.beneficios = request.POST.get("beneficios", "")
        carta.seguro_medico = request.POST.get("seguro_medico") == "on"
        carta.transporte = request.POST.get("transporte") == "on"
        carta.alimentacion = request.POST.get("alimentacion") == "on"
        
        # Guardar archivos si se subieron
        if 'carta_propuesta' in request.FILES:
            carta.carta_propuesta = request.FILES['carta_propuesta']
        if 'documento_empresa' in request.FILES:
            carta.documento_empresa = request.FILES['documento_empresa']
        
        carta.save()
        
        messages.success(request, "Carta de contrato actualizada")
        return redirect("detalle_carta_contrato", carta.id)
    
    context = {
        'carta': carta,
        'empresa': empresa,
        'tipos_contrato': CartaFechas._meta.get_field('tipo_contrato').choices,
    }
    
    return render(request, 'plataforma/cartas_contrato/editar_carta.html', context)


@funcionario_sena_required
def lista_cartas_pendientes(request):
    """Lista las cartas de contrato pendientes de aprobación"""
    cartas = CartaFechas.objects.filter(estado='PENDIENTE').order_by('-fecha_solicitud')
    
    # Filtros
    empresa_filtro = request.GET.get("empresa", "").strip()
    if empresa_filtro:
        cartas = cartas.filter(empresa__nombre__icontains=empresa_filtro)
    
    # Paginación
    paginator = Paginator(cartas, 10)
    pagina = request.GET.get("pagina")
    cartas = paginator.get_page(pagina)
    
    context = {
        'cartas': cartas,
        'estados_cartas': CartaFechas.ESTADOS,
    }
    
    return render(request, 'plataforma/cartas_contrato/cartas_pendientes.html', context)


@funcionario_sena_required
def aprobar_carta_contrato(request, carta_id):
    """Aprueba o rechaza una carta de contrato"""
    carta = get_object_or_404(CartaFechas, id=carta_id)
    
    if carta.estado != 'PENDIENTE':
        messages.error(request, "Esta carta ya fue procesada")
        return redirect("lista_cartas_pendientes")
    
    if request.method == "POST":
        accion = request.POST.get("accion")
        comentarios = request.POST.get("comentarios", "")
        
        if accion == "aprobar":
            carta.estado = 'APROBADA'
            carta.funcionario_aprobacion = request.user
            carta.fecha_aprobacion = timezone.now()
            carta.comentarios_aprobacion = comentarios
            carta.save()
            
            # Actualizar estado del aprendiz
            carta.aprendiz.estado = 'PROCESO_SELECCION_ABIERTO'
            carta.aprendiz.empresa_actual = carta.empresa
            carta.aprendiz.fecha_ultima_actividad = timezone.now()
            carta.aprendiz.save()
            
            messages.success(request, f"Carta aprobada para {carta.aprendiz.nombre}")
            
        elif accion == "rechazar":
            carta.estado = 'RECHAZADA'
            carta.funcionario_aprobacion = request.user
            carta.fecha_aprobacion = timezone.now()
            carta.comentarios_aprobacion = comentarios
            carta.save()
            
            messages.warning(request, f"Carta rechazada para {carta.aprendiz.nombre}")
        
        return redirect("lista_cartas_pendientes")
    
    context = {
        'carta': carta,
    }
    
    return render(request, 'plataforma/cartas_contrato/aprobar_carta.html', context)


@estudiante_required
def mis_cartas_contrato(request):
    """Muestra las cartas de contrato del aprendiz"""
    try:
        aprendiz = request.user.perfil.aprendiz
    except Exception:
        messages.error(request, "No tienes un perfil de aprendiz asociado")
        return redirect("inicio")
    
    cartas = CartaFechas.objects.filter(aprendiz=aprendiz).order_by('-fecha_solicitud')
    
    context = {
        'cartas': cartas,
        'aprendiz': aprendiz,
    }
    
    return render(request, 'plataforma/cartas_contrato/mis_cartas.html', context)


@estudiante_required
def responder_carta_contrato(request, carta_id):
    """El aprendiz responde a una carta de contrato"""
    try:
        aprendiz = request.user.perfil.aprendiz
    except Exception:
        messages.error(request, "No tienes un perfil de aprendiz asociado")
        return redirect("inicio")
    
    carta = get_object_or_404(CartaFechas, id=carta_id, aprendiz=aprendiz)
    
    if carta.estado != 'APROBADA':
        messages.error(request, "Esta carta no está aprobada")
        return redirect("mis_cartas_contrato")
    
    if carta.aprendiz_acepta is not None:
        messages.warning(request, "Ya has respondido a esta carta")
        return redirect("mis_cartas_contrato")
    
    if request.method == "POST":
        accion = request.POST.get("accion")
        comentarios = request.POST.get("comentarios", "")
        
        if accion == "aceptar":
            carta.aprendiz_acepta = True
            carta.fecha_aceptacion_aprendiz = timezone.now()
            carta.comentarios_aprendiz = comentarios
            carta.save()
            
            # Actualizar estado del aprendiz
            carta.aprendiz.estado = 'CONTRATO_NO_REGISTRADO'
            carta.aprendiz.fecha_ultima_actividad = timezone.now()
            carta.aprendiz.save()
            
            messages.success(request, "Has aceptado la propuesta de contrato")
            
        elif accion == "rechazar":
            carta.aprendiz_acepta = False
            carta.fecha_aceptacion_aprendiz = timezone.now()
            carta.comentarios_aprendiz = comentarios
            carta.save()
            
            # Actualizar estado del aprendiz
            carta.aprendiz.estado = 'DISPONIBLE'
            carta.aprendiz.empresa_actual = None
            carta.aprendiz.fecha_ultima_actividad = timezone.now()
            carta.aprendiz.save()
            
            messages.info(request, "Has rechazado la propuesta de contrato")
        
        return redirect("mis_cartas_contrato")
    
    context = {
        'carta': carta,
        'aprendiz': aprendiz,
    }
    
    return render(request, 'plataforma/cartas_contrato/responder_carta.html', context)


@funcionario_sena_required
def dashboard_cartas(request):
    """Dashboard de estadísticas de cartas de contrato"""
    from django.db.models import Count
    
    # Estadísticas generales
    total_cartas = CartaFechas.objects.count()
    cartas_pendientes = CartaFechas.objects.filter(estado='PENDIENTE').count()
    cartas_aprobadas = CartaFechas.objects.filter(estado='APROBADA').count()
    cartas_rechazadas = CartaFechas.objects.filter(estado='RECHAZADA').count()
    cartas_completadas = CartaFechas.objects.filter(estado='COMPLETADA').count()
    
    # Cartas por estado
    cartas_por_estado = CartaFechas.objects.values('estado').annotate(
        count=Count('id')
    ).order_by('estado')
    
    # Cartas recientes
    cartas_recientes = CartaFechas.objects.all().order_by('-fecha_solicitud')[:10]
    
    context = {
        'total_cartas': total_cartas,
        'cartas_pendientes': cartas_pendientes,
        'cartas_aprobadas': cartas_aprobadas,
        'cartas_rechazadas': cartas_rechazadas,
        'cartas_completadas': cartas_completadas,
        'cartas_por_estado': cartas_por_estado,
        'cartas_recientes': cartas_recientes,
        'fecha_actualizacion': timezone.now(),
    }
    
    return render(request, 'plataforma/cartas_contrato/dashboard_cartas.html', context)
