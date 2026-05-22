#!/usr/bin/env python
import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bytegirls.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from oficios.models import Perfil, Oferta, Servicio, PortafolioFoto, Calificacion

print("=" * 60)
print("   CARGANDO DATOS PARA PROBAR FILTROS DEL MAPA")
print("=" * 60)

# ========== LIMPIAR DATOS EXISTENTES ==========
respuesta = input("\n¿Eliminar datos existentes y cargar nuevos? (s/n): ")
if respuesta.lower() == 's':
    print("\nEliminando datos existentes...")
    Calificacion.objects.all().delete()
    PortafolioFoto.objects.all().delete()
    Servicio.objects.all().delete()
    Oferta.objects.all().delete()
    Perfil.objects.filter(usuario__is_superuser=False).delete()
    User.objects.filter(is_superuser=False).delete()
    print("✓ Datos eliminados")

# ========== CREAR ADMIN ==========
print("\n1. Creando administrador...")
admin, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@chamba.com',
        'first_name': 'Administrador',
        'last_name': 'CHAMBA',
        'is_staff': True,
        'is_superuser': True,
        'password': make_password('admin123')
    }
)
print("   ✓ Admin: admin / admin123")

# ========== TRABAJADORES CON DIFERENTES CIUDADES Y EXPERIENCIAS ==========
print("\n2. Creando trabajadores...")

trabajadores_data = [
    # La Paz
    ("Carlos", "Gutierrez", "Electricista", "Electricista especializado en instalaciones residenciales", 8, "La Paz, Zona Sur", "78945612", 4.8, 12),
    ("Maria", "Fernandez", "Plomera", "Plomera con amplia experiencia en reparaciones", 5, "La Paz, Centro", "78945613", 4.5, 8),
    ("Jose", "Mamani", "Carpintero", "Carpintero artesanal, muebles a medida", 10, "El Alto, Villa Bolivar", "78945614", 4.9, 15),
    ("Ana", "Quispe", "Cocinera", "Chef profesional, especialidad comida boliviana", 6, "La Paz, Sopocachi", "78945615", 4.7, 6),
    
    # Santa Cruz
    ("Pedro", "Vargas", "Pintor", "Pintor de interiores y exteriores", 4, "Santa Cruz, Equipetrol", "78945616", 4.2, 5),
    ("Lucia", "Torrez", "Limpieza", "Limpieza general para hogares y oficinas", 3, "Santa Cruz, La Ramada", "78945617", 4.3, 4),
    ("Roberto", "Flores", "Mecánico", "Mecánico automotriz con taller propio", 12, "Santa Cruz, Centro", "78945618", 4.9, 20),
    ("Sofia", "Rios", "Jardinera", "Diseño y mantenimiento de jardines", 7, "Santa Cruz, Urbarí", "78945619", 4.6, 10),
    
    # Cochabamba
    ("Miguel", "Paredes", "Albañil", "Construcción y remodelaciones en general", 15, "Cochabamba, Queru Queru", "78945620", 4.8, 25),
    ("Elena", "Cruz", "Costurera", "Confección y reparación de ropa a medida", 9, "Cochabamba, Cala Cala", "78945621", 4.7, 12),
    ("Pablo", "Rojas", "Electricista", "Electricista industrial y residencial", 6, "Cochabamba, Plaza Principal", "78945622", 4.4, 7),
    ("Daniela", "Flores", "Plomera", "Plomera especialista en instalaciones", 4, "Cochabamba, Tiquipaya", "78945623", 4.2, 3),
    
    # Sucre
    ("Fernando", "Arias", "Pintor", "Pintor de obras grandes y pequeñas", 8, "Sucre, Centro", "78945624", 4.5, 6),
    ("Carmen", "Lopez", "Cocinera", "Comida típica boliviana a domicilio", 5, "Sucre, Calvo", "78945625", 4.6, 4),
    
    # Tarija
    ("Ricardo", "Mendez", "Jardinero", "Mantenimiento de jardines residenciales", 6, "Tarija, La Victoria", "78945626", 4.3, 5),
    ("Andrea", "Soliz", "Limpieza", "Limpieza profunda de oficinas", 3, "Tarija, Centro", "78945627", 4.1, 2),
    
    # Potosí
    ("Julio", "Campos", "Albañil", "Construcción de viviendas", 11, "Potosi, Centro", "78945628", 4.7, 8),
    ("Roxana", "Villca", "Costurera", "Confección de ropa tradicional", 8, "Potosi, Villa Imperial", "78945629", 4.8, 6),
    
    # Oruro
    ("Oscar", "Mamani", "Mecánico", "Reparación de motores diésel", 9, "Oruro, Centro", "78945630", 4.5, 7),
    ("Liliana", "Choque", "Electricista", "Electricista domiciliaria", 5, "Oruro, Villa Santos", "78945631", 4.4, 4),
]

