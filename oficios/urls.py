from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("perfil/", views.perfil_user, name="perfil"),
    path("logout/", views.logout_view, name="logout"),
    path("publicar-oferta/", views.publicar_oferta, name="publicar_oferta"),
    path("ofrecer-servicio/", views.ofrecer_servicio, name="ofrecer_servicio"),
    path("publicar/", views.publicar_estado, name="publicar_estado"),
    path("like/<int:publicacion_id>/", views.like_toggle, name="like_toggle"),
    path("comentar/<int:publicacion_id>/", views.comentar, name="comentar"),
    path(
        "comentarios/<int:publicacion_id>/",
        views.listar_comentarios,
        name="listar_comentarios",
    ),
    path("empleos/", views.empleos, name="empleos"),
    path("trabajadores/", views.trabajadores, name="trabajadores"),
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
    path("perfil/cambiar-foto/", views.cambiar_foto, name="cambiar_foto"),
    path("perfil/editar-campo/", views.editar_campo, name="editar_campo"),
    path(
        "perfil/toggle-disponibilidad/",
        views.toggle_disponibilidad,
        name="toggle_disponibilidad",
    ),
    path("perfil/editar-perfil/", views.editar_perfil, name="editar_perfil"),
    path("perfil/subir-portafolio/", views.subir_portafolio, name="subir_portafolio"),
    path(
        "perfil/eliminar-portafolio/<int:foto_id>/",
        views.eliminar_portafolio,
        name="eliminar_portafolio",
    ),
    path("api/buscar-ajax/", views.api_buscar_ajax, name="api_buscar_ajax"),
    path(
        "perfil-trabajador/<int:trabajador_id>/",
        views.perfil_trabajador_publico,
        name="perfil_trabajador_publico",
    ),
    path("calificar/", views.calificar_usuario, name="calificar_usuario"),
    path(
        "api/calificaciones/<int:usuario_id>/",
        views.obtener_calificaciones,
        name="obtener_calificaciones",
    ),
    path(
        "api/mis-calificaciones/", views.mis_calificaciones, name="mis_calificaciones"
    ),
    path("recuperar-password/", views.recuperar_password, name="recuperar_password"),
    path(
        "reset-password/<uidb64>/<token>/", views.reset_password, name="reset_password"
    ),
    path("mapa/", views.mapa, name="mapa"),
    path("api/ubicaciones/", views.api_ubicaciones, name="api_ubicaciones"),
    path(
        "api/todos-trabajadores/",
        views.api_todos_trabajadores,
        name="api_todos_trabajadores",
    ),
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
    path(
        "comentario/editar/<int:pk>/", views.editar_comentario, name="editar_comentario"
    ),
    path(
        "comentario/eliminar/<int:pk>/",
        views.eliminar_comentario,
        name="eliminar_comentario",
    ),
    path(
        "perfil/editar-portafolio/<int:foto_id>/",
        views.editar_portafolio,
        name="editar_portafolio",
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
    # Mod admin
    path("dashboard-admin/", views.dashboard_admin, name="dashboard_admin"),
    path("api/usuarios/", views.api_usuarios, name="api_usuarios"),
    path(
        "api/usuario/cambiar-estado/<int:user_id>/",
        views.cambiar_estado_usuario,
        name="cambiar_estado_usuario",
    ),
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
    # Editar oferta y servicio
    path("oferta/editar/<int:pk>/", views.editar_oferta, name="editar_oferta"),
    path("servicio/editar/<int:pk>/", views.editar_servicio, name="editar_servicio"),
    # Para editar perfil completo
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
    path(
        "perfil/toggle-disponibilidad/",
        views.toggle_disponibilidad,
        name="toggle_disponibilidad",
    ),
    # Para portafolio
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
    # Para publicaciones
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
    path("like/<int:publicacion_id>/", views.like_toggle, name="like_toggle"),
    path(
        "comentarios/<int:publicacion_id>/",
        views.comentarios_lista,
        name="comentarios_lista",
    ),
    # Para ofertas y servicios
    path("oferta/editar/<int:pk>/", views.editar_oferta, name="editar_oferta"),
    path("servicio/editar/<int:pk>/", views.editar_servicio, name="editar_servicio"),
    # Editar publicación (para oferta, servicio y estado)
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
    path("perfil/editar-portafolio/<int:foto_id>/", views.editar_portafolio, name="editar_portafolio"),
]
