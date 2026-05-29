from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils import timezone
from django.db import models
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .models import (
    Perfil,
    Publicacion,
    Like,
    Comentario,
    Oferta,
    Servicio,
    PortafolioFoto,
    Calificacion,
    Reporte,
    HistorialAdmin,
)


# ========== VISTAS PÚBLICAS ==========
def index(request):
    return render(request, "index.html")


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        remember_me = request.POST.get("remember_me")

        user_obj = User.objects.filter(email=email).first()

        if user_obj is None:
            return render(request, "login.html", {"error": "Correo no registrado"})

        user = authenticate(request, username=user_obj.username, password=password)

        if user is not None:
            login(request, user)

            if remember_me:
                request.session.set_expiry(2592000)
            else:
                request.session.set_expiry(0)

            if user.is_superuser or user.is_staff:
                return redirect("dashboard_admin")
            else:
                return redirect("dashboard")
        else:
            return render(request, "login.html", {"error": "Credenciales incorrectas"})

    return render(request, "login.html")


@login_required
def dashboard_admin(request):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("dashboard")

    total_usuarios = User.objects.count()
    total_trabajadores = Perfil.objects.filter(tipo="trabajador").count()
    total_empleadores = Perfil.objects.filter(tipo="empleador").count()
    total_publicaciones = Publicacion.objects.count()
    total_ofertas = Oferta.objects.count()
    total_servicios = Servicio.objects.count()
    total_comentarios = Comentario.objects.count()

    ultimos_usuarios = User.objects.order_by("-date_joined")[:10]
    ultimas_publicaciones = Publicacion.objects.all().order_by("-fecha_creacion")[:10]

    from django.db.models.functions import TruncMonth
    from django.db.models import Count
    from datetime import datetime, timedelta

    usuarios_por_mes = (
        User.objects.annotate(mes=TruncMonth("date_joined"))
        .values("mes")
        .annotate(total=Count("id"))
        .order_by("-mes")[:6]
    )

    context = {
        "total_usuarios": total_usuarios,
        "total_trabajadores": total_trabajadores,
        "total_empleadores": total_empleadores,
        "total_publicaciones": total_publicaciones,
        "total_ofertas": total_ofertas,
        "total_servicios": total_servicios,
        "total_comentarios": total_comentarios,
        "usuarios_bloqueados": User.objects.filter(is_active=False).count(),
        "reportes_pendientes": Reporte.objects.filter(estado="pendiente").count(),
        "publicaciones_eliminadas": HistorialAdmin.objects.filter(
            accion__icontains="Publicación eliminada"
        ).count(),
        "ultimos_reportes": Reporte.objects.select_related(
            "reportante", "usuario_reportado"
        ).order_by("-fecha")[:5],
        "ultimas_acciones": HistorialAdmin.objects.select_related(
            "administrador"
        ).order_by("-fecha")[:5],
        "ultimos_usuarios": ultimos_usuarios,
        "ultimas_publicaciones": ultimas_publicaciones,
        "usuarios_por_mes": usuarios_por_mes,
    }
    return render(request, "dashboard_admin.html", context)


def recuperar_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = request.build_absolute_uri(f"/reset-password/{uid}/{token}/")
            send_mail(
                "Recupera tu contraseña - CHAMBA",
                f"""
Estimado usuario,

Hemos recibido una solicitud para restablecer la contraseña de su cuenta en CHAMBA.

Para crear una nueva contraseña, acceda al siguiente enlace:

{reset_url}

Este enlace expirará en 24 horas por razones de seguridad.

Si usted no solicitó este cambio, ignore este mensaje.

Atentamente,
El equipo de CHAMBA
""",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(request, "Te hemos enviado un correo con instrucciones")
            return redirect("login")
        except User.DoesNotExist:
            messages.error(request, "No existe un usuario con ese correo")
    return render(request, "recuperar_password.html")


def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == "POST":
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Contraseña actualizada correctamente")
                return redirect("login")
            else:
                messages.error(request, "Las contraseñas no coinciden")
        return render(request, "reset_password.html", {"validlink": True})
    else:
        return render(request, "reset_password.html", {"validlink": False})


def register_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        nombre = request.POST.get("nombre")
        rol = request.POST.get("rol")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Este correo ya está registrado")
            return render(request, "register.html", {"error": "Email ya registrado"})

        username = email.split("@")[0]
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username, email=email, password=password, first_name=nombre
        )

        perfil_data = {
            "usuario": user,
            "tipo": rol,
            "telefono": request.POST.get("telefono", ""),
            "ubicacion": request.POST.get("ubicacion", ""),
            "descripcion_personal": request.POST.get("descripcion_personal", ""),
        }

        if rol == "trabajador":
            perfil_data["oficios"] = request.POST.get("oficio", "")
            perfil_data["anios_experiencia"] = request.POST.get("anios_experiencia", 0)
        else:
            perfil_data["nombre_empresa"] = request.POST.get("nombre_empresa", "")
            perfil_data["rubro"] = request.POST.get("rubro", "")

        Perfil.objects.create(**perfil_data)

        messages.success(request, "¡Registro exitoso! Ahora puedes iniciar sesión")
        return redirect("login")

    return render(request, "register.html")


def logout_view(request):
    logout(request)
    return redirect("index")


@login_required
def dashboard(request):
    publicaciones = Publicacion.objects.all().order_by("-fecha_creacion")
    ofertas = Oferta.objects.filter(activa=True).order_by("-fecha_publicacion")
    servicios = Servicio.objects.filter(disponible=True).order_by("-fecha_publicacion")
    trabajadores = Perfil.objects.filter(tipo="trabajador").select_related("usuario")[
        :10
    ]

    return render(
        request,
        "dashboard.html",
        {
            "publicaciones": publicaciones,
            "ofertas": ofertas,
            "servicios": servicios,
            "trabajadores": trabajadores,
        },
    )


@login_required
def publicar_estado(request):
    if request.method == "POST":
        contenido = request.POST.get("contenido")
        imagen = request.FILES.get("imagen")
        if contenido:
            publicacion = Publicacion.objects.create(
                usuario=request.user, contenido=contenido, tipo="estado"
            )
            if imagen:
                publicacion.imagen = imagen
                publicacion.save()
            return redirect("dashboard")
    return render(request, "publicar.html")


@login_required
def like_toggle(request, publicacion_id):
    publicacion = get_object_or_404(Publicacion, id=publicacion_id)
    like, creado = Like.objects.get_or_create(
        usuario=request.user, publicacion=publicacion
    )
    if not creado:
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({"liked": liked, "total_likes": publicacion.likes.count()})