trabajadores = []
for nombre, apellido, oficio, desc, exp, ubic, telefono, rating, calif_total in trabajadores_data:
    username = f"{nombre.lower()}.{apellido.lower()}"
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': f"{username}@trabajador.com",
            'first_name': nombre,
            'last_name': apellido,
            'password': make_password('trabajador123')
        }
    )
    
    perfil, created = Perfil.objects.get_or_create(
        usuario=user,
        defaults={
            'tipo': 'trabajador',
            'telefono': telefono,
            'ubicacion': ubic,
            'oficios': oficio,
            'descripcion_personal': desc,
            'anios_experiencia': exp,
            'disponible': random.choice([True, True, True, True, False]),
            'promedio_calificacion': rating,
            'total_calificaciones': calif_total,
        }
    )
    if created:
        print(f"   ✓ {nombre} {apellido} - {oficio} ({exp} años) - {ubic.split(',')[0]}")
    trabajadores.append(user)

# ========== EMPLEADORES ==========
print("\n3. Creando empleadores...")

empleadores_data = [
    ("Construcciones", "Andes", "Constructora", "Empresa líder en construcción de viviendas", "La Paz, Zona Sur", "78945601", 4.9, 15),
    ("Servicios", "Integrales", "Servicios Generales", "Mantenimiento y limpieza industrial", "Santa Cruz, Equipetrol", "78945602", 4.7, 12),
    ("Tecno", "Fix", "Tecnología", "Reparación de equipos electrónicos", "Cochabamba, Queru Queru", "78945603", 4.5, 8),
    ("Hogar", "Seguro", "Hogar", "Servicios para el hogar y jardinería", "El Alto, Villa Bolivar", "78945604", 4.6, 10),
    ("Auto", "Center", "Automotriz", "Taller mecánico y eléctrico automotriz", "Santa Cruz, La Ramada", "78945605", 4.8, 14),
    ("Electro", "Hogar", "Electrodomésticos", "Venta y reparación de electrodomésticos", "La Paz, Centro", "78945606", 4.4, 6),
    ("Mega", "Construcción", "Construcción", "Materiales y construcción", "Cochabamba, Cala Cala", "78945607", 4.7, 9),
]

empleadores = []
for nombre, apellido, rubro, desc, ubic, telefono, rating, calif_total in empleadores_data:
    username = f"{nombre.lower()}{apellido.lower()}"
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': f"{username}@empresa.com",
            'first_name': nombre,
            'last_name': apellido,
            'password': make_password('empleador123')
        }
    )
    
    perfil, created = Perfil.objects.get_or_create(
        usuario=user,
        defaults={
            'tipo': 'empleador',
            'telefono': telefono,
            'ubicacion': ubic,
            'nombre_empresa': f"{nombre} {apellido}",
            'rubro': rubro,
            'descripcion_personal': desc,
            'promedio_calificacion': rating,
            'total_calificaciones': calif_total,
        }
    )
    if created:
        print(f"   ✓ {nombre} {apellido} - {rubro} - {ubic.split(',')[0]}")
    empleadores.append(user)

# ========== CREAR SERVICIOS PARA CADA TRABAJADOR ==========
print("\n4. Creando servicios ofrecidos...")
servicios_creados = 0
precios = ["150 Bs", "200 Bs", "250 Bs", "300 Bs", "350 Bs", "400 Bs", "500 Bs", "Por negociar"]
oficios_lista = ["Electricista", "Plomero", "Carpintero", "Cocinero", "Pintor", "Limpieza", "Mecánico", "Jardinero", "Albañil", "Costurera"]

for trabajador in trabajadores:
    oficio_trabajador = trabajador.perfil.oficios
    # 2-3 servicios por trabajador
    for i in range(random.randint(2, 3)):
        titulo = f"Servicio de {oficio_trabajador} a domicilio - {random.choice(['Profesional', 'Económico', 'Express', 'Premium'])}"
        Servicio.objects.create(
            trabajador=trabajador,
            titulo=titulo,
            oficio=oficio_trabajador,
            descripcion=f"Ofrezco servicios de {oficio_trabajador} con {trabajador.perfil.anios_experiencia} años de experiencia. Calidad garantizada y precios competitivos. Atención personalizada.",
            ubicacion=trabajador.perfil.ubicacion,
            precio=random.choice(precios),
            disponible=trabajador.perfil.disponible
        )
        servicios_creados += 1
print(f"   ✓ Creados {servicios_creados} servicios")

