#!/bin/bash

# Script de instalación rápida para Launcher Admin Panel
# Configura automáticamente el entorno de desarrollo

set -e  # Salir en caso de error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir con colores
print_color() {
    printf "${1}${2}${NC}\n"
}

print_header() {
    echo ""
    print_color $BLUE "=================================================="
    print_color $BLUE "    🎮 LAUNCHER ADMIN PANEL - INSTALACIÓN"
    print_color $BLUE "=================================================="
    echo ""
}

print_step() {
    print_color $YELLOW "➤ $1"
}

print_success() {
    print_color $GREEN "✓ $1"
}

print_error() {
    print_color $RED "✗ $1"
}

# Verificar si Python está instalado
check_python() {
    print_step "Verificando Python..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        print_success "Python $PYTHON_VERSION encontrado"
        
        # Verificar versión mínima
        if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 7) else 1)'; then
            print_success "Versión de Python compatible"
        else
            print_error "Python 3.7 o superior es requerido"
            exit 1
        fi
    else
        print_error "Python 3 no está instalado"
        print_color $YELLOW "Por favor instala Python 3.7+ desde https://python.org"
        exit 1
    fi
}

# Verificar si pip está instalado
check_pip() {
    print_step "Verificando pip..."
    
    if command -v pip3 &> /dev/null; then
        print_success "pip encontrado"
    else
        print_error "pip no está instalado"
        print_step "Intentando instalar pip..."
        
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y python3-pip
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3-pip
        elif command -v brew &> /dev/null; then
            brew install python3
        else
            print_error "No se pudo instalar pip automáticamente"
            exit 1
        fi
    fi
}

# Crear entorno virtual
create_venv() {
    print_step "Creando entorno virtual..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Entorno virtual creado"
    else
        print_success "Entorno virtual ya existe"
    fi
    
    # Activar entorno virtual
    source venv/bin/activate
    print_success "Entorno virtual activado"
}

# Instalar dependencias
install_dependencies() {
    print_step "Instalando dependencias..."
    
    # Actualizar pip
    pip install --upgrade pip
    
    # Instalar dependencias desde requirements.txt
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Dependencias instaladas desde requirements.txt"
    else
        print_error "Archivo requirements.txt no encontrado"
        exit 1
    fi
    
    # Instalar dependencias adicionales para desarrollo
    pip install gunicorn
    print_success "Gunicorn instalado"
}

# Crear directorios necesarios
create_directories() {
    print_step "Creando estructura de directorios..."
    
    directories=(
        "uploads"
        "uploads/files"
        "uploads/updates"
        "static/downloads"
        "logs"
        "backups"
        "temp"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        echo "  ✓ $dir"
    done
    
    print_success "Directorios creados"
}

# Configurar archivo .env
setup_env() {
    print_step "Configurando archivo de entorno..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            
            # Generar SECRET_KEY aleatoria
            SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
            
            # Reemplazar en .env (compatible con macOS y Linux)
            if [[ "$OSTYPE" == "darwin"* ]]; then
                sed -i '' "s/SECRET_KEY=change-this-secret-key-in-production/SECRET_KEY=$SECRET_KEY/" .env
            else
                sed -i "s/SECRET_KEY=change-this-secret-key-in-production/SECRET_KEY=$SECRET_KEY/" .env
            fi
            
            print_success "Archivo .env creado con SECRET_KEY generada"
        else
            print_error "Archivo .env.example no encontrado"
            exit 1
        fi
    else
        print_success "Archivo .env ya existe"
    fi
}

# Inicializar base de datos
init_database() {
    print_step "Inicializando base de datos..."
    
    if [ -f "install.py" ]; then
        python install.py
        print_success "Base de datos inicializada"
    else
        print_error "Script install.py no encontrado"
        exit 1
    fi
}

# Crear banner por defecto
create_banner() {
    print_step "Creando banner por defecto..."
    
    if [ ! -f "static/downloads/banner.html" ]; then
        cat > static/downloads/banner.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Game Launcher</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }
        .banner-content {
            text-align: center;
            padding: 20px;
        }
        .logo {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
        .title {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
        .subtitle {
            font-size: 1.2rem;
            opacity: 0.8;
            margin-bottom: 2rem;
        }
        .news-item {
            background: rgba(255, 255, 255, 0.1);
            margin: 10px 0;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #ffd700;
        }
    </style>
</head>
<body>
    <div class="banner-content">
        <div class="logo">🎮</div>
        <div class="title">Mi Juego</div>
        <div class="subtitle">¡Bienvenido al launcher!</div>
        
        <div style="margin-top: 2rem;">
            <div class="news-item">
                <strong>🔥 ¡Sistema configurado!</strong><br>
                El panel de administración está funcionando correctamente.
            </div>
            <div class="news-item">
                <strong>📝 Personaliza este banner</strong><br>
                Edita static/downloads/banner.html para personalizar esta vista.
            </div>
            <div class="news-item">
                <strong>🚀 ¡Comienza a gestionar!</strong><br>
                Accede al panel admin para subir archivos y gestionar versiones.
            </div>
        </div>
    </div>
</body>
</html>
EOF
        print_success "Banner por defecto creado"
    else
        print_success "Banner ya existe"
    fi
}

# Verificar instalación
verify_installation() {
    print_step "Verificando instalación..."
    
    # Verificar que se pueden importar los módulos principales
    python3 -c "
import sys
sys.path.insert(0, '.')

try:
    from app import app
    from models import User
    print('✓ Módulos principales importados correctamente')
except ImportError as e:
    print(f'✗ Error importando módulos: {e}')
    sys.exit(1)
"
    
    print_success "Instalación verificada correctamente"
}

# Mostrar información de finalización
show_completion_info() {
    echo ""
    print_color $GREEN "=================================================="
    print_color $GREEN "    ✅ INSTALACIÓN COMPLETADA EXITOSAMENTE"
    print_color $GREEN "=================================================="
    echo ""
    
    print_color $BLUE "Para iniciar el servidor:"
    echo "  1. Activa el entorno virtual: source venv/bin/activate"
    echo "  2. Ejecuta la aplicación: python run.py"
    echo ""
    
    print_color $BLUE "URLs importantes:"
    echo "  • Panel Admin: http://localhost:5000"
    echo "  • API: http://localhost:5000/api"
    echo "  • Banner: http://localhost:5000/Launcher/banner.html"
    echo ""
    
    print_color $BLUE "Credenciales por defecto:"
    echo "  • Usuario: admin"
    echo "  • Contraseña: admin123"
    echo ""
    
    print_color $YELLOW "¡No olvides cambiar las credenciales por defecto!"
    echo ""
}

# Función principal
main() {
    print_header
    
    # Verificar dependencias del sistema
    check_python
    check_pip
    
    # Configurar entorno Python
    create_venv
    install_dependencies
    
    # Configurar aplicación
    create_directories
    setup_env
    create_banner
    init_database
    
    # Verificar instalación
    verify_installation
    
    # Mostrar información final
    show_completion_info
}

# Verificar si el script se ejecuta directamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi