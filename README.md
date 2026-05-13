# CHAMBA - Conecta tu talento 🚀

[![Django Version](https://img.shields.io/badge/Django-6.0.5-green.svg)](https://www.djangoproject.com/)
[![Python Version](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

CHAMBA es una plataforma web que conecta **trabajadores de oficios** con **empleadores** en Bolivia. Encuentra trabajo o contrata al profesional ideal de manera rápida y sencilla.

## 📋 Tabla de Contenidos

- [Características](#características)
- [Capturas de pantalla](#capturas-de-pantalla)
- [Tecnologías utilizadas](#tecnologías-utilizadas)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Credenciales de prueba](#credenciales-de-prueba)
- [Contribución](#contribución)
- [Licencia](#licencia)
- [Contacto](#contacto)

## ✨ Características

### Para Trabajadores
- 👤 Registro de perfil profesional
- 📝 Publicación de servicios ofrecidos
- 📸 Portafolio de trabajos realizados
- ⭐ Sistema de calificaciones y reseñas
- 🔔 Disponibilidad en tiempo real
- 📱 Perfil público para compartir

### Para Empleadores
- 🏢 Registro de empresas
- 💼 Publicación de ofertas laborales
- 🔍 Búsqueda de trabajadores por oficio y ubicación
- 📊 Estadísticas de publicaciones
- ⭐ Calificación de trabajadores contratados

### Generales
- 🗺️ **Mapa interactivo** con geolocalización de profesionales
- 🔐 Sistema de autenticación con "Recordarme"
- 📧 Recuperación de contraseña por email
- 💬 Comentarios y likes en publicaciones
- 🔎 Buscador con filtros avanzados
- 📱 Diseño responsivo para móviles y tablets

## 📸 Capturas de pantalla

| Dashboard | Mapa de profesionales | Perfil de usuario |
|-----------|----------------------|-------------------|
| ![Dashboard](https://via.placeholder.com/300x200?text=Dashboard) | ![Mapa](https://via.placeholder.com/300x200?text=Mapa) | ![Perfil](https://via.placeholder.com/300x200?text=Perfil) |

## 🛠️ Tecnologías utilizadas

- **Backend**: Django 6.0.5 (Python 3.12)
- **Frontend**: HTML5, CSS3, JavaScript
- **Mapas**: Leaflet + OpenStreetMap
- **Base de datos**: SQLite3 (desarrollo)
- **Iconos**: FontAwesome 6
- **Fuentes**: Google Fonts (Inter)

## 🚀 Instalación

### Requisitos previos

- Python 3.12 o superior
- Git
- (Opcional) Entorno virtual de Python

### Pasos de instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/yleonardomt/chamba.git
cd chamba

# 2. Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Migrar base de datos
python manage.py makemigrations
python manage.py migrate

# 5. Crear superusuario
python manage.py createsuperuser

# 6. Ejecutar servidor
python manage.py runserver 127.0.0.1:8080