@login_required
def comentar(request, publicacion_id):
    if request.method == "POST":
        publicacion = get_object_or_404(Publicacion, id=publicacion_id)
        texto = request.POST.get("texto", "").strip()
        if texto:
            comentario = Comentario.objects.create(
                usuario=request.user, publicacion=publicacion, texto=texto
            )
            return JsonResponse(
                {
                    "success": True,
                    "usuario": request.user.get_full_name() or request.user.username,
                    "texto": comentario.texto,
                    "fecha": comentario.fecha.strftime("%d/%m/%Y %H:%M"),
                }
            )
    return JsonResponse({"success": False}, status=400)


@login_required
def listar_comentarios(request, publicacion_id):
    publicacion = get_object_or_404(Publicacion, id=publicacion_id)
    comentarios = publicacion.comentarios.all().order_by("fecha")
    data = {
        "comentarios": [
            {
                "usuario": c.usuario.get_full_name() or c.usuario.username,
                "usuario_id": c.usuario.id,
                "texto": c.texto,
                "fecha": c.fecha.strftime("%d/%m/%Y %H:%M"),
            }
            for c in comentarios
        ]
    }
    return JsonResponse(data)


@login_required
def publicar_oferta(request):
    if request.method == "POST":
        oferta = Oferta.objects.create(
            empleador=request.user,
            titulo=request.POST.get("titulo"),
            oficio=request.POST.get("oficio"),
            descripcion=request.POST.get("descripcion"),
            ubicacion=request.POST.get("ubicacion"),
            remuneracion=request.POST.get("remuneracion", ""),
            fecha_limite=request.POST.get("fecha_limite") or None,
            latitud=request.POST.get("latitud") or None,
            longitud=request.POST.get("longitud") or None,
        )
        Publicacion.objects.create(
            usuario=request.user,
            contenido=f"📢 NUEVA OFERTA: {request.POST.get('titulo')}\n\n{request.POST.get('descripcion')[:200]}",
            tipo="oferta",
        )
        return redirect("dashboard")
    return render(request, "publicar_oferta.html")


@login_required
def empleos(request):
    from datetime import date

    hoy = date.today()
    ofertas = Oferta.objects.filter(activa=True).order_by("-fecha_publicacion")
    for oferta in ofertas:
        if oferta.fecha_limite:
            if oferta.fecha_limite < hoy:
                oferta.estado = "Caducada"
                oferta.estado_color = "#EF4444"
            elif (oferta.fecha_limite - hoy).days <= 3:
                oferta.estado = "¡Por vencer!"
                oferta.estado_color = "#F59E0B"
            else:
                oferta.estado = "Abierta"
                oferta.estado_color = "#10B981"
        else:
            oferta.estado = "Abierta"
            oferta.estado_color = "#10B981"
    return render(request, "empleos.html", {"ofertas": ofertas})


@login_required
def ofrecer_servicio(request):
    if request.method == "POST":
        servicio = Servicio.objects.create(
            trabajador=request.user,
            titulo=request.POST.get("titulo"),
            oficio=request.POST.get("oficio"),
            descripcion=request.POST.get("descripcion"),
            ubicacion=request.POST.get("ubicacion"),
            precio=request.POST.get("precio", ""),
            latitud=request.POST.get("latitud") or None,
            longitud=request.POST.get("longitud") or None,
        )
        Publicacion.objects.create(
            usuario=request.user,
            contenido=f"🔧 NUEVO SERVICIO: {request.POST.get('titulo')}\n\n{request.POST.get('descripcion')[:200]}",
            tipo="servicio",
        )
        return redirect("dashboard")
    return render(request, "ofrecer_servicio.html")


def formatear_tiempo(fecha):
    ahora = timezone.now()
    diff = ahora - fecha
    if diff.days > 0:
        return f"{diff.days} día{'s' if diff.days > 1 else ''} atrás"
    elif diff.seconds // 3600 > 0:
        horas = diff.seconds // 3600
        return f"{horas} hora{'s' if horas > 1 else ''} atrás"
    elif diff.seconds // 60 > 0:
        minutos = diff.seconds // 60
        return f"{minutos} minuto{'s' if minutos > 1 else ''} atrás"
    else:
        return "hace un momento"


@login_required
def trabajadores(request):
    servicios = Servicio.objects.filter(disponible=True).order_by("-fecha_publicacion")
    return render(request, "trabajadores.html", {"servicios": servicios})

# Botón reportar
@login_required
def reportar_oferta(request, oferta_id):
    oferta = get_object_or_404(Oferta, id=oferta_id)

    if request.method == "POST":
        motivo = request.POST.get("motivo", "Otro motivo")
        detalle = request.POST.get("detalle", "").strip()

        if oferta.empleador != request.user:
            Reporte.objects.create(
                reportante=request.user,
                usuario_reportado=oferta.empleador,
                tipo="publicacion",
                motivo=f"Oferta reportada: {oferta.titulo}. Motivo: {motivo}" + (f". Detalle: {detalle}" if detalle else ""),
                estado="pendiente"
            )

    return redirect("empleos")

@login_required
def reportar_servicio(request, servicio_id):
    servicio = get_object_or_404(Servicio, id=servicio_id)

    if request.method == "POST":
        motivo = request.POST.get("motivo", "Otro motivo")
        detalle = request.POST.get("detalle", "").strip()

        if servicio.trabajador != request.user:
            Reporte.objects.create(
                reportante=request.user,
                usuario_reportado=servicio.trabajador,
                tipo="publicacion",
                motivo=f"Servicio reportado: {servicio.titulo}. Motivo: {motivo}" + (f". Detalle: {detalle}" if detalle else ""),
                estado="pendiente"
            )

    return redirect("trabajadores")

@login_required
def api_oferta_detalle(request, oferta_id):
    oferta = get_object_or_404(Oferta, id=oferta_id)
    from datetime import date

    hoy = date.today()
    estado = "Abierta"
    estado_color = "#10B981"
    estado_icono = "fa-check-circle"
    if oferta.fecha_limite:
        if oferta.fecha_limite < hoy:
            estado = "Caducada"
            estado_color = "#EF4444"
            estado_icono = "fa-calendar-xmark"
        elif (oferta.fecha_limite - hoy).days <= 3:
            estado = "¡Por vencer!"
            estado_color = "#F59E0B"
            estado_icono = "fa-clock"
    data = {
        "id": oferta.id,
        "titulo": oferta.titulo,
        "oficio": oferta.oficio,
        "descripcion": oferta.descripcion,
        "ubicacion": oferta.ubicacion,
        "remuneracion": oferta.remuneracion,
        "fecha_limite": (
            oferta.fecha_limite.strftime("%d/%m/%Y") if oferta.fecha_limite else None
        ),
        "fecha": formatear_tiempo(oferta.fecha_publicacion),
        "empresa": oferta.empleador.perfil.nombre_empresa
        or oferta.empleador.get_full_name(),
        "telefono": oferta.empleador.perfil.telefono,
        "foto": (
            oferta.empleador.perfil.foto_perfil.url
            if oferta.empleador.perfil.foto_perfil
            else f"https://ui-avatars.com/api/?background=0A66C2&color=fff&name={oferta.empleador.username}"
        ),
        "tipo": "oferta",
        "es_propia": oferta.empleador == request.user,
        "estado": estado,
        "estado_color": estado_color,
        "estado_icono": estado_icono,
    }
    return JsonResponse(data)


