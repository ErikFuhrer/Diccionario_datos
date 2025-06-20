# Diccionario de Datos MySQL con Interfaz Gráfica

Este proyecto es una herramienta de escritorio desarrollada en Python con `ttkbootstrap` que permite conectarse a una base de datos MySQL, visualizar su estructura y generar un PDF con el diccionario de datos.

## 📋 Funcionalidades

- Conexión a base de datos MySQL mediante credenciales del usuario.
- Visualización de:
  - Tablas
  - Columnas y sus tipos de datos
  - Claves primarias y foráneas
  - Vistas y procedimientos almacenados
- Generación de un archivo PDF con toda la información estructurada.

## 📦 Requisitos

- Python 3.x
- Paquetes Python necesarios:
  - `pymysql`
  - `reportlab`
  - `tkinter` (incluido en la mayoría de instalaciones de Python)
  - `ttkbootstrap`

Puedes instalar los paquetes requeridos con:

```bash
pip install pymysql reportlab ttkbootstrap
```

## 🚀 Cómo usar

1. Ejecuta el archivo `.py`.
2. Ingresa tus credenciales de conexión a la base de datos MySQL:
   - Host (ej. `localhost`)
   - Usuario
   - Contraseña
   - Nombre de la base de datos
3. Utiliza los botones para visualizar:
   - Tablas
   - Columnas
   - Claves
   - Vistas y procedimientos
4. Haz clic en **Generar PDF** para exportar el diccionario completo a `Diccionario_de_datos.pdf`.

## 📄 Salida PDF

El PDF generado incluye:

- Listado de tablas
- Detalle de columnas con tipos de datos
- Claves primarias y foráneas
- Vistas y procedimientos

## 🛠️ Estructura del Código

- Interfaz: `ttkbootstrap`
- Conexión a MySQL: `pymysql`
- Exportación PDF: `reportlab`
- Consultas a `INFORMATION_SCHEMA` para obtener metadatos de la base de datos
