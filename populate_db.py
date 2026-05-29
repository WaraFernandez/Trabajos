#!/usr/bin/env python
import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bytegirls.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from oficios.models import Perfil, Publicacion, Oferta, Servicio, Calificacion, Like, Comentario

print("=" * 60)
print("   CARGANDO DATOS DE PRUEBA EN CHAMBA")
print("=" * 60)

# ========== DATOS ==========
TRABAJADORES = [
    ("Carlos", "Gutierrez", "electricista", "Electricista con 8 años de experiencia", 8),
    ("Maria", "Fernandez", "plomera", "Plomera certificada, reparaciones 24/7", 5),
    ("Jose", "Mamani", "carpintero", "Carpintero artesanal, muebles a medida", 10),
    ("Ana", "Quispe", "cocinera", "Chef profesional, comida boliviana", 6),
    ("Pedro", "Vargas", "pintor", "Pintor de interiores y exteriores", 4),
    ("Lucia", "Torrez", "limpieza", "Limpieza general para hogares y oficinas", 3),
    ("Roberto", "Flores", "mecanico", "Mecánico automotriz con taller propio", 12),
    ("Sofia", "Rios", "jardinera", "Diseño y mantenimiento de jardines", 7),
]

EMPLEADORES = [
    ("Construcciones", "Andes", "Constructora", "Construcción y remodelaciones"),
    ("Servicios", "Integrales", "Servicios", "Mantenimiento industrial"),
    ("Tecno", "Fix", "Tecnología", "Reparación de equipos"),
    ("Hogar", "Seguro", "Hogar", "Servicios para el hogar"),
    ("Auto", "Center", "Automotriz", "Taller mecánico"),
]

UBICACIONES = [
    "La Paz, Zona Sur", "La Paz, Centro", "El Alto, Villa Bolivar",
    "Santa Cruz, Equipetrol", "Santa Cruz, La Ramada",
    "Cochabamba, Queru Queru", "Cochabamba, Cala Cala",
    "Sucre, Centro", "Tarija, La Victoria"
]

PRECIOS = ["150 Bs", "200 Bs", "250 Bs", "300 Bs", "400 Bs", "500 Bs", "Por negociar"]

# ========== LIMPIAR DATOS EXISTENTES (OPCIONAL) ==========
respuesta = input("\n¿Deseas eliminar todos los datos existentes antes de cargar nuevos? (s/n): ")
if respuesta.lower() == 's':
    print("\nEliminando datos existentes...")
    Calificacion.objects.all().delete()
    Like.objects.all().delete()
    Comentario.objects.all().delete()
    Publicacion.objects.all().delete()
    Oferta.objects.all().delete()
    Servicio.objects.all().delete()
    Perfil.objects.filter(usuario__is_superuser=False).delete()
    User.objects.filter(is_superuser=False).delete()
    print("✓ Datos eliminados")

# ========== 1. CREAR ADMIN ==========
print("\n1. Creando administrador...")
admin, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@chamba.com',
        'first_name': 'Administrador',
        'last_name': 'CHAMBA',
        'is_staff': True,
        'is_superuser': True
    }
)
if created:
    admin.set_password('admin123')
    admin.save()
    print("   ✓ Admin creado: admin / admin123")
else:
    print("   ✓ Admin ya existe")

Perfil.objects.get_or_create(
    usuario=admin,
    defaults={
        'tipo': 'empleador',
        'telefono': '77777777',
        'ubicacion': 'La Paz',
        'nombre_empresa': 'CHAMBA Admin',
        'rubro': 'Tecnología',
    }
)

# ========== 2. CREAR TRABAJADORES ==========
print("\n2. Creando trabajadores...")
trabajadores = []
for nombre, apellido, oficio, desc, exp in TRABAJADORES:
    username = f"{nombre.lower()}.{apellido.lower()}"
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': f"{username}@ejemplo.com",
            'first_name': nombre,
            'last_name': apellido
        }
    )
    if created:
        user.set_password('trabajador123')
        user.save()
    
    perfil, created = Perfil.objects.get_or_create(
        usuario=user,
        defaults={
            'tipo': 'trabajador',
            'telefono': f'6{random.randint(1000000, 9999999)}',
            'ubicacion': random.choice(UBICACIONES),
            'oficios': oficio,
            'descripcion_personal': desc,
            'anios_experiencia': exp,
            'disponible': True,
        }
    )
    if created:
        print(f"   ✓ {nombre} {apellido} - {oficio} ({exp} años)")
    trabajadores.append(user)

# ========== 3. CREAR EMPLEADORES ==========
print("\n3. Creando empleadores...")
empleadores = []
for nombre, apellido, rubro, desc in EMPLEADORES:
    username = f"{nombre.lower()}{apellido.lower()}"
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': f"{username}@empresa.com",
            'first_name': nombre,
            'last_name': apellido
        }
    )
    if created:
        user.set_password('empleador123')
        user.save()
    
    perfil, created = Perfil.objects.get_or_create(
        usuario=user,
        defaults={
            'tipo': 'empleador',
            'telefono': f'7{random.randint(1000000, 9999999)}',
            'ubicacion': random.choice(UBICACIONES),
            'nombre_empresa': f"{nombre} {apellido}",
            'rubro': rubro,
            'descripcion_personal': desc,
        }
    )
    if created:
        print(f"   ✓ {nombre} {apellido} - {rubro}")
    empleadores.append(user)