@login_required
def api_servicio_detalle(request, servicio_id):
    servicio = get_object_or_404(Servicio, id=servicio_id)
    from .models import PortafolioFoto

    portafolio = PortafolioFoto.objects.filter(trabajador=servicio.trabajador).order_by(
        "orden"
    )
    data = {
        "id": servicio.id,
        "titulo": servicio.titulo,
        "oficio": servicio.oficio,
        "descripcion": servicio.descripcion,
        "ubicacion": servicio.ubicacion,
        "precio": servicio.precio,
        "fecha": formatear_tiempo(servicio.fecha_publicacion),
        "trabajador": servicio.trabajador.get_full_name()
        or servicio.trabajador.username,
        "telefono": servicio.trabajador.perfil.telefono,
        "foto": (
            servicio.trabajador.perfil.foto_perfil.url
            if servicio.trabajador.perfil.foto_perfil
            else f"https://ui-avatars.com/api/?background=0A66C2&color=fff&name={servicio.trabajador.username}"
        ),
        "portafolio_fotos": [
            {"url": p.imagen.url, "titulo": p.titulo} for p in portafolio
        ],
        "tipo": "servicio",
    }
    return JsonResponse(data)


@login_required
def cambiar_foto(request):
    if request.method == "POST" and request.FILES.get("foto"):
        perfil = request.user.perfil
        perfil.foto_perfil = request.FILES["foto"]
        perfil.save()
    return redirect("perfil")


@login_required
def editar_campo(request):
    if request.method == "POST":
        campo = request.POST.get("campo")
        valor = request.POST.get("valor")
        if not campo or not campo.strip():
            return JsonResponse({"success": False, "error": "Campo no especificado"})
        perfil = request.user.perfil
        campos_permitidos = [
            "telefono",
            "ubicacion",
            "oficios",
            "descripcion_personal",
            "nombre_empresa",
            "rubro",
            "anios_experiencia",
            "disponible",
        ]
        if campo in campos_permitidos:
            if campo == "anios_experiencia":
                try:
                    valor = int(valor) if valor else 0
                except ValueError:
                    valor = 0
            setattr(perfil, campo, valor)
            perfil.save()
            return JsonResponse({"success": True})
        else:
            return JsonResponse(
                {"success": False, "error": f"Campo '{campo}' no permitido"}
            )
    return JsonResponse({"success": False, "error": "Método no permitido"})


@login_required
def toggle_disponibilidad(request):
    if request.method == "POST":
        perfil = request.user.perfil
        perfil.disponible = not perfil.disponible
        perfil.save()
        return JsonResponse({"success": True, "disponible": perfil.disponible})
    return JsonResponse({"success": False})


@login_required
def editar_perfil(request):
    """Vista para editar el perfil completo"""
    perfil = request.user.perfil
    
    if request.method == "POST":
        # Actualizar usuario
        user = request.user
        user.first_name = request.POST.get("nombre", "")
        user.save()
        
        # Actualizar perfil - campos comunes
        perfil.telefono = request.POST.get("telefono", "")
        perfil.ubicacion = request.POST.get("ubicacion", "")
        perfil.anios_experiencia = request.POST.get("anios_experiencia", 0)
        
        # Disponibilidad
        disponible = request.POST.get("disponible")
        if disponible == 'True':
            perfil.disponible = True
        elif disponible == 'False':
            perfil.disponible = False
        
        # Actualizar contactos externos (redes sociales)
        contactos = {}
        if request.POST.get("whatsapp"):
            contactos['whatsapp'] = request.POST.get("whatsapp")
        if request.POST.get("facebook"):
            contactos['facebook'] = request.POST.get("facebook")
        if request.POST.get("instagram"):
            contactos['instagram'] = request.POST.get("instagram")
        if request.POST.get("linkedin"):
            contactos['linkedin'] = request.POST.get("linkedin")
        if contactos:
            perfil.contactos_externos = contactos
        
        # Datos según el rol
        if perfil.tipo == "trabajador":
            perfil.oficios = request.POST.get("oficios", "")
            perfil.descripcion_personal = request.POST.get("descripcion_personal", "")
        else:
            perfil.nombre_empresa = request.POST.get("nombre_empresa", "")
            perfil.rubro = request.POST.get("rubro", "")
            perfil.descripcion_personal = request.POST.get("descripcion_personal", "")
        
        perfil.save()
        messages.success(request, "¡Perfil actualizado correctamente!")
        return redirect("perfil")
    
    # Si es GET, mostrar formulario con datos actuales
    context = {
        'user': request.user,
        'perfil': perfil,
    }
    return render(request, "editar_perfil.html", context)


@login_required
def perfil_user(request):
    from .models import PortafolioFoto, Calificacion, Oferta, Servicio, Publicacion, Like, Comentario

    calificaciones_recibidas = (
        Calificacion.objects.filter(calificado=request.user)
        .select_related("calificador")
        .order_by("-fecha")
    )
    
    # Obtener ofertas y servicios del usuario
    ofertas_usuario = Oferta.objects.filter(empleador=request.user).order_by("-fecha_publicacion")
    servicios_usuario = Servicio.objects.filter(trabajador=request.user).order_by("-fecha_publicacion")
    
    # Obtener publicaciones de estado del usuario
    publicaciones_estado = Publicacion.objects.filter(usuario=request.user, tipo='estado').order_by("-fecha_creacion")
    
    # Crear una lista combinada con objetos reales de Publicacion
    mis_publicaciones = list(publicaciones_estado)  # Las de estado ya son objetos Publicacion
    
    # Para ofertas y servicios, necesitamos obtener o crear sus Publicaciones asociadas
    for oferta in ofertas_usuario:
        # Buscar la publicación asociada a esta oferta
        pub = Publicacion.objects.filter(usuario=request.user, tipo='oferta', contenido__icontains=oferta.titulo).first()
        if pub:
            mis_publicaciones.append(pub)
        else:
            # Si no existe, crear una publicación temporal (opcional)
            # Pero lo mejor es asegurarse de que se crea al publicar la oferta
            pass
    
    for servicio in servicios_usuario:
        # Buscar la publicación asociada a este servicio
        pub = Publicacion.objects.filter(usuario=request.user, tipo='servicio', contenido__icontains=servicio.titulo).first()
        if pub:
            mis_publicaciones.append(pub)
    
    # Ordenar por fecha (más reciente primero)
    mis_publicaciones.sort(key=lambda x: x.fecha_creacion, reverse=True)
    
    context = {
        "portafolio_fotos": (
            PortafolioFoto.objects.filter(trabajador=request.user).order_by("orden")
            if request.user.perfil.tipo == "trabajador"
            else []
        ),
        "mis_publicaciones": mis_publicaciones,  # ✅ Ahora son objetos Publicacion REALES
        "ofertas": ofertas_usuario,
        "servicios": servicios_usuario,
        "calificaciones_recibidas": calificaciones_recibidas,
        "promedio_calificacion": request.user.perfil.promedio_calificacion,
        "total_calificaciones": request.user.perfil.total_calificaciones,
        "anios_experiencia": request.user.perfil.anios_experiencia or 0,
    }
    return render(request, "perfil.html", context)

