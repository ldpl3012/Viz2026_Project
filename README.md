# Viz2026

Proyecto de análisis y visualización de datos basado en archivos Excel, cargados a una base de datos SQL y procesados con Python. El objetivo del sistema es transformar información operativa en reportes interactivos listos para consulta y análisis empresarial.

El proyecto está orientado a la lectura de datos de ventas, pagos y sesiones desde archivos `.xlsx`, su preparación y limpieza en Python, y la generación de gráficas HTML a partir de consultas directamente ejecutadas sobre la base de datos.

## Descripción general

El flujo del sistema es el siguiente:

1. Se leen los archivos Excel ubicados en `data/`.
2. Los datos se limpian, normalizan y transforman con funciones definidas en `dataTransform.py`.
3. La información se carga en una base de datos SQL llamada `Viz2026` usando `SQLAlchemy`.
4. Se ejecutan consultas específicas (declaradas como `query_variable`) para recuperar los datos necesarios.
5. Se generan reportes HTML interactivos con Plotly, envueltos en un template oscuro común (`html_template.py`), y se almacenan en la carpeta `output/`.

La arquitectura es útil para entornos empresariales donde los datos de operación no deben depender de los archivos originales y donde la visualización debe ser reproducible, consistente y actualizable.

## Objetivo del proyecto

El proyecto tiene como finalidad convertir datos brutos almacenados en Excel en información analítica preparada para la toma de decisiones. En particular, trabaja con datos de ventas, pagos y sesiones de un punto de venta, permitiendo:

- normalizar nombres de columnas,
- convertir fechas y montos,
- eliminar duplicados,
- cargar datos a una base de datos relacional,
- generar dashboards interactivos analizando tendencias y comportamiento por período.

## Outputs generados

El proyecto genera tres archivos HTML en la carpeta `output/`:

- `output/ordenes.html` — Importe total agrupado por mes y responsable (barras agrupadas).
- `output/pagos.html` — Importe agrupado por método de pago, con selector interactivo día / semana / mes / trimestre, filtrando solo 2025-2026.
- `output/sesiones.html` — Duración promedio de las sesiones por semana y por usuario (barras agrupadas).

