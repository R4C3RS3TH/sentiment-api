#!/usr/bin/env bash
#
# run.sh - Script de automatización del proyecto Sentiment API
#
# Automatiza:
#   1. Clonación del repositorio (comando 'clone')
#   2. Instalación de dependencias + entrenamiento del modelo (comando 'setup')
#   3. Ejecución de las pruebas unitarias (comando 'test')
#   4. Ejecución del proyecto en modo local (comando 'run')
#   5. Flujo completo: clonar + setup + test + run (comando 'all')
#
# Uso:
#   ./run.sh clone   [<url_del_repo>]
#   ./run.sh setup
#   ./run.sh test
#   ./run.sh run
#   ./run.sh all     [<url_del_repo>]
#
set -euo pipefail

REPO_URL_DEFAULT="https://github.com/R4C3RS3TH/sentiment-api.git"
PROJECT_DIR="sentiment-api"
VENV_DIR=".venv"

# ---------------------------------------------------------------------------
# Utilidades de salida
# ---------------------------------------------------------------------------
info()    { echo -e "\033[1;34m[INFO]\033[0m $1"; }
success() { echo -e "\033[1;32m[OK]\033[0m $1"; }
error()   { echo -e "\033[1;31m[ERROR]\033[0m $1" >&2; }

# ---------------------------------------------------------------------------
# Utilidades de entorno virtual (compatible Linux/macOS y Windows/Git Bash)
# ---------------------------------------------------------------------------
detectar_python() {
    if command -v python3 >/dev/null 2>&1 && python3 -c "" >/dev/null 2>&1; then
        echo "python3"
    elif command -v python >/dev/null 2>&1; then
        echo "python"
    else
        error "No se encontró Python en el PATH."
        exit 1
    fi
}

# En Windows el venv usa Scripts/activate; en Linux/macOS usa bin/activate.
activar_venv() {
    if [ -f "$VENV_DIR/bin/activate" ]; then
        # shellcheck disable=SC1091
        source "$VENV_DIR/bin/activate"
    elif [ -f "$VENV_DIR/Scripts/activate" ]; then
        # shellcheck disable=SC1091
        source "$VENV_DIR/Scripts/activate"
    else
        error "No se encontró el script de activación en '$VENV_DIR'."
        error "Elimina el directorio y vuelve a ejecutar: rm -rf $VENV_DIR && ./run.sh setup"
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# 1. Clonar el repositorio
# ---------------------------------------------------------------------------
clonar_repositorio() {
    local repo_url="${1:-$REPO_URL_DEFAULT}"

    if [ -d "$PROJECT_DIR" ]; then
        info "El directorio '$PROJECT_DIR' ya existe, se omite la clonación."
        return 0
    fi

    info "Clonando repositorio desde $repo_url ..."
    if git clone "$repo_url" "$PROJECT_DIR"; then
        success "Repositorio clonado en ./$PROJECT_DIR"
    else
        error "No se pudo clonar el repositorio."
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# 2. Instalar dependencias y entrenar el modelo
# ---------------------------------------------------------------------------
configurar_entorno() {
    info "Creando entorno virtual en $VENV_DIR ..."
    if [ ! -d "$VENV_DIR" ]; then
        "$(detectar_python)" -m venv "$VENV_DIR"
    fi

    activar_venv

    info "Instalando dependencias (requirements-dev.txt) ..."
    python -m pip install --quiet --upgrade pip
    python -m pip install --quiet -r requirements-dev.txt
    success "Dependencias instaladas."

    if [ ! -f "models/sentiment_model.pkl" ]; then
        info "Entrenando el modelo de clasificación ..."
        python train/train_model.py
        success "Modelo entrenado y guardado en models/sentiment_model.pkl"
    else
        info "El modelo ya existe, se omite el entrenamiento."
    fi
}

# ---------------------------------------------------------------------------
# 3. Ejecutar pruebas unitarias
# ---------------------------------------------------------------------------
ejecutar_tests() {
    activar_venv

    info "Ejecutando pruebas unitarias con pytest ..."
    if python -m pytest -v; then
        success "Todas las pruebas pasaron correctamente."
    else
        error "Algunas pruebas fallaron."
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# 4. Ejecutar el proyecto en modo local
# ---------------------------------------------------------------------------
ejecutar_local() {
    activar_venv

    if [ ! -f "models/sentiment_model.pkl" ]; then
        info "Modelo no encontrado, entrenando antes de iniciar ..."
        python train/train_model.py
    fi

    info "Iniciando la API Flask en modo local (http://localhost:5000) ..."
    export FLASK_APP=app.main
    python -m flask run --host=0.0.0.0 --port=5000
}

# ---------------------------------------------------------------------------
# Menú principal
# ---------------------------------------------------------------------------
mostrar_uso() {
    cat <<EOF
Uso: ./run.sh <comando> [argumentos]

Comandos disponibles:
  clone [url]   Clona el repositorio (usa la URL dada o la de origin por defecto)
  setup         Crea el entorno virtual, instala dependencias y entrena el modelo
  test          Ejecuta las pruebas unitarias con pytest
  run           Levanta la API Flask en modo local
  all [url]     Ejecuta clone + setup + test + run en secuencia
EOF
}

main() {
    local comando="${1:-}"

    case "$comando" in
        clone)
            clonar_repositorio "${2:-}"
            ;;
        setup)
            configurar_entorno
            ;;
        test)
            configurar_entorno
            ejecutar_tests
            ;;
        run)
            configurar_entorno
            ejecutar_local
            ;;
        all)
            clonar_repositorio "${2:-}"
            cd "$PROJECT_DIR"
            configurar_entorno
            ejecutar_tests
            ejecutar_local
            ;;
        *)
            mostrar_uso
            exit 1
            ;;
    esac
}

main "$@"