@login_required
def subir_portafolio(request):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    if request.method == "POST" and request.FILES.get("imagen"):
        titulo = request.POST.get("titulo", "")
        descripcion = request.POST.get("descripcion", "")
        imagen = request.FILES["imagen"]
        if imagen.size > 5 * 1024 * 1024:
            if is_ajax:
                return JsonResponse(
                    {"success": False, "error": "La imagen no debe superar los 5MB"}
                )
            return redirect("perfil")
        foto = PortafolioFoto.objects.create(
            trabajador=request.user,
            titulo=titulo,
            descripcion=descripcion,
            imagen=imagen,
        )
        if is_ajax:
            return JsonResponse(
                {"success": True, "foto_id": foto.id, "url": foto.imagen.url}
            )
        return redirect("perfil")
    if is_ajax:
        return JsonResponse({"success": False, "error": "No se recibió ninguna imagen"})
    return redirect("perfil")


@login_required
def eliminar_portafolio(request, foto_id):
    foto = get_object_or_404(PortafolioFoto, id=foto_id, trabajador=request.user)
    foto.delete()
    return redirect("perfil")


@login_required
def api_buscar_ajax(request):
    query = request.GET.get("q", "").strip()
    resultados = {"ofertas": [], "servicios": [], "trabajadores": []}
    if query and len(query) >= 2:
        ofertas = Oferta.objects.filter(activa=True).filter(
            models.Q(titulo__icontains=query)
            | models.Q(descripcion__icontains=query)
            | models.Q(oficio__icontains=query)
            | models.Q(ubicacion__icontains=query)
        )[:5]
        for o in ofertas:
            resultados["ofertas"].append(
                {
                    "id": o.id,
                    "titulo": o.titulo,
                    "empresa": o.empleador.perfil.nombre_empresa
                    or o.empleador.get_full_name(),
                    "ubicacion": o.ubicacion,
                    "foto": (
                        o.empleador.perfil.foto_perfil.url
                        if o.empleador.perfil.foto_perfil
                        else None
                    ),
                }
            )
        servicios = Servicio.objects.filter(disponible=True).filter(
            models.Q(titulo__icontains=query)
            | models.Q(descripcion__icontains=query)
            | models.Q(oficio__icontains=query)
            | models.Q(ubicacion__icontains=query)
        )[:5]
        for s in servicios:
            resultados["servicios"].append(
                {
                    "id": s.id,
                    "titulo": s.titulo,
                    "trabajador": s.trabajador.get_full_name() or s.trabajador.username,
                    "ubicacion": s.ubicacion,
                    "foto": (
                        s.trabajador.perfil.foto_perfil.url
                        if s.trabajador.perfil.foto_perfil
                        else None
                    ),
                }
            )
        trabajadores = (
            Perfil.objects.filter(tipo="trabajador")
            .filter(
                models.Q(usuario__first_name__icontains=query)
                | models.Q(usuario__username__icontains=query)
                | models.Q(oficios__icontains=query)
                | models.Q(ubicacion__icontains=query)
            )
            .select_related("usuario")[:5]
        )
        for p in trabajadores:
            resultados["trabajadores"].append(
                {
                    "id": p.usuario.id,
                    "nombre": p.usuario.get_full_name() or p.usuario.username,
                    "oficio": p.oficios or "Trabajador",
                    "ubicacion": p.ubicacion,
                    "foto": p.foto_perfil.url if p.foto_perfil else None,
                }
            )
    return JsonResponse(resultados)


@login_required
def perfil_trabajador_publico(request, trabajador_id):
    perfil = get_object_or_404(Perfil, usuario__id=trabajador_id)
    portafolio = []
    servicios = []
    ofertas = []
    if perfil.tipo == "trabajador":
        portafolio = PortafolioFoto.objects.filter(trabajador=perfil.usuario).order_by(
            "orden"
        )
        servicios = Servicio.objects.filter(
            trabajador=perfil.usuario, disponible=True
        ).order_by("-fecha_publicacion")
    else:
        ofertas = Oferta.objects.filter(empleador=perfil.usuario, activa=True).order_by(
            "-fecha_publicacion"
        )
    context = {
        "trabajador": perfil.usuario,
        "perfil": perfil,
        "portafolio_fotos": portafolio,
        "servicios": servicios,
        "ofertas": ofertas,
    }
    return render(request, "perfil_trabajador_publico.html", context)


# ========== CALIFICACIONES ==========
@login_required
def calificar_usuario(request):
    if request.method == "POST":
        calificado_id = request.POST.get("calificado_id")
        puntuacion = request.POST.get("puntuacion")
        comentario = request.POST.get("comentario", "")
        oferta_id = request.POST.get("oferta_id")
        servicio_id = request.POST.get("servicio_id")
        calificado = get_object_or_404(User, id=calificado_id)
        if calificado == request.user:
            return JsonResponse(
                {"success": False, "error": "No puedes calificarte a ti mismo"},
                status=400,
            )
        try:
            puntuacion = int(puntuacion)
            if puntuacion < 1 or puntuacion > 5:
                raise ValueError
        except:
            return JsonResponse(
                {"success": False, "error": "Puntuación inválida"}, status=400
            )
        calificacion, created = Calificacion.objects.update_or_create(
            calificador=request.user,
            calificado=calificado,
            oferta_id=oferta_id if oferta_id else None,
            servicio_id=servicio_id if servicio_id else None,
            defaults={"puntuacion": puntuacion, "comentario": comentario},
        )
        perfil = calificado.perfil
        todas_calif = Calificacion.objects.filter(calificado=calificado)
        total = todas_calif.count()
        promedio = (
            todas_calif.aggregate(models.Avg("puntuacion"))["puntuacion__avg"] or 0
        )
        perfil.promedio_calificacion = promedio
        perfil.total_calificaciones = total
        perfil.save()
        return JsonResponse(
            {
                "success": True,
                "promedio": float(promedio),
                "total": total,
                "mensaje": "¡Calificación guardada correctamente! Gracias por tu opinión.",
            }
        )
    return JsonResponse({"success": False, "error": "Método no permitido"}, status=400)


