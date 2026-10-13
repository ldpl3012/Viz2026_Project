# Viz2026

Proyecto para importar los archivos Excel existentes de `data/` a una base de datos
MySQL (o PostgreSQL), transformar los datos con pandas y generar gráficas HTML
interactivas consultando directamente la base de datos mediante SQLAlchemy.

## Requisitos

- Python 3.10 o superior
- MySQL local por defecto, o PostgreSQL configurado en `.env`
- Los archivos `.xlsx` ya están en `data/`; no deben modificarse

## Crear la base de datos

MySQL:

```sql
CREATE DATABASE IF NOT EXISTS Viz2026
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
```

También puedes ejecutar `db/create_database.sql`. Desde una terminal con el cliente
MySQL configurado:

```powershell
Get-Content .\db\create_database.sql | mysql -u root -p
```

PostgreSQL:

```sql
CREATE DATABASE "Viz2026";
```

Este comando se ejecuta conectado a PostgreSQL, no dentro de la base de datos que
se está creando. Desde PowerShell puedes ejecutarlo así:

```powershell
psql -U postgres -c 'CREATE DATABASE "Viz2026";'
```

SQLAlchemy no crea bases de datos automáticamente. Si el motor o las credenciales
no están disponibles, crea la base con el comando correspondiente.

## Configurar `.env`

El proyecto incluye un `.env` local de ejemplo para MySQL (`root` / `root`).
Ajusta usuario, contraseña, host y puerto según tu instalación. No compartas ni
incluyas este archivo con credenciales en el control de versiones.

Para PostgreSQL configura, por ejemplo:

```dotenv
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=5432
DB_NAME=Viz2026
DB_ENGINE=postgresql
```

Para MySQL usa `DB_ENGINE=mysql` y normalmente `DB_PORT=3306`.

## Entorno e instalación

En PowerShell, desde la carpeta del proyecto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

En Visual Studio Code selecciona el intérprete `.venv` del proyecto.

## Ejecución

Desde la carpeta del proyecto y con el entorno virtual activado:

```powershell
python loadToDB.py
python generate_ordenes.py
python generate_pagos.py
```

`loadToDB.py` lee únicamente los `.xlsx` directamente dentro de `data/`, crea
una tabla por archivo (nombre normalizado a minúsculas, ASCII y guiones bajos) y
reemplaza esa tabla en cada carga. Luego los generadores leen de SQL y escriben
`output/ordenes.html` y `output/pagos.html`. La gráfica de pagos permite alternar
día, semana, mes y trimestre, y se limita a registros de 2025 y 2026.
