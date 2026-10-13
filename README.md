# Viz2026

Proyecto de análisis y visualización de datos basado en archivos Excel, cargados a una base de datos SQL y procesados con Python. El objetivo del sistema es transformar información operativa en reportes interactivos listos para consulta y análisis empresarial.

El proyecto está orientado a la lectura de datos de ventas y pagos desde archivos `.xlsx`, su preparación y limpieza en Python, y la generación de gráficas HTML a partir de consultas directamente ejecutadas sobre la base de datos.

## Descripción general

El flujo del sistema es el siguiente:

1. Se leen los archivos Excel ubicados en `data/`.
2. Los datos se limpian, normalizan y transforman con funciones definidas en `dataTransform.py`.
3. La información se carga en una base de datos SQL llamada `Viz2026` usando `SQLAlchemy`.
4. Se ejecutan consultas específicas para recuperar los datos necesarios.
5. Se generan reportes HTML interactivos con Plotly y se almacenan en la carpeta `output/`.

La arquitectura es útil para entornos empresariales donde los datos de operación no deben depender de los archivos originales y donde la visualización debe ser reproducible, consistente y actualizable.

## Objetivo del proyecto

El proyecto tiene como finalidad convertir datos brutos almacenados en Excel en información analítica preparada para la toma de decisiones. En particular, trabaja con datos de ventas y pagos de un punto de venta, permitiendo:

- normalizar nombres de columnas,
- convertir fechas y montos,
- eliminar duplicados,
- cargar datos a una base de datos relacional,
- generar dashboards interactivos analizando tendencias y comportamiento por período.

## Outputs generados

El proyecto genera tres archivos HTML en la carpeta `output/`:

- `output/ordenes.html`
- `output/pagos.html`
- una tercera salida visual complementaria, según la estructura analítica del conjunto de datos cargado

Estos archivos se generan a partir de consultas SQL, no directamente desde los Excel locales.

## Estructura del proyecto

```text
Viz2026_Project/
├── data/
│   ├── Grafica_lineal_ventas_mensuales.xlsx
│   ├── Pagos en Punto de venta (pos.payment)(1).xlsx
│   ├── Sesión de Punto de venta (pos.session).xlsx
│   ├── Tabla dinámica Análisis de Punto de venta (report.pos.order)(4).xlsx
│   └── Órdenes del Punto de venta (pos.order)(2).xlsx
├── db/
│   ├── __init__.py
│   └── create_database.sql
├── output/
├── .env
├── .env.example
├── .gitignore
├── dataTransform.py
├── dbConnection.py
├── generate_ordenes.py
├── generate_pagos.py
├── loadToDB.py
├── README.md
├── requirements.txt
└── ...
```

## Componentes principales

### 1. `loadToDB.py`

Script encargado de recorrer los archivos `.xlsx` dentro de `data/`, aplicar la transformación correspondiente y cargarlos en la base de datos SQL. Cada archivo genera una tabla con un nombre normalizado, siguiendo la convención de minúsculas y sin espacios ni acentos.

### 2. `dataTransform.py`

Archivo central para la limpieza y transformación de datos. Incluye funciones reutilizables para:

- limpiar columnas,
- convertir fechas,
- eliminar duplicados,
- convertir campos numéricos,
- preparar datos de órdenes y pagos.

Estas funciones reciben y devuelven `pandas.DataFrame` y no contienen lógica de conexión ni lectura de archivos.

### 3. `dbConnection.py`

Gestiona la conexión a la base de datos mediante SQLAlchemy. La configuración se construye a partir de variables de entorno (`.env`) y permite alternar entre MySQL y PostgreSQL sin cambiar la lógica del código.

### 4. `generate_ordenes.py`

Genera una visualización de órdenes consultando directamente la base de datos SQL. La consulta se define como una variable llamada `query_variable` y se usa con `pandas.read_sql()`.

### 5. `generate_pagos.py`

Genera la visualización de pagos y agrupa el importe por método de pago. Además, permite alternar la vista por día, semana, mes y trimestre mediante controles interactivos de Plotly. El rango analizado está limitado a los años 2025 y 2026.

## Base de datos

El proyecto usa una base de datos llamada `Viz2026`. De forma predeterminada se configura para MySQL, aunque el motor puede cambiarse a PostgreSQL mediante la variable de entorno `DB_ENGINE`.

### MySQL

```sql
CREATE DATABASE IF NOT EXISTS Viz2026
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
```

### PostgreSQL

```sql
CREATE DATABASE "Viz2026";
```

> La base de datos debe existir antes de ejecutar el proceso de carga.

## Dependencias

El proyecto utiliza las siguientes librerías:

- pandas
- openpyxl
- sqlalchemy
- pymysql
- psycopg2-binary
- plotly
- python-dotenv

## Configuración del entorno

Se incluye un archivo `.env` con una configuración base para MySQL local:

```dotenv
# Ajusta usuario y contraseña si tus credenciales locales son distintas.
# Para PostgreSQL usa DB_ENGINE=postgresql y DB_PORT=5432.
DB_USER=root
DB_PASSWORD=root
DB_HOST=localhost
DB_PORT=3306
DB_NAME=Viz2026
DB_ENGINE=mysql
```

También existe `.env.example` como plantilla de referencia.

## Instalación

En PowerShell, desde la carpeta del proyecto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Orden de ejecución

Una vez instalado el entorno y configurada la base de datos:

```powershell
python loadToDB.py
python generate_ordenes.py
python generate_pagos.py
```

### ¿Qué se obtiene?

- Se cargan las tablas de Excel a SQL.
- Se generan gráficos HTML en `output/`.
- La fuente visual final proviene directamente de la base de datos y no de los archivos locales.

## Requisitos y buenas prácticas

- Los archivos de `data/` deben mantenerse intactos.
- No deben modificarse, reescribirse ni renombrarse.
- La lógica de transformación se mantiene separada de la lógica de acceso a la base de datos.
- Las consultas que alimentan los reportes se declaran en variables llamadas `query_variable` en cada script HTML-generador.

## Importancia del proyecto

Este proyecto representa una implementación práctica de ETL y visualización de datos aplicada a un caso real de análisis comercial. Su valor no solo está en la generación de gráficos, sino en la disciplina técnica detrás de ellos:

- extracción de datos desde archivos fuente,
- preparación y limpieza,
- almacenamiento en una base de datos estructurada,
- consulta analítica,
- construcción de reportes interactivos,
- y entrega de información útil para la toma de decisiones.

El resultado es un flujo analítico reproducible, mantenible y extensible, adecuado tanto para entornos educativos como para aplicaciones de reporting empresariales.

## Resumen breve

El proyecto transforma datos de ventas y pagos desde Excel a SQL, los prepara con limpieza y normalización, y genera reportes HTML interactivos con Plotly. La estructura está diseñada para ser clara, reutilizable y compatible con MySQL o PostgreSQL, siguiendo buenas prácticas de ingeniería de datos y análisis visual.