@login_required
def obtener_calificaciones(request, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)
    calificaciones = Calificacion.objects.filter(calificado=usuario).select_related(
        "calificador"
    )
    data = {
        "promedio": float(usuario.perfil.promedio_calificacion or 0),
        "total": usuario.perfil.total_calificaciones or 0,
        "calificaciones": [
            {
                "calificador": c.calificador.get_full_name() or c.calificador.username,
                "puntuacion": c.puntuacion,
                "comentario": c.comentario,
                "fecha": c.fecha.strftime("%d/%m/%Y"),
                "estrellas": "⭐" * c.puntuacion,
            }
            for c in calificaciones[:20]
        ],
    }
    return JsonResponse(data)


@login_required
def mis_calificaciones(request):
    recibidas = Calificacion.objects.filter(calificado=request.user).select_related(
        "calificador"
    )
    dadas = Calificacion.objects.filter(calificador=request.user).select_related(
        "calificado"
    )
    return JsonResponse(
        {
            "recibidas": [
                {
                    "de": c.calificador.get_full_name() or c.calificador.username,
                    "puntuacion": c.puntuacion,
                    "estrellas": "⭐" * c.puntuacion,
                    "comentario": c.comentario,
                    "fecha": c.fecha.strftime("%d/%m/%Y"),
                }
                for c in recibidas
            ],
            "dadas": [
                {
                    "a": c.calificado.get_full_name() or c.calificado.username,
                    "puntuacion": c.puntuacion,
                    "estrellas": "⭐" * c.puntuacion,
                    "comentario": c.comentario,
                    "fecha": c.fecha.strftime("%d/%m/%Y"),
                }
                for c in dadas
            ],
        }
    )


@login_required
def mapa(request):
    return render(request, "mapa.html")


@login_required
def api_ubicaciones(request):
    tipo = request.GET.get("tipo", "todos")
    perfiles = Perfil.objects.all().select_related("usuario")
    if tipo == "trabajadores":
        perfiles = perfiles.filter(tipo="trabajador")
    elif tipo == "empleadores":
        perfiles = perfiles.filter(tipo="empleador")
    ubicaciones = []
    for perfil in perfiles:
        if perfil.ubicacion and perfil.ubicacion != "No especificada":
            lat, lng = None, None
            if perfil.tipo == "trabajador":
                servicio = Servicio.objects.filter(
                    trabajador=perfil.usuario, latitud__isnull=False
                ).first()
                if servicio and servicio.latitud:
                    lat, lng = float(servicio.latitud), float(servicio.longitud)
            else:
                oferta = Oferta.objects.filter(
                    empleador=perfil.usuario, latitud__isnull=False
                ).first()
                if oferta and oferta.latitud:
                    lat, lng = float(oferta.latitud), float(oferta.longitud)
            if not lat:
                coords = obtener_coords_ciudad(perfil.ubicacion)
                lat, lng = coords[0], coords[1]
            ubicaciones.append(
                {
                    "id": perfil.usuario.id,
                    "nombre": perfil.usuario.get_full_name() or perfil.usuario.username,
                    "tipo": perfil.tipo,
                    "ubicacion": perfil.ubicacion,
                    "lat": lat,
                    "lng": lng,
                    "oficio": perfil.oficios
                    or (
                        perfil.nombre_empresa
                        if perfil.tipo == "empleador"
                        else "Trabajador"
                    ),
                    "foto": perfil.foto_perfil.url if perfil.foto_perfil else None,
                    "calificacion": float(perfil.promedio_calificacion or 0),
                    "disponible": (
                        perfil.disponible if perfil.tipo == "trabajador" else None
                    ),
                    "anios_experiencia": perfil.anios_experiencia or 0,
                }
            )
    return JsonResponse({"ubicaciones": ubicaciones})


@login_required
def api_todos_trabajadores(request):
    trabajadores = Perfil.objects.filter(tipo="trabajador").select_related("usuario")
    data = []
    for t in trabajadores:
        data.append(
            {
                "id": t.usuario.id,
                "nombre": t.usuario.get_full_name() or t.usuario.username,
                "oficio": t.oficios or "Trabajador",
                "foto": t.foto_perfil.url if t.foto_perfil else None,
                "calificacion": float(t.promedio_calificacion or 0),
                "total_calificaciones": t.total_calificaciones or 0,
                "disponible": t.disponible,
            }
        )
    return JsonResponse({"trabajadores": data})

