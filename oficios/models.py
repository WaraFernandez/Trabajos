from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone  # ← IMPORTANTE: agregar esta línea


class Perfil(models.Model):
    TIPO_CHOICES = (
        ("trabajador", "Trabajador de Oficio"),
        ("empleador", "Empleador"),
    )

    usuario = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="perfil"
    )
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)

    # --- Campos comunes para ambos ---
    telefono = models.CharField(max_length=25)
    ubicacion = models.CharField(max_length=150)
    foto_perfil = models.ImageField(upload_to="perfiles/", blank=True, null=True)

    # --- Campos del TRABAJADOR ---
    oficios = models.CharField(max_length=200, blank=True, null=True)
    descripcion_personal = models.TextField(blank=True, null=True)
    anios_experiencia = models.PositiveIntegerField(default=0, blank=True, null=True)
    disponible = models.BooleanField(default=True)
    fotos_portafolio = models.TextField(blank=True, null=True)
    contactos_externos = models.JSONField(blank=True, null=True)

    # --- Campos del EMPLEADOR ---
    nombre_empresa = models.CharField(max_length=150, blank=True, null=True)
    rubro = models.CharField(max_length=100, blank=True, null=True)

    # --- Reputación ---
    promedio_calificacion = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.0
    )
    total_calificaciones = models.PositiveIntegerField(default=0)

    # --- Control ---
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.get_tipo_display()}"

    @property
    def nombre_completo(self):
        return self.usuario.get_full_name() or self.usuario.username

    @property
    def es_trabajador(self):
        return self.tipo == "trabajador"

    @property
    def es_empleador(self):
        return self.tipo == "empleador"


class Publicacion(models.Model):
    TIPO_CHOICES = (
        ("oferta", "Oferta laboral"),
        ("servicio", "Servicio ofrecido"),
        ("estado", "Estado personal"),
    )

    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="publicaciones"
    )
    contenido = models.TextField()
    revisada = models.BooleanField(default=False)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default="estado")
    imagen = models.ImageField(upload_to="publicaciones/", blank=True, null=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.usuario.username} - {self.fecha_creacion.strftime('%d/%m/%Y')}"

    class Meta:
        ordering = ["-fecha_creacion"]


class Like(models.Model):
    """Likes en publicaciones"""

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    publicacion = models.ForeignKey(
        Publicacion, on_delete=models.CASCADE, related_name="likes"
    )
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            "usuario",
            "publicacion",
        )  # Un like por usuario por publicación
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.usuario.username} ❤️ {self.publicacion.id}"


class Comentario(models.Model):
    """Comentarios en publicaciones"""

    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comentarios"
    )
    publicacion = models.ForeignKey(
        Publicacion, on_delete=models.CASCADE, related_name="comentarios"
    )
    texto = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    revisado = models.BooleanField(default=False)

    class Meta:
        ordering = ["fecha"]  # Del más antiguo al más reciente

    def __str__(self):
        return f"{self.usuario.username} 💬 {self.publicacion.id}"


class Oferta(models.Model):
    empleador = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ofertas",
        limit_choices_to={"perfil__tipo": "empleador"},
    )
    titulo = models.CharField(max_length=200)
    oficio = models.CharField(max_length=100)
    descripcion = models.TextField()
    ubicacion = models.CharField(max_length=150)
    remuneracion = models.CharField(max_length=100, blank=True)
    fecha_limite = models.DateField(blank=True, null=True)
    activa = models.BooleanField(default=True)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    # En models.py, dentro de la clase Oferta:
    latitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    def __str__(self):
        return self.titulo

    class Meta:
        ordering = ["-fecha_publicacion"]


class Servicio(models.Model):
    trabajador = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="servicios",
        limit_choices_to={"perfil__tipo": "trabajador"},
    )
    titulo = models.CharField(max_length=200)
    oficio = models.CharField(max_length=100)
    descripcion = models.TextField()
    ubicacion = models.CharField(max_length=150)
    precio = models.CharField(max_length=100, blank=True)
    disponible = models.BooleanField(default=True)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    # En models.py, dentro de la clase Servicio:
    latitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitud = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    imagen = models.ImageField(upload_to="servicios/", blank=True, null=True)  # ← AGREGAR ESTO

    def __str__(self):
        return self.titulo

    class Meta:
        ordering = ["-fecha_publicacion"]


class PortafolioFoto(models.Model):
    trabajador = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="portafolio_fotos",
        limit_choices_to={"perfil__tipo": "trabajador"},
    )
    titulo = models.CharField(max_length=100, blank=True)
    descripcion = models.CharField(max_length=200, blank=True)
    imagen = models.ImageField(upload_to="portafolio/")
    fecha_subida = models.DateTimeField(auto_now_add=True)
    orden = models.IntegerField(default=0)

    class Meta:
        ordering = ["orden", "-fecha_subida"]

    def __str__(self):
        return f"{self.trabajador.username} - {self.titulo or 'Foto'}"


class Calificacion(models.Model):
    """Calificaciones que los usuarios se dan entre sí"""

    CALIFICACION_CHOICES = (
        (1, "⭐ Muy malo"),
        (2, "⭐⭐ Malo"),
        (3, "⭐⭐⭐ Regular"),
        (4, "⭐⭐⭐⭐ Bueno"),
        (5, "⭐⭐⭐⭐⭐ Excelente"),
    )

    # Quien califica
    calificador = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="calificaciones_hechas"
    )

    # Quien recibe la calificación
    calificado = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="calificaciones_recibidas"
    )

    # Puede estar asociado a una oferta o servicio específico
    oferta = models.ForeignKey(
        Oferta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="calificaciones",
    )
    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="calificaciones",
    )
    
    

    puntuacion = models.IntegerField(choices=CALIFICACION_CHOICES)
    comentario = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("calificador", "calificado", "oferta", "servicio")
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.calificador.username} → {self.calificado.username}: {self.puntuacion}⭐"

#modulo admin
class Reporte(models.Model):
    TIPO_CHOICES = (
        ("comentario", "Comentario"),
        ("publicacion", "Publicación"),
        ("usuario", "Usuario"),
    )

    ESTADO_CHOICES = (
        ("pendiente", "Pendiente"),
        ("revisado", "Revisado"),
        ("resuelto", "Resuelto"),
    )

    reportante = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reportes_realizados")
    usuario_reportado = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reportes_recibidos", null=True, blank=True)
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, null=True, blank=True)
    comentario = models.ForeignKey(Comentario, on_delete=models.CASCADE, null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    motivo = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="pendiente")
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} - {self.estado}"


class HistorialAdmin(models.Model):
    administrador = models.ForeignKey(User, on_delete=models.CASCADE)
    accion = models.CharField(max_length=200)
    elemento_afectado = models.CharField(max_length=200)
    resultado = models.CharField(max_length=100)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.administrador.username} - {self.accion}"