Los tres HTMLs comparten la misma estética oscura tipo dashboard SQL (badge verde, KPIs, caja de query y tarjeta de gráfica). Se generan a partir de consultas SQL, no directamente desde los Excel locales.

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
│   ├── ordenes.html
│   ├── pagos.html
│   └── sesiones.html
├── .env
├── .env.example
├── .gitignore
├── dataTransform.py
├── dbConnection.py
├── generate_ordenes.py
├── generate_pagos.py
├── generate_sesiones.py
├── html_template.py
├── loadToDB.py
├── README.md
├── requirements.txt
└── ...
```

## Componentes principales

### 1. `loadToDB.py`

Script encargado de recorrer los archivos `.xlsx` dentro de `data/`, aplicar la transformación correspondiente y cargarlos en la base de datos SQL. Cada archivo genera una tabla con un nombre normalizado, siguiendo la convención de minúsculas, sin espacios ni acentos.

Ejemplos de mapeo archivo → tabla:

| Archivo en `data/` | Tabla en `Viz2026` |
|--------------------|--------------------|
| `Grafica_lineal_ventas_mensuales.xlsx` | `grafica_lineal_ventas_mensuales` |
| `Pagos en Punto de venta (pos.payment)(1).xlsx` | `pagos_en_punto_de_venta_pos_payment_1` |
| `Sesión de Punto de venta (pos.session).xlsx` | `sesion_de_punto_de_venta_pos_session` |
| `Tabla dinámica Análisis de Punto de venta (report.pos.order)(4).xlsx` | `tabla_dinamica_analisis_de_punto_de_venta_report_pos_order_4` |
| `Órdenes del Punto de venta (pos.order)(2).xlsx` | `ordenes_del_punto_de_venta_pos_order_2` |

### 2. `dataTransform.py`

Archivo central para la limpieza y transformación de datos. Incluye funciones reutilizables para:

- limpiar columnas,
- convertir fechas,
- eliminar duplicados,
- convertir campos numéricos,
- preparar datos de órdenes, pagos y sesiones.

Funciones expuestas:

- `limpiar_columnas(df)`
- `convertir_fechas(df, columnas)`
- `eliminar_duplicados(df)`
- `convertir_numericos(df, columnas)`
- `transformar_ordenes(df)`
- `transformar_pagos(df)`
- `transformar_sesiones(df)`

Estas funciones reciben y devuelven `pandas.DataFrame` y no contienen lógica de conexión ni lectura de archivos.

### 3. `dbConnection.py`

Gestiona la conexión a la base de datos mediante SQLAlchemy. La configuración se construye a partir de variables de entorno (`.env`) y permite alternar entre MySQL y PostgreSQL sin cambiar la lógica del código. Expone `get_engine()` y `get_session()`.

### 4. `generate_ordenes.py`

Genera `output/ordenes.html` consultando la tabla `ordenes_del_punto_de_venta_pos_order_2`. La consulta se define como variable `query_variable` y se ejecuta con `pandas.read_sql()`. El resultado se agrupa por mes y responsable, se grafica con Plotly en barras agrupadas y se envuelve con el template oscuro.

### 5. `generate_pagos.py`

Genera `output/pagos.html`. La tabla consultada es `pagos_en_punto_de_venta_pos_payment_1`, renombrando `metodo_de_pago` como `metodo_pago` en el propio query. Agrupa el importe por método de pago y permite alternar la vista por día, semana, mes y trimestre mediante `updatemenus` de Plotly. El rango analizado está limitado a 2025 y 2026.

### 6. `generate_sesiones.py`

Genera `output/sesiones.html`. Consulta la tabla `sesion_de_punto_de_venta_pos_session`, calcula la duración de cada sesión como la diferencia entre `fecha_de_cierre` y `fecha_de_apertura` (en minutos), filtra duraciones válidas y agrupa por semana y usuario (`abierta_por`) mostrando el promedio. Gráfica en barras agrupadas.

### 7. `html_template.py`

Define la función `build_html(...)`, que envuelve el `<div>` de Plotly en un layout HTML completo con estética oscura tipo dashboard SQL:

- Badge superior con el texto "BASE DE DATOS MYSQL: VIZ2026 • REPORTE SQL".
- Título y subtítulo.
- Dos KPIs (facturación / importe total y registros extraídos).
- Caja con el contenido de `query_variable` en fuente monoespaciada y borde cyan.
- Tarjeta con la gráfica Plotly en fondo oscuro.

Los tres generadores usan esta función para mantener la misma estética.

## Base de datos

El proyecto usa una base de datos llamada `Viz2026`. De forma predeterminada se configura para MySQL, aunque el motor puede cambiarse a PostgreSQL mediante la variable de entorno `DB_ENGINE`.

### MySQL

```sql
CREATE DATABASE IF NOT EXISTS Viz2026
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
```

Ejecutable desde PowerShell con XAMPP:

```powershell
& "C:\xampp\mysql\bin\mysql.exe" -u root -e "CREATE DATABASE IF NOT EXISTS Viz2026 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### PostgreSQL

```sql
CREATE DATABASE "Viz2026";
```

```powershell
psql -U postgres -c 'CREATE DATABASE "Viz2026";'
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
# En XAMPP el usuario root normalmente no tiene contraseña (déjala vacía).
# Para PostgreSQL usa DB_ENGINE=postgresql y DB_PORT=5432.
DB_USER=root
DB_PASSWORD=
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
python generate_sesiones.py
```

### ¿Qué se obtiene?

- Se cargan las tablas de Excel a SQL.
- Se generan los tres gráficos HTML en `output/`.
- La fuente visual final proviene directamente de la base de datos y no de los archivos locales.

## Requisitos y buenas prácticas