@login_required
def editar_publicacion(request, pk):
    print(f"🔍 EDITAR PUBLICACIÓN - ID RECIBIDO: {pk}")
    
    # PRIMERO buscar en Publicacion (porque el ID que viene es de Publicacion)
    publicacion = Publicacion.objects.filter(id=pk, usuario=request.user).first()
    
    tipo = None
    objeto = None
    
    if publicacion:
        print(f"📝 Publicación encontrada - Tipo: {publicacion.tipo}")
        
        if publicacion.tipo == 'oferta':
            # Buscar la oferta asociada a esta publicación
            # Buscar por contenido (el título está en el contenido)
            contenido = publicacion.contenido
            # Extraer título después de "📢 OFERTA: " o "📢 NUEVA OFERTA: "
            import re
            match = re.search(r'OFERTA:\s*(.+?)(?:\n|$)', contenido)
            if match:
                titulo_oferta = match.group(1).strip()
                oferta = Oferta.objects.filter(empleador=request.user, titulo=titulo_oferta).first()
                if oferta:
                    tipo = 'oferta'
                    objeto = oferta
                    print(f"✅ Oferta encontrada - ID: {oferta.id}")
        
        elif publicacion.tipo == 'servicio':
            # Buscar el servicio asociado
            contenido = publicacion.contenido
            import re
            match = re.search(r'SERVICIO:\s*(.+?)(?:\n|$)', contenido)
            if match:
                titulo_servicio = match.group(1).strip()
                servicio = Servicio.objects.filter(trabajador=request.user, titulo=titulo_servicio).first()
                if servicio:
                    tipo = 'servicio'
                    objeto = servicio
                    print(f"✅ Servicio encontrado - ID: {servicio.id}")
        
        else:  # tipo == 'estado'
            tipo = 'estado'
            objeto = publicacion
            print(f"✅ Estado encontrado - ID: {publicacion.id}")
    
    if not objeto:
        messages.error(request, "No tienes permiso para editar esta publicación")
        return redirect('perfil')
    
    if request.method == "POST":
        if tipo == 'oferta':
            objeto.titulo = request.POST.get('titulo')
            objeto.oficio = request.POST.get('oficio')
            objeto.descripcion = request.POST.get('descripcion')
            objeto.ubicacion = request.POST.get('ubicacion')
            objeto.remuneracion = request.POST.get('remuneracion', '')
            objeto.fecha_limite = request.POST.get('fecha_limite') or None
            objeto.activa = request.POST.get('activa') == 'True'
            objeto.save()
            
            # Actualizar la publicación asociada
            publicacion.contenido = f"📢 OFERTA: {objeto.titulo}\n\n{objeto.descripcion[:200]}"
            publicacion.save()
            
        elif tipo == 'servicio':
            objeto.titulo = request.POST.get('titulo')
            objeto.oficio = request.POST.get('oficio')
            objeto.descripcion = request.POST.get('descripcion')
            objeto.ubicacion = request.POST.get('ubicacion')
            objeto.precio = request.POST.get('precio', '')
            objeto.disponible = request.POST.get('disponible') == 'on'
            objeto.save()
            
            # Actualizar la publicación asociada
            publicacion.contenido = f"🔧 SERVICIO: {objeto.titulo}\n\n{objeto.descripcion[:200]}"
            publicacion.save()
            
        else:  # estado
            objeto.contenido = request.POST.get('contenido')
            if request.FILES.get('imagen'):
                if objeto.imagen:
                    objeto.imagen.delete(save=False)
                objeto.imagen = request.FILES['imagen']
            elif request.POST.get('eliminar_imagen') == 'true':
                if objeto.imagen:
                    objeto.imagen.delete(save=False)
                    objeto.imagen = None
            objeto.save()
        
        messages.success(request, "Publicación actualizada correctamente")
        return redirect('perfil')
    
    context = {
        'tipo': tipo,
        'objeto': objeto,
        'es_oferta': tipo == 'oferta',
        'es_servicio': tipo == 'servicio',
        'es_estado': tipo == 'estado',
    }
    return render(request, 'editar_publicacion.html', context)


@login_required
def eliminar_publicacion(request, pk):
    # Buscar en las tres tablas
    oferta = Oferta.objects.filter(id=pk, empleador=request.user).first()
    servicio = Servicio.objects.filter(id=pk, trabajador=request.user).first()
    publicacion = Publicacion.objects.filter(id=pk, usuario=request.user).first()
    
    if oferta:
        # Eliminar publicación asociada
        Publicacion.objects.filter(usuario=request.user, tipo='oferta', contenido__icontains=oferta.titulo).delete()
        oferta.delete()
    elif servicio:
        # Eliminar publicación asociada
        Publicacion.objects.filter(usuario=request.user, tipo='servicio', contenido__icontains=servicio.titulo).delete()
        servicio.delete()
    elif publicacion:
        publicacion.delete()
    else:
        messages.error(request, "No tienes permiso para eliminar esta publicación")
        return redirect('perfil')
    
    messages.success(request, "Publicación eliminada correctamente")
    return redirect('perfil')


@login_required
def editar_comentario(request, pk):
    comentario = get_object_or_404(Comentario, pk=pk, usuario=request.user)
    if request.method == "POST":
        comentario.texto = request.POST.get("texto")
        comentario.save()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False})


@login_required
def eliminar_comentario(request, pk):
    comentario = get_object_or_404(Comentario, pk=pk, usuario=request.user)
    comentario.delete()
    return JsonResponse({"success": True})


@login_required
def editar_portafolio(request, foto_id):
    foto = get_object_or_404(PortafolioFoto, id=foto_id, trabajador=request.user)
    
    if request.method == "POST":
        titulo = request.POST.get("titulo", "")
        descripcion = request.POST.get("descripcion", "")
        foto.titulo = titulo
        foto.descripcion = descripcion
        
        nueva_imagen = request.FILES.get("imagen")
        if nueva_imagen:
            # Eliminar imagen anterior
            if foto.imagen:
                foto.imagen.delete(save=False)
            foto.imagen = nueva_imagen
        
        foto.save()
        messages.success(request, "Foto actualizada correctamente")
        return redirect("perfil")
    
    # Si es GET, mostrar formulario
    context = {
        'foto': foto,
        'titulo': foto.titulo,
        'descripcion': foto.descripcion,
        'imagen_url': foto.imagen.url
    }
    return render(request, "editar_portafolio.html", context)


@login_required
def editar_oferta_api(request, oferta_id):
    oferta = get_object_or_404(Oferta, id=oferta_id, empleador=request.user)
    if request.method == "POST":
        oferta.titulo = request.POST.get("titulo")
        oferta.oficio = request.POST.get("oficio")
        oferta.descripcion = request.POST.get("descripcion")
        oferta.ubicacion = request.POST.get("ubicacion")
        oferta.remuneracion = request.POST.get("remuneracion", "")
        oferta.fecha_limite = request.POST.get("fecha_limite") or None
        oferta.save()
        publicacion = Publicacion.objects.filter(
            usuario=request.user, tipo="oferta"
        ).first()
        if publicacion:
            publicacion.contenido = (
                f"📢 NUEVA OFERTA: {oferta.titulo}\n\n{oferta.descripcion[:200]}"
            )
            publicacion.save()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False})


@login_required
def eliminar_oferta_api(request, oferta_id):
    oferta = get_object_or_404(Oferta, id=oferta_id, empleador=request.user)
    Publicacion.objects.filter(
        usuario=request.user, tipo="oferta", contenido__icontains=oferta.titulo
    ).delete()
    oferta.delete()
    return JsonResponse({"success": True})


def obtener_coords_ciudad(ubicacion):
    coordenadas = {
        "la paz": [-16.5000, -68.1500],
        "santa cruz": [-17.7836, -63.1821],
        "cochabamba": [-17.3895, -66.1568],
        "el alto": [-16.5100, -68.1700],
        "sucre": [-19.0333, -65.2627],
        "potosi": [-19.5836, -65.7531],
        "tarija": [-21.5355, -64.7295],
        "oruro": [-17.9667, -67.1167],
        "trinidad": [-14.8333, -64.9000],
        "cobija": [-11.0267, -68.7692],
    }
    if not ubicacion:
        return [-16.5000, -68.1500]
    ubicacion_lower = ubicacion.lower()
    for key, coord in coordenadas.items():
        if key in ubicacion_lower:
            return coord
    return [-16.5000, -68.1500]


@login_required
def api_usuarios(request):
    if not request.user.is_superuser:
        return JsonResponse({"error": "No autorizado"}, status=403)
    usuarios = User.objects.all().select_related("perfil")
    data = {
        "usuarios": [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "tipo": u.perfil.tipo if hasattr(u, "perfil") else "empleador",
                "is_active": u.is_active,
                "date_joined": u.date_joined.strftime("%d/%m/%Y"),
            }
            for u in usuarios
        ]
    }
    return JsonResponse(data)


