from django.urls import path
from . import views

urlpatterns = [
    # Públicas
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("recuperar-password/", views.recuperar_password, name="recuperar_password"),
    path(
        "reset-password/<uidb64>/<token>/", views.reset_password, name="reset_password"
    ),
    # Dashboard y perfil
    path("dashboard/", views.dashboard, name="dashboard"),
    path("perfil/", views.perfil_user, name="perfil"),
    path("perfil/editar/", views.editar_perfil, name="editar_perfil"),
    path(
        "perfil/editar-descripcion/",
        views.editar_descripcion,
        name="editar_descripcion",
    ),
    path(
        "perfil/editar-experiencia/",
        views.editar_experiencia,
        name="editar_experiencia",
    ),
    path("perfil/cambiar-foto/", views.cambiar_foto, name="cambiar_foto"),
    path("perfil/editar-campo/", views.editar_campo, name="editar_campo"),
    path(
        "perfil/toggle-disponibilidad/",
        views.toggle_disponibilidad,
        name="toggle_disponibilidad",
    ),
    # Publicaciones
    path("publicar/", views.publicar_estado, name="publicar_estado"),
    path("publicar-oferta/", views.publicar_oferta, name="publicar_oferta"),
    path("ofrecer-servicio/", views.ofrecer_servicio, name="ofrecer_servicio"),
    path(
        "publicacion/editar/<int:pk>/",
        views.editar_publicacion,
        name="editar_publicacion",
    ),
    path(
        "publicacion/eliminar/<int:pk>/",
        views.eliminar_publicacion,
        name="eliminar_publicacion",
    ),
    # Likes y comentarios
    path("like/<int:publicacion_id>/", views.like_toggle, name="like_toggle"),
    path("comentar/<int:publicacion_id>/", views.comentar, name="comentar"),
    path(
        "comentarios/<int:publicacion_id>/",
        views.listar_comentarios,
        name="listar_comentarios",
    ),
    path(
        "comentario/editar/<int:pk>/", views.editar_comentario, name="editar_comentario"
    ),
    path(
        "comentario/eliminar/<int:pk>/",
        views.eliminar_comentario,
        name="eliminar_comentario",
    ),
    # Empleos y trabajadores
    path("empleos/", views.empleos, name="empleos"),
    path("trabajadores/", views.trabajadores, name="trabajadores"),
    path("mapa/", views.mapa, name="mapa"),

    # Botón reportar
    path("reportar-oferta/<int:oferta_id>/", views.reportar_oferta, name="reportar_oferta"),
    path("reportar-servicio/<int:servicio_id>/", views.reportar_servicio, name="reportar_servicio"),
    
    # Portafolio
    path("perfil/subir-portafolio/", views.subir_portafolio, name="subir_portafolio"),
    path(
        "perfil/editar-portafolio/<int:foto_id>/",
        views.editar_portafolio,
        name="editar_portafolio",
    ),
    path(
        "perfil/eliminar-portafolio/<int:foto_id>/",
        views.eliminar_portafolio,
        name="eliminar_portafolio",
    ),
    # APIs
    path(
        "api/oferta/<int:oferta_id>/",
        views.api_oferta_detalle,
        name="api_oferta_detalle",
    ),
    path(
        "api/servicio/<int:servicio_id>/",
        views.api_servicio_detalle,
        name="api_servicio_detalle",
    ),
    path("api/buscar-ajax/", views.api_buscar_ajax, name="api_buscar_ajax"),
    path("api/ubicaciones/", views.api_ubicaciones, name="api_ubicaciones"),
    path(
        "api/todos-trabajadores/",
        views.api_todos_trabajadores,
        name="api_todos_trabajadores",
    ),
    path("api/usuarios/", views.api_usuarios, name="api_usuarios"),
    path(
        "api/usuario/cambiar-estado/<int:user_id>/",
        views.cambiar_estado_usuario,
        name="cambiar_estado_usuario",
    ),
    path(
        "api/calificaciones/<int:usuario_id>/",
        views.obtener_calificaciones,
        name="obtener_calificaciones",
    ),
    path(
        "api/mis-calificaciones/", views.mis_calificaciones, name="mis_calificaciones"
    ),
    path(
        "api/oferta/editar/<int:oferta_id>/",
        views.editar_oferta_api,
        name="editar_oferta_api",
    ),
    path(
        "api/oferta/eliminar/<int:oferta_id>/",
        views.eliminar_oferta_api,
        name="eliminar_oferta_api",
    ),
    # Calificaciones
    path("calificar/", views.calificar_usuario, name="calificar_usuario"),
    # Perfil público
    path(
        "perfil-trabajador/<int:trabajador_id>/",
        views.perfil_trabajador_publico,
        name="perfil_trabajador_publico",
    ),
    # Admin
    path("dashboard-admin/", views.dashboard_admin, name="dashboard_admin"),
    path("usuarios-admin/", views.usuarios_admin, name="usuarios_admin"),
    path("reportes-admin/", views.reportes_admin, name="reportes_admin"),
    path("comentarios-admin/", views.comentarios_admin, name="comentarios_admin"),
    path("publicaciones-admin/", views.publicaciones_admin, name="publicaciones_admin"),
    path("historial-admin/", views.historial_admin, name="historial_admin"),
    path(
        "bloquear-usuario/<int:user_id>/",
        views.bloquear_usuario,
        name="bloquear_usuario",
    ),
    path(
        "reactivar-usuario/<int:user_id>/",
        views.reactivar_usuario,
        name="reactivar_usuario",
    ),
    path(
        "admin-advertir-usuario/<int:user_id>/",
        views.admin_advertir_usuario,
        name="admin_advertir_usuario",
    ),
    path(
        "admin-notificar-usuario/<int:user_id>/",
        views.admin_notificar_usuario,
        name="admin_notificar_usuario",
    ),
    path(
        "admin-eliminar-comentario/<int:comentario_id>/",
        views.admin_eliminar_comentario,
        name="admin_eliminar_comentario",
    ),
    path(
        "admin-revisar-comentario/<int:comentario_id>/",
        views.admin_marcar_comentario_revisado,
        name="admin_marcar_comentario_revisado",
    ),
    path(
        "admin-eliminar-publicacion/<int:publicacion_id>/",
        views.admin_eliminar_publicacion,
        name="admin_eliminar_publicacion",
    ),
    path(
        "admin-reporte-revisado/<int:reporte_id>/",
        views.admin_marcar_reporte_revisado,
        name="admin_marcar_reporte_revisado",
    ),
    path(
        "admin-reporte-resuelto/<int:reporte_id>/",
        views.admin_resolver_reporte,
        name="admin_resolver_reporte",
    ),
    path(
        "publicacion-revisar/<int:publicacion_id>/",
        views.marcar_publicacion_revisada,
        name="marcar_publicacion_revisada",
    ),
]