# ========== 4. CREAR OFERTAS ==========
print("\n4. Creando ofertas laborales...")
ofertas_creadas = 0
titulos_ofertas = [
    "Se necesita electricista urgente",
    "Plomero para reparación de filtraciones",
    "Carpintero para muebles a medida",
    "Cocinero para restaurante nuevo",
    "Pintor para edificio completo",
    "Personal de limpieza para oficinas",
    "Mecánico con experiencia",
    "Jardinero para mantenimiento"
]

for emp in empleadores:
    for i in range(3):
        titulo = random.choice(titulos_ofertas)
        oficio = random.choice(['Electricista', 'Plomero', 'Carpintero', 'Cocinero', 'Pintor', 'Limpieza', 'Mecánico', 'Jardinero'])
        oferta = Oferta.objects.create(
            empleador=emp,
            titulo=titulo,
            oficio=oficio,
            descripcion=f"Buscamos {oficio} para trabajar en {random.choice(UBICACIONES)}. Horario flexible, pago puntual.",
            ubicacion=random.choice(UBICACIONES),
            remuneracion=random.choice(PRECIOS),
            activa=True,
            fecha_limite=timezone.now().date() + timedelta(days=random.randint(7, 30))
        )
        ofertas_creadas += 1
print(f"   ✓ Creadas {ofertas_creadas} ofertas")

# ========== 5. CREAR SERVICIOS ==========
print("\n5. Creando servicios ofrecidos...")
servicios_creados = 0
for trab in trabajadores:
    for i in range(2):
        servicio = Servicio.objects.create(
            trabajador=trab,
            titulo=f"Servicio de {trab.perfil.oficios} a domicilio",
            oficio=trab.perfil.oficios,
            descripcion=trab.perfil.descripcion_personal,
            ubicacion=trab.perfil.ubicacion,
            precio=random.choice(PRECIOS),
            disponible=True
        )
        servicios_creados += 1
print(f"   ✓ Creados {servicios_creados} servicios")

# ========== 6. CREAR PUBLICACIONES ==========
print("\n6. Creando publicaciones...")
todos_usuarios = trabajadores + empleadores
publicaciones_creadas = 0
contenidos = [
    "¡Buen día a todos! Estoy disponible para trabajar hoy.",
    "Nuevo proyecto completado con éxito!",
    "Gracias a CHAMBA por conectar profesionales.",
    "¿Alguien necesita mis servicios? Estoy disponible.",
    "Feliz de ayudar a más clientes cada día.",
    "Comparto mi portafolio de trabajos recientes.",
    "Disponible para trabajos urgentes este fin de semana.",
    "Recomendado por mis últimos clientes."
]

for user in todos_usuarios:
    for i in range(random.randint(1, 3)):
        pub = Publicacion.objects.create(
            usuario=user,
            contenido=random.choice(contenidos),
            tipo='estado',
            fecha_creacion=timezone.now() - timedelta(days=random.randint(0, 15))
        )
        publicaciones_creadas += 1
print(f"   ✓ Creadas {publicaciones_creadas} publicaciones")

# ========== 7. CREAR CALIFICACIONES ==========
print("\n7. Creando calificaciones...")
calif_creadas = 0
comentarios_calif = [
    "Excelente profesional, lo recomiendo.",
    "Muy buen trabajo, cumplió con todo lo acordado.",
    "Profesional muy capacitado, volvería a contratarlo.",
    "Puntual y responsable, excelente servicio.",
    "Trabajo de calidad, muy satisfecho.",
    "Buen trato y excelente resultado."
]

for _ in range(30):
    calificador = random.choice(todos_usuarios)
    calificado = random.choice([u for u in todos_usuarios if u != calificador])
    if calificador and calificado:
        calif = Calificacion.objects.create(
            calificador=calificador,
            calificado=calificado,
            puntuacion=random.randint(4, 5),
            comentario=random.choice(comentarios_calif)
        )
        calif_creadas += 1
print(f"   ✓ Creadas {calif_creadas} calificaciones")

# ========== 8. ACTUALIZAR PROMEDIOS ==========
print("\n8. Actualizando promedios de calificaciones...")
for user in todos_usuarios:
    calificaciones = Calificacion.objects.filter(calificado=user)
    if calificaciones.exists():
        total = calificaciones.count()
        promedio = calificaciones.aggregate(models.Avg('puntuacion'))['puntuacion__avg'] or 0
        user.perfil.promedio_calificacion = promedio
        user.perfil.total_calificaciones = total
        user.perfil.save()
print("   ✓ Promedios actualizados")

# ========== ESTADÍSTICAS FINALES ==========
print("\n" + "=" * 60)
print("   ESTADÍSTICAS FINALES")
print("=" * 60)
print(f"📊 Usuarios totales: {User.objects.count()}")
print(f"👷 Trabajadores: {Perfil.objects.filter(tipo='trabajador').count()}")
print(f"🏢 Empleadores: {Perfil.objects.filter(tipo='empleador').count()}")
print(f"💼 Ofertas: {Oferta.objects.count()}")
print(f"🔧 Servicios: {Servicio.objects.count()}")
print(f"📝 Publicaciones: {Publicacion.objects.count()}")
print(f"⭐ Calificaciones: {Calificacion.objects.count()}")

print("\n" + "=" * 60)
print("   ✅ BASE DE DATOS CARGADA CON ÉXITO")
print("=" * 60)
print("\n🔑 CREDENCIALES DE ACCESO:")
print("   Administrador: admin / admin123")
print("   Trabajadores: nombre.apellido / trabajador123")
print("   Empleadores: nombreapellido / empleador123")
print("\n📝 Ejemplos:")
print("   - carlos.gutierrez / trabajador123")
print("   - construccionesandes / empleador123")