@login_required
def cambiar_estado_usuario(request, user_id):
    if not request.user.is_superuser:
        return JsonResponse({"error": "No autorizado"}, status=403)
    usuario = get_object_or_404(User, id=user_id)
    usuario.is_active = not usuario.is_active
    usuario.save()
    return JsonResponse({"success": True, "is_active": usuario.is_active})


# ========== MÓDULO ADMINISTRACIÓN Y MODERACIÓN ==========
@login_required
def usuarios_admin(request):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("dashboard")
    usuarios = (
        User.objects.select_related("perfil")
        .prefetch_related("reportes_recibidos")
        .order_by("-date_joined")
    )
    context = {
        "usuarios": usuarios,
        "total_usuarios": usuarios.count(),
        "usuarios_activos": usuarios.filter(is_active=True).count(),
        "usuarios_bloqueados": usuarios.filter(is_active=False).count(),
    }
    return render(request, "usuarios_admin.html", context)


@login_required
def reportes_admin(request):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("dashboard")
    from django.core.paginator import Paginator
    from .models import Reporte

    estado = request.GET.get("estado", "pendiente")
    reportes_base = Reporte.objects.select_related(
        "reportante", "usuario_reportado", "publicacion", "comentario"
    ).order_by("-fecha")
    total_reportes = reportes_base.count()
    pendientes = reportes_base.filter(estado="pendiente").count()
    revisados = reportes_base.filter(estado="revisado").count()
    resueltos = reportes_base.filter(estado="resuelto").count()
    if estado in ["pendiente", "revisado", "resuelto"]:
        reportes_filtrados = reportes_base.filter(estado=estado)
    else:
        reportes_filtrados = reportes_base
    paginator = Paginator(reportes_filtrados, 5)
    page_number = request.GET.get("page")
    reportes = paginator.get_page(page_number)
    context = {
        "reportes": reportes,
        "estado_actual": estado,
        "total_reportes": total_reportes,
        "pendientes": pendientes,
        "revisados": revisados,
        "resueltos": resueltos,
    }
    return render(request, "reportes_admin.html", context)


@login_required
def comentarios_admin(request):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("dashboard")
    comentarios_pendientes = Comentario.objects.filter(revisado=False).count()
    comentarios = Comentario.objects.select_related("usuario", "publicacion").order_by(
        "revisado", "-fecha"
    )
    context = {
        "comentarios": comentarios,
        "comentarios_pendientes": comentarios_pendientes,
        "total_comentarios": comentarios.count(),
    }
    return render(request, "comentarios_admin.html", context)


@login_required
def publicaciones_admin(request):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("dashboard")
    publicaciones = Publicacion.objects.select_related("usuario").order_by(
        "-fecha_creacion"
    )
    context = {
        "publicaciones": publicaciones,
        "total_publicaciones": publicaciones.count(),
    }
    return render(request, "publicaciones_admin.html", context)


@login_required
def historial_admin(request):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("dashboard")
    historial = HistorialAdmin.objects.select_related("administrador").order_by(
        "-fecha"
    )
    context = {"historial": historial}
    return render(request, "historial_admin.html", context)


@login_required
def bloquear_usuario(request, user_id):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("dashboard")
    usuario = get_object_or_404(User, id=user_id)
    if usuario == request.user:
        messages.error(request, "No puedes bloquear tu propia cuenta administradora.")
        return redirect("usuarios_admin")
    usuario.is_active = False
    usuario.save()
    HistorialAdmin.objects.create(
        administrador=request.user,
        accion="Usuario bloqueado",
        elemento_afectado=usuario.username,
        resultado="Bloqueado",
    )
    messages.success(request, "Usuario bloqueado correctamente.")
    return redirect("usuarios_admin")


@login_required
def reactivar_usuario(request, user_id):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("dashboard")
    usuario = get_object_or_404(User, id=user_id)
    usuario.is_active = True
    usuario.save()
    HistorialAdmin.objects.create(
        administrador=request.user,
        accion="Usuario reactivado",
        elemento_afectado=usuario.username,
        resultado="Reactivado",
    )
    messages.success(request, "Usuario reactivado correctamente.")
    return redirect("usuarios_admin")


@login_required
def admin_eliminar_comentario(request, comentario_id):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("dashboard")
    comentario = get_object_or_404(Comentario, id=comentario_id)
    HistorialAdmin.objects.create(
        administrador=request.user,
        accion="Comentario eliminado",
        elemento_afectado=f"Comentario de {comentario.usuario.username}",
        resultado="Eliminado",
    )
    comentario.delete()
    return redirect("comentarios_admin")


@login_required
def admin_marcar_comentario_revisado(request, comentario_id):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("dashboard")
    comentario = get_object_or_404(Comentario, id=comentario_id)
    comentario.revisado = True
    comentario.save()
    HistorialAdmin.objects.create(
        administrador=request.user,
        accion="Comentario revisado",
        elemento_afectado=f"Comentario de {comentario.usuario.username}",
        resultado="Marcado como revisado",
    )
    return redirect("comentarios_admin")


@login_required
def admin_eliminar_publicacion(request, publicacion_id):
    if not request.user.is_staff and not request.user.is_superuser:
        return redirect("dashboard")
    publicacion = get_object_or_404(Publicacion, id=publicacion_id)
    nombre_usuario = publicacion.usuario.username
    contenido = publicacion.contenido[:40]
    HistorialAdmin.objects.create(
        administrador=request.user,
        accion="Publicación eliminada",
        elemento_afectado=f"{nombre_usuario} - {contenido}",
        resultado="Eliminado",
    )
    publicacion.delete()
    return redirect("publicaciones_admin")


@login_required
def admin_marcar_reporte_revisado(request, reporte_id):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("dashboard")
    reporte = get_object_or_404(Reporte, id=reporte_id)
    reporte.estado = "revisado"
    reporte.save()
    HistorialAdmin.objects.create(
        administrador=request.user,
        accion="Reporte revisado",
        elemento_afectado=f"Reporte de {reporte.reportante.username}",
        resultado="Revisado",
    )
    return redirect("reportes_admin")


@login_required
def admin_resolver_reporte(request, reporte_id):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("dashboard")
    reporte = get_object_or_404(Reporte, id=reporte_id)
    reporte.estado = "resuelto"
    reporte.save()
    HistorialAdmin.objects.create(
        administrador=request.user,
        accion="Reporte resuelto",
        elemento_afectado=f"Reporte de {reporte.reportante.username}",
        resultado="Resuelto",
    )
    return redirect("reportes_admin")


