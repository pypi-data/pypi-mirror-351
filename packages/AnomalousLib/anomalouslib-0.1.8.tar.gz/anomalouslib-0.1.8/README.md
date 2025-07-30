
Para hacer pruebas en local (des de la raiz del repositorio):
python -m build
pots fer: pip install .\dist\anomalouslib-0.1.0-py3-none-any.whl --force-reinstall
però millor: pip install --upgrade .\dist\anomalouslib-0.1.0-py3-none-any.whl
Para hacer update de los requirements: pip freeze > requirements.txt

No instalar una versión que no sea local a este repositorio (no?)

Para subirlo: twine upload dist/*
[Link](https://pypi.org/project/AnomalousLib/)

Activate:
en powershell: .\venv\Scripts\Activate.ps1

deactivate:
en powershell : deactivate


<!-- EXPLICAR ESTO -->
<!-- - Entrar al environment "env"

```
project_root/
│
├── data/                   # Todos los datos relacionados
│   ├── raw/                # Datos originales/inmutables (descargados)
│   ├── generated/          # Datos sintéticos generados
│   ├── processed/          # Datos transformados/listos para modelar
│   └── external/           # Datos de terceros/externos
│
├── models/                 # Modelos guardados
│   ├── trained_models/     # Modelos entrenados (pickles u otros formatos)
│   └── model_configs/      # Configuraciones/parámetros de modelos
│
├── results/                # Resultados de análisis y predicciones
│   ├── reports/            # Reportes estadísticos/analíticos
│   ├── predictions/        # Resultados de predicciones
│   └── visualizations/     # Gráficos y visualizaciones
│
├── src/                    # Código fuente del proyecto
│   ├── data/               # Módulo para manejo de datos
│   │   ├── __init__.py
│   │   ├── datasets.py     # Clases Dataset, GeneratedDataset, RealDataset
│   │   └── preprocessing.py# Funciones de preprocesamiento
│   │
│   ├── models/             # Módulo para modelos
│   │   ├── __init__.py
│   │   ├── base_model.py   # Clase base Model
│   │   └── specific_models/# Modelos concretos (ej. random_forest.py)
│   │
│   ├── analysis/           # Módulo de análisis
│   │   ├── __init__.py
│   │   ├── analyzer.py     # Clase DataAnalyzer
│   │   └── metrics.py      # Funciones de evaluación
│   │
│   └── utils/              # Utilidades auxiliares
│       ├── __init__.py
│       ├── logger.py       # Sistema de logging
│       └── helpers.py      # Funciones helper
│
├── notebooks/              # Jupyter notebooks de exploración
│   ├── EDA/                # Análisis exploratorio
│   └── experiments/        # Experimentos con modelos
│
├── tests/                  # Tests unitarios e integración
│   ├── __init__.py
│   ├── test_datasets.py
│   └── test_models.py
│
├── config/                 # Configuraciones del proyecto
│   ├── paths.yaml          # Rutas de archivos/directorios
│   └── settings.yaml       # Parámetros globales
│
├── scripts/                # Scripts ejecutables
│   ├── train_model.py
│   └── generate_data.py
│
├── requirements.txt        # Dependencias
├── README.md               # Documentación del proyecto
├── .gitignore              # Archivos a ignorar en Git
└── .env                    # Variables de entorno (opcional)
```

pip freeze > requirements.txt

<!-- para montar el entorno (activar, hacer estos canvios y desactivar):
Para Linux
export PYTHONPATH="/ruta/a/tu/proyecto_raiz:$PYTHONPATH"

Para Windows (bat):
set PYTHONPATH=C:\ruta\a\tu\proyecto_raiz;%PYTHONPATH%

Para Windows (ps1): -->