- Los archivos de `data/` deben mantenerse intactos.
- No deben modificarse, reescribirse ni renombrarse.
- La lógica de transformación se mantiene separada de la lógica de acceso a la base de datos.
- Las consultas que alimentan los reportes se declaran en variables llamadas `query_variable` en cada script HTML-generador.
- La estética compartida se centraliza en `html_template.py`.

## Notas sobre `.gitignore` y outputs

El archivo `.gitignore` está configurado para excluir:

```gitignore
.venv/
__pycache__/
.env
*.pyc
```

Los HTMLs de `output/` **sí se suben al repositorio** (no están ignorados). Si en el futuro quieres que se regeneren automáticamente y no subirlos, agrega esta línea al `.gitignore`:

```gitignore
output/*.html
```

Si quieres ignorar todos los HTMLs excepto los tres principales, puedes usar:

```gitignore
output/*.html
!output/ordenes.html
!output/pagos.html
!output/sesiones.html
```

## Subir el proyecto a GitHub

Si algún archivo `.xlsx` de `data/` supera los **100 MB**, GitHub lo bloqueará y será necesario usar **Git LFS**.

### Flujo normal (todos los archivos < 100 MB)

```powershell
git init
git add .
git commit -m "Primer commit - estructura base del proyecto"
git remote add origin https://github.com/TU_USUARIO/Viz2026_Project.git
git branch -M main
git push -u origin main
```

Si al hacer `git push` te pide contraseña y tienes 2FA activo, genera un **Personal Access Token** en GitHub y úsalo como contraseña.

### Flujo con Git LFS (archivos > 100 MB)

```powershell
git lfs install
git lfs track "*.xlsx"
git add .gitattributes
git commit -m "Configurar Git LFS para archivos xlsx"
git add .
git commit -m "Subir archivos xlsx con LFS"
git push -u origin main
```

> Plan gratuito de LFS: 1 GB de almacenamiento y 1 GB de ancho de banda por mes.

## Solución de problemas comunes

### `Unknown column 'metodo_pago' in 'field list'`

La tabla en MySQL tiene la columna como `metodo_de_pago`, no `metodo_pago`. Solución: en `generate_pagos.py`, usa `SELECT importe, metodo_de_pago AS metodo_pago, fecha FROM ...` o agrega `"metodo_de_pago"` a los candidatos en `transformar_pagos()` dentro de `dataTransform.py`.

### `NameError: name 'figure' is not defined`

El bloque final que llama a `figure.to_html(...)` quedó fuera del alcance donde se define `figure`. Solución: construye `figure` siempre en una sola ruta (sin ramas `if/elif/else` que puedan saltarse su definición) o mueve la generación del HTML dentro de la misma rama.

### `Table 'viz2026.sesion_punto_de_venta' doesn't exist`

El nombre real de la tabla es `sesion_de_punto_de_venta_pos_session`. Corrige `TABLE_NAME` en `generate_sesiones.py` o el `query_variable` correspondiente.

### `Access denied for user 'root'@'localhost'`

Credenciales incorrectas en `.env`. En XAMPP, el usuario `root` normalmente tiene contraseña vacía, así que `DB_PASSWORD=` debe quedar sin valor.

### `ModuleNotFoundError: No module named 'html_template'`

El archivo `html_template.py` no existe en la raíz del proyecto. Créalo con la función `build_html(...)` antes de ejecutar los generadores.

## Importancia del proyecto

Este proyecto representa una implementación práctica de ETL y visualización de datos aplicada a un caso real de análisis comercial. Su valor no solo está en la generación de gráficos, sino en la disciplina técnica detrás de ellos:

- extracción de datos desde archivos fuente,
- preparación y limpieza,
- almacenamiento en una base de datos estructurada,
- consulta analítica,
- construcción de reportes interactivos con estética consistente,
- y entrega de información útil para la toma de decisiones.

El resultado es un flujo analítico reproducible, mantenible y extensible, adecuado tanto para entornos educativos como para aplicaciones de reporting empresariales.