@login_required
def admin_advertir_usuario(request, user_id):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("dashboard")
    usuario = get_object_or_404(User, id=user_id)
    HistorialAdmin.objects.create(
        administrador=request.user,
        accion="Usuario advertido",
        elemento_afectado=usuario.username,
        resultado="Advertencia registrada",
    )
    messages.success(request, "Advertencia registrada correctamente.")
    return redirect("usuarios_admin")


@login_required
def admin_notificar_usuario(request, user_id):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("dashboard")
    usuario = get_object_or_404(User, id=user_id)
    HistorialAdmin.objects.create(
        administrador=request.user,
        accion="Usuario notificado",
        elemento_afectado=usuario.username,
        resultado="Notificación administrativa registrada",
    )
    messages.success(request, "Notificación administrativa registrada correctamente.")
    return redirect("usuarios_admin")


@login_required
def marcar_publicacion_revisada(request, publicacion_id):
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("dashboard")
    publicacion = get_object_or_404(Publicacion, id=publicacion_id)
    publicacion.revisada = True
    publicacion.save()
    HistorialAdmin.objects.create(
        administrador=request.user,
        accion="Publicación revisada",
        elemento_afectado=f"Publicación #{publicacion.id}",
        resultado="Revisada",
    )
    return redirect("publicaciones_admin")


# ========== EDITAR OFERTA Y SERVICIO ==========
@login_required
def editar_oferta(request, pk):
    oferta = get_object_or_404(Oferta, pk=pk, empleador=request.user)
    if request.method == "POST":
        if (
            request.headers.get("X-Requested-With") == "XMLHttpRequest"
            and request.POST.get("eliminar_imagen") == "true"
        ):
            if hasattr(oferta, "imagen") and oferta.imagen:
                oferta.imagen.delete(save=False)
                oferta.imagen = None
                oferta.save()
            return JsonResponse({"success": True})

        oferta.titulo = request.POST.get("titulo")
        oferta.oficio = request.POST.get("oficio")
        oferta.descripcion = request.POST.get("descripcion")
        oferta.ubicacion = request.POST.get("ubicacion")
        oferta.remuneracion = request.POST.get("remuneracion", "")
        oferta.fecha_limite = request.POST.get("fecha_limite") or None
        oferta.latitud = request.POST.get("latitud") or None
        oferta.longitud = request.POST.get("longitud") or None

        if request.FILES.get("imagen"):
            if hasattr(oferta, "imagen") and oferta.imagen:
                oferta.imagen.delete(save=False)
            oferta.imagen = request.FILES["imagen"]

        oferta.save()

        publicacion = Publicacion.objects.filter(
            usuario=request.user, tipo="oferta"
        ).first()
        if publicacion:
            publicacion.contenido = (
                f"📢 OFERTA: {oferta.titulo}\n\n{oferta.descripcion[:200]}"
            )
            if hasattr(oferta, "imagen") and oferta.imagen:
                publicacion.imagen = oferta.imagen
            publicacion.save()

        messages.success(request, "Oferta actualizada correctamente")
        return redirect("perfil")

    context = {"oferta": oferta}
    return render(request, "editar_oferta.html", context)


@login_required
def editar_servicio(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk, trabajador=request.user)
    if request.method == "POST":
        if (
            request.headers.get("X-Requested-With") == "XMLHttpRequest"
            and request.POST.get("eliminar_imagen") == "true"
        ):
            if servicio.imagen:
                servicio.imagen.delete(save=False)
                servicio.imagen = None
                servicio.save()
            return JsonResponse({"success": True})

        servicio.titulo = request.POST.get("titulo")
        servicio.oficio = request.POST.get("oficio")
        servicio.descripcion = request.POST.get("descripcion")
        servicio.ubicacion = request.POST.get("ubicacion")
        servicio.precio = request.POST.get("precio", "")
        servicio.disponible = request.POST.get("disponible") == "on"
        # Reemplazar coma por punto en coordenadas
        lat_raw = request.POST.get('latitud', '')
        lng_raw = request.POST.get('longitud', '')
        servicio.latitud = lat_raw.replace(',', '.') if lat_raw else None
        servicio.longitud = lng_raw.replace(',', '.') if lng_raw else None

        if request.FILES.get("imagen"):
            if servicio.imagen:
                servicio.imagen.delete(save=False)
            servicio.imagen = request.FILES["imagen"]

        servicio.save()

        publicacion = Publicacion.objects.filter(
            usuario=request.user, tipo="servicio"
        ).first()
        if publicacion:
            publicacion.contenido = (
                f"🔧 SERVICIO: {servicio.titulo}\n\n{servicio.descripcion[:200]}"
            )
            if servicio.imagen:
                publicacion.imagen = servicio.imagen
            publicacion.save()

        messages.success(request, "Servicio actualizado correctamente")
        return redirect("perfil")

    context = {"servicio": servicio}
    return render(request, "editar_servicio.html", context)


@login_required
def editar_descripcion(request):
    """Vista para editar la descripción personal"""
    if request.method == "POST":
        descripcion = request.POST.get("descripcion_personal", "")
        perfil = request.user.perfil
        perfil.descripcion_personal = descripcion
        perfil.save()
        messages.success(request, "Descripción actualizada correctamente")
        return redirect("perfil")
    
    context = {
        'descripcion_actual': request.user.perfil.descripcion_personal or '',
    }
    return render(request, "editar_descripcion.html", context)


@login_required
def editar_experiencia(request):
    """Vista para editar los años de experiencia"""
    if request.method == "POST":
        anios = request.POST.get("anios_experiencia", 0)
        try:
            anios = int(anios)
        except ValueError:
            anios = 0
        perfil = request.user.perfil
        perfil.anios_experiencia = anios
        perfil.save()
        messages.success(request, "Experiencia actualizada correctamente")
        return redirect("perfil")
    
    context = {
        'anios_actual': request.user.perfil.anios_experiencia or 0,
    }
    return render(request, "editar_experiencia.html", context)


@login_required
def comentarios_lista(request, publicacion_id):
    """Vista para ver y gestionar comentarios de una publicación"""
    publicacion = get_object_or_404(Publicacion, id=publicacion_id)
    comentarios = publicacion.comentarios.all().order_by("fecha")
    
    if request.method == "POST":
        texto = request.POST.get("texto", "").strip()
        if texto:
            Comentario.objects.create(
                usuario=request.user,
                publicacion=publicacion,
                texto=texto
            )
            messages.success(request, "Comentario agregado")
        return redirect("comentarios_lista", publicacion_id=publicacion_id)
    
    context = {
        'publicacion': publicacion,
        'comentarios': comentarios,
    }
    return render(request, "comentarios_lista.html", context)