# ========== CREAR OFERTAS PARA EMPLEADORES ==========
print("\n5. Creando ofertas laborales...")
ofertas_creadas = 0
titulos_ofertas = [
    "Se necesita {oficio} para proyecto urgente",
    "Buscamos {oficio} con experiencia",
    "Contratación inmediata de {oficio}",
    "Se solicita {oficio} para trabajo fijo",
    "Proyecto requiere {oficio} calificado"
]

for empleador in empleadores:
    for i in range(random.randint(2, 3)):
        oficio = random.choice(oficios_lista)
        titulo = random.choice(titulos_ofertas).format(oficio=oficio)
        Oferta.objects.create(
            empleador=empleador,
            titulo=titulo,
            oficio=oficio,
            descripcion=f"Importante empresa busca {oficio} para trabajar en {empleador.perfil.ubicacion}. Horario flexible, pago puntual. Beneficios de ley.",
            ubicacion=empleador.perfil.ubicacion,
            remuneracion=random.choice(["1500 Bs", "2000 Bs", "2500 Bs", "3000 Bs", "A convenir"]),
            fecha_limite=datetime.now().date() + timedelta(days=random.randint(7, 30)),
            activa=True
        )
        ofertas_creadas += 1
print(f"   ✓ Creadas {ofertas_creadas} ofertas")

# ========== CALIFICACIONES ENTRE USUARIOS ==========
print("\n6. Creando calificaciones...")
todos_usuarios = trabajadores + empleadores
calificaciones_creadas = 0
comentarios_calif = [
    "Excelente profesional, muy recomendado",
    "Cumplió con todo lo acordado, muy satisfecho",
    "Trabajo de calidad, volvería a contratarlo",
    "Muy responsable y puntual, excelente servicio",
    "Buen trato y excelente resultado final",
    "Profesional muy capacitado, superó expectativas",
    "Comunicación excelente, trabajo impecable",
    "Lo recomiendo ampliamente, muy buen servicio"
]

for _ in range(60):
    calificador = random.choice(todos_usuarios)
    calificado = random.choice([u for u in todos_usuarios if u != calificador])
    puntuacion = random.randint(3, 5)
    
    Calificacion.objects.create(
        calificador=calificador,
        calificado=calificado,
        puntuacion=puntuacion,
        comentario=random.choice(comentarios_calif)
    )
    calificaciones_creadas += 1
print(f"   ✓ Creadas {calificaciones_creadas} calificaciones")

# ========== ACTUALIZAR PROMEDIOS ==========
print("\n7. Actualizando promedios de calificaciones...")
from django.db.models import Avg

for user in todos_usuarios:
    calificaciones = Calificacion.objects.filter(calificado=user)
    if calificaciones.exists():
        promedio = calificaciones.aggregate(Avg('puntuacion'))['puntuacion__avg']
        user.perfil.promedio_calificacion = promedio
        user.perfil.total_calificaciones = calificaciones.count()
        user.perfil.save()
print("   ✓ Promedios actualizados")

# ========== ESTADÍSTICAS FINALES ==========
print("\n" + "=" * 60)
print("   ESTADÍSTICAS FINALES")
print("=" * 60)
print(f"📊 Usuarios totales: {User.objects.count()}")
print(f"👷 Trabajadores: {Perfil.objects.filter(tipo='trabajador').count()}")
print(f"🏢 Empleadores: {Perfil.objects.filter(tipo='empleador').count()}")
print(f"🔧 Servicios: {Servicio.objects.count()}")
print(f"💼 Ofertas: {Oferta.objects.count()}")
print(f"⭐ Calificaciones: {Calificacion.objects.count()}")

print("\n" + "=" * 60)
print("   📍 DISTRIBUCIÓN POR CIUDAD")
print("=" * 60)

ciudades = ["La Paz", "El Alto", "Santa Cruz", "Cochabamba", "Sucre", "Tarija", "Potosi", "Oruro"]
for ciudad in ciudades:
    trabajadores_ciudad = Perfil.objects.filter(tipo='trabajador', ubicacion__icontains=ciudad).count()
    empleadores_ciudad = Perfil.objects.filter(tipo='empleador', ubicacion__icontains=ciudad).count()
    print(f"   {ciudad}: {trabajadores_ciudad} trabajadores, {empleadores_ciudad} empleadores")

print("\n" + "=" * 60)
print("   ✅ BASE DE DATOS CARGADA CON ÉXITO")
print("=" * 60)
print("\n🔑 CREDENCIALES:")
print("   Admin: admin / admin123")
print("   Trabajadores: nombre.apellido / trabajador123")
print("   Empleadores: nombreapellido / empleador123")
print("\n📝 EJEMPLOS:")
print("   - carlos.gutierrez / trabajador123")
print("   - construccionesandes / empleador123")