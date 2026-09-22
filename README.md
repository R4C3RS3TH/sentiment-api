# Sentiment API

API REST en Flask que clasifica el sentimiento (`positive` / `negative`) de un
texto corto en español, usando un modelo de Machine Learning entrenado con
scikit-learn (TF-IDF + Regresión Logística). Cada predicción se registra en
una base de datos PostgreSQL como bitácora básica de monitoreo del modelo.

Proyecto desarrollado para el curso de **DevOps** — Informe Parcial 1
(Control de versiones, pruebas unitarias y dockerización).

## Tabla de contenidos

- [Descripción del proyecto](#descripción-del-proyecto)
- [Arquitectura](#arquitectura)
- [Prerrequisitos](#prerrequisitos)
- [Instalación y ejecución local](#instalación-y-ejecución-local)
- [Ejecutar las pruebas unitarias](#ejecutar-las-pruebas-unitarias)
- [Ejecutar con Docker](#ejecutar-con-docker)
- [Script de automatización](#script-de-automatización)
- [Endpoints de la API](#endpoints-de-la-api)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Flujo de trabajo con Git (GitFlow + Conventional Commits)](#flujo-de-trabajo-con-git-gitflow--conventional-commits)

## Descripción del proyecto

- **Problema:** clasificar manualmente el sentimiento de comentarios o
  reseñas de usuarios es lento y no escala.
- **Solución:** una API ligera que recibe un texto y devuelve si su
  sentimiento es positivo o negativo, junto con el nivel de confianza del
  modelo, lista para integrarse a cualquier sistema (formularios de
  contacto, reseñas de producto, redes sociales, etc.).

## Arquitectura

```
Cliente HTTP → Flask (Gunicorn) → Modelo scikit-learn (TF-IDF + LogisticRegression)
                                 → PostgreSQL (registro de cada predicción)
```

## Prerrequisitos

Para correr el proyecto **en modo local** (sin Docker):

- Python 3.11 o superior
- pip
- Git

Para correr el proyecto **con Docker** (recomendado):

- Docker Engine 24+
- Docker Compose v2 (`docker compose`)

## Instalación y ejecución local

```bash
# 1. Clonar el repositorio
git clone https://github.com/<tu-usuario>/sentiment-api.git
cd sentiment-api

# 2. Crear entorno virtual e instalar dependencias
python3 -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

# 3. Entrenar el modelo (genera models/sentiment_model.pkl)
python train/train_model.py

# 4. Levantar la API en modo local
export FLASK_APP=app.main        # En Windows (PowerShell): $env:FLASK_APP="app.main"
python -m flask run --host=0.0.0.0 --port=5000
```

La API quedará disponible en `http://localhost:5000`.

> Nota: si no se levanta PostgreSQL localmente, la API sigue funcionando con
> normalidad — el registro de predicciones simplemente se omite (ver
> `app/db.py`).

## Ejecutar las pruebas unitarias

Con el entorno virtual activado y las dependencias de `requirements-dev.txt`
instaladas, el comando exacto para correr las pruebas es:

```bash
pytest
```

Esto ejecuta las 22 pruebas unitarias ubicadas en el directorio [`tests/`](tests/)
(preprocesamiento de texto, predicciones del modelo y endpoints de la API).

Salida esperada:

```
tests/test_api.py::test_health_endpoint_returns_200 PASSED
...
============================== 22 passed in 0.05s ==============================
```

## Ejecutar con Docker

```bash
# Construir las imágenes y levantar los contenedores (web + PostgreSQL)
docker compose up -d --build

# Ver logs del servicio web
docker compose logs -f web

# Probar el healthcheck
curl http://localhost:5000/health

# Detener y eliminar los contenedores
docker compose down
```

El servicio `web` corre la API con **Gunicorn** en el puerto `5000`, y el
servicio `db` levanta **PostgreSQL 16**. El modelo se entrena automáticamente
durante el build de la imagen.

## Script de automatización

El archivo [`run.sh`](run.sh) en la raíz del proyecto automatiza clonación,
instalación de dependencias, ejecución de pruebas y arranque local:

```bash
chmod +x run.sh

./run.sh clone <url-del-repo>   # Clona el repositorio
./run.sh setup                  # Crea el venv, instala dependencias y entrena el modelo
./run.sh test                   # Ejecuta las pruebas unitarias (pytest)
./run.sh run                    # Levanta la API en modo local
./run.sh all <url-del-repo>     # Ejecuta todo el flujo anterior en secuencia
```

## Endpoints de la API

### `GET /health`

Verifica el estado de la API y si el modelo está cargado.

```bash
curl http://localhost:5000/health
```

```json
{ "status": "ok", "model_loaded": true }
```

### `POST /classify`

Clasifica el sentimiento de un texto.

```bash
curl -X POST http://localhost:5000/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "excelente producto, lo recomiendo totalmente"}'
```

```json
{
  "text": "excelente producto, lo recomiendo totalmente",
  "label": "positive",
  "confidence": 0.87,
  "probabilities": { "negative": 0.13, "positive": 0.87 }
}
```

## Estructura del proyecto

```
sentiment-api/
├── app/                  # Código fuente de la API Flask
│   ├── main.py           # Application factory + endpoints
│   ├── model.py          # Carga del modelo y lógica de predicción
│   ├── preprocessing.py  # Validación y limpieza de texto de entrada
│   └── db.py             # Registro de predicciones en PostgreSQL
├── train/
│   └── train_model.py    # Script de entrenamiento del modelo
├── data/
│   └── reviews.csv       # Dataset de entrenamiento
├── tests/                # Pruebas unitarias (pytest)
├── models/                # Modelo entrenado (.pkl, generado, no versionado)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
├── run.sh                # Script de automatización
└── README.md
```

## Flujo de trabajo con Git (GitFlow + Conventional Commits)

Este proyecto usa **GitFlow** como metodología de ramificación:

- `main`: rama protegida, solo recibe merges vía Pull Request.
- `develop`: rama de integración de nuevas funcionalidades.
- `feature/*`: ramas de corta duración para cada funcionalidad, creadas
  desde `develop`.

Los mensajes de commit siguen el estándar **Conventional Commits**:

```
<tipo>[alcance opcional]: <descripción>
```

Tipos usados en este proyecto: `feat`, `fix`, `docs`, `test`, `chore`, `ci`,
`refactor`.
