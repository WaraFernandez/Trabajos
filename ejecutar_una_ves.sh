#!/bin/bash

# ============================================
# SCRIPT DE INSTALACIÓN Y EJECUCIÓN - CHAMBA
# ============================================

echo "🚀 CHAMBA - Iniciando configuración..."

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado. Por favor instálalo primero."
    exit 1
fi

echo "✅ Python3 encontrado: $(python3 --version)"

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
    echo "✅ Entorno virtual creado"
else
    echo "✅ Entorno virtual ya existe"
fi

# Activar entorno virtual
echo "🔄 Activando entorno virtual..."
source venv/bin/activate

# Actualizar pip
echo "🔄 Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
if [ -f "requirements.txt" ]; then
    echo "📦 Instalando dependencias desde requirements.txt..."
    pip install -r requirements.txt
else
    echo "⚠️ requirements.txt no encontrado. Instalando dependencias por defecto..."
    pip install django==6.0.5 Pillow==10.4.0
fi

# Verificar si hay migraciones pendientes
echo "🔄 Verificando migraciones..."
python manage.py makemigrations
python manage.py migrate

# Crear superusuario si no existe
echo "👤 Creando superusuario (opcional)..."
python manage.py createsuperuser --noinput --username admin --email admin@chamba.com 2>/dev/null || echo "ℹ️ El superusuario ya existe o se creará manualmente"

# Recolectar archivos estáticos
echo "📁 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput 2>/dev/null || echo "ℹ️ Configuración de static opcional"

# Ejecutar servidor
echo ""
echo "🎉 CHAMBA está listo para ejecutarse!"
echo "==========================================="
echo "🌐 Iniciando servidor en http://127.0.0.1:8080"
echo "⚠️  Presiona CTRL+C para detener el servidor"
echo "==========================================="
echo ""

python manage.py runserver 127.0.0.1:8080