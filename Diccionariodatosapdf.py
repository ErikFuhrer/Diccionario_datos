import tkinter as tk
from tkinter import messagebox, ttk
import pymysql
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# ----------Funciones------------
def conectar_db():
    try:
        conexion = pymysql.connect(
            host=tbhost.get(),
            user=tbusuario.get(),
            password=tbcontrasena.get(),
            database=tbbase.get()
        )
        return conexion
    except pymysql.MySQLError as error:
        messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos: {error}")
        return None

# Muestra todas las tablas de la base de datos desde INFORMATION_SCHEMA
def mostrar_tablas():
    conexion = conectar_db()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute(f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA ='{tbbase.get()}';")
            resultados = cursor.fetchall()
            
            # Limpiar la tabla antes de mostrar datos
            for row in tabla.get_children():
                tabla.delete(row)

            # Configurar las columnas del treeview
            tabla["columns"] = ("Tabla",)
            tabla.heading("Tabla", text="Tabla")
            tabla.column("Tabla", width=150, anchor="center")
            tabla.configure(show="headings")

            # Insertar datos en la tabla
            for row in resultados:
                tabla.insert("", "end", values=row)

            conexion.close()
        except pymysql.MySQLError as error:
            messagebox.showerror("Error de consulta", f"Error: {error}")

# Muestra todas las columnas y sus tipos de todas las tablas
def mostrar_columnas():
        conexion = conectar_db()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute(f"SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = '{tbbase.get()}' ORDER BY TABLE_NAME;")
                resultados = cursor.fetchall()
                
                # Limpiar la tabla antes de mostrar datos
                for row in tabla.get_children():
                    tabla.delete(row)

                # Configurar las columnas del treeview
                tabla["columns"] = ("NombreTabla", "NombreColumna", "TipoDato")
                tabla.configure(show="headings")  # Oculta la columna #0

                # Configurar encabezados
                tabla.heading("NombreTabla", text="Tabla")
                tabla.heading("NombreColumna", text="Campo")
                tabla.heading("TipoDato", text="Tipo de Dato")

                # Configurar ancho y alineación de las columnas
                tabla.column("NombreTabla", width=100, anchor="center")
                tabla.column("NombreColumna", width=150, anchor="center")
                tabla.column("TipoDato", width=120, anchor="center")

                # Insertar datos en la tabla
                for row in resultados:
                    tabla.insert("", "end", values=row)

                conexion.close()
            except pymysql.MySQLError as error:
                messagebox.showerror("Error de consulta", f"Error: {error}")

# Muestra las claves primarias y foraneas de todas las tablas
def mostrar_claves():
    conexion = conectar_db()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute(f"SELECT TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA = '{tbbase.get()}';")
            resultados = cursor.fetchall()
            
            # Limpiar la tabla antes de mostrar datos
            for row in tabla.get_children():
                tabla.delete(row)

            # Configurar las columnas del treeview
            tabla["columns"] = ("NombreTabla", "NombreCampo", "Clave", "ReferenciaTabla", "ReferenciaColumna")
            tabla.configure(show="headings")  # Oculta la columna #0

            # Configurar encabezados
            tabla.heading("NombreTabla", text="Tabla")
            tabla.heading("NombreCampo", text="Campo")
            tabla.heading("Clave", text="Tipo de Clave")
            tabla.heading("ReferenciaTabla", text="Relacion con tabla")
            tabla.heading("ReferenciaColumna", text="Relacion con campo")

            # Configurar ancho y alineación de las columnas
            tabla.column("NombreTabla", width=100, anchor="center")
            tabla.column("NombreCampo", width=150, anchor="center")
            tabla.column("Clave", width=120, anchor="center")
            tabla.column("ReferenciaTabla", width=120, anchor="center")
            tabla.column("ReferenciaColumna", width=120, anchor="center")

            # Insertar datos en la tabla
            for row in resultados:
                tabla.insert("", "end", values=row)

            conexion.close()
        except pymysql.MySQLError as error:
            messagebox.showerror("Error de consulta", f"Error: {error}")

# Muestra las vistas y los procedimientos de la base de datos
def mostrar_vistas_procedimientos():
    conexion = conectar_db()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute(f"(SELECT 'Vista' AS Tipo, TABLE_NAME AS Nombre FROM INFORMATION_SCHEMA.VIEWS WHERE TABLE_SCHEMA = '{tbbase.get()}')UNION(SELECT 'Procedimiento' AS Tipo, ROUTINE_NAME AS Nombre FROM INFORMATION_SCHEMA.ROUTINES WHERE ROUTINE_SCHEMA = '{tbbase.get()}');")
            resultados = cursor.fetchall()
            
            # Limpiar la tabla antes de mostrar datos
            for row in tabla.get_children():
                tabla.delete(row)

            # Configurar las columnas del treeview
            tabla["columns"] = ("Tipo", "Nombre")
            tabla.configure(show="headings")  # Oculta la columna #0

            # Configurar encabezados
            tabla.heading("Tipo", text="Tipo")
            tabla.heading("Nombre", text="Nombre")

            # Configurar ancho y alineación de las columnas
            tabla.column("Tipo", width=100, anchor="center")
            tabla.column("Nombre", width=150, anchor="center")

            # Insertar datos en la tabla
            for row in resultados:
                tabla.insert("", "end", values=row)

            conexion.close()
        except pymysql.MySQLError as error:
            messagebox.showerror("Error de consulta", f"Error: {error}")

# Genera pdf con los datos de las 4 consultas
def generar_pdf():
    doc = SimpleDocTemplate("Diccionario_de_datos.pdf", pagesize=letter)
    estilos = getSampleStyleSheet()

    # Lista de elementos para agregar texto y tablas
    elementos = []

    # Titulo del documento 
    elementos.append(Paragraph("Diccionario de Datos", estilos['Title']))
    elementos.append(Paragraph("<br/><br/>", estilos['Normal']))

    # Sacar datos 
    resultados_tablas = None
    resultados_claves = None
    resultados_tipo_dato = None
    resultaods_vistas_procedimientos = None

    # Tablas
    conexion = conectar_db()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute(f"(SELECT 'Tabla')UNION (SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA ='{tbbase.get()}');")
            resultados_tablas = cursor.fetchall()
            conexion.close()
        except pymysql.MySQLError as error:
            messagebox.showerror("Error de consulta", f"Error: {error}")

    # Tipos de dato de los campos por tabla
    conexion = conectar_db()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute(f"(SELECT 'Tabla', 'Nombre de Columna', 'Tipo de Dato')UNION (SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = '{tbbase.get()}' ORDER BY TABLE_NAME);")
            resultados_tipo_dato = cursor.fetchall()
            conexion.close()
        except pymysql.MySQLError as error:
            messagebox.showerror("Error de consulta", f"Error: {error}")

    # Claves
    conexion = conectar_db()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute(f"(SELECT 'Tabla', 'Nombre de Columna', 'Tipo de Clave', 'Referencia con Tabla', 'Referencia con Campo') UNION (SELECT TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA = '{tbbase.get()}');")
            resultados_claves = cursor.fetchall()
            conexion.close()
        except pymysql.MySQLError as error:
            messagebox.showerror("Error de consulta", f"Error: {error}")

    # Vistas y Procedimientos
    conexion = conectar_db()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute(f"(SELECT 'Tipo', 'Nombre') UNION (SELECT 'Vista' AS Tipo, TABLE_NAME AS Nombre FROM INFORMATION_SCHEMA.VIEWS WHERE TABLE_SCHEMA = '{tbbase.get()}')UNION(SELECT 'Procedimiento' AS Tipo, ROUTINE_NAME AS Nombre FROM INFORMATION_SCHEMA.ROUTINES WHERE ROUTINE_SCHEMA = '{tbbase.get()}');")
            resultaods_vistas_procedimientos = cursor.fetchall()
            conexion.close()
        except pymysql.MySQLError as error:
            messagebox.showerror("Error de consulta", f"Error: {error}")

    # Agregar datos de las consultas
    # Tablas
    elementos.append(Paragraph("Tablas:", estilos['Heading2']))
    t = Table(resultados_tablas)
    t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
    elementos.append(t)
    elementos.append(Paragraph("<br/><br/>", estilos["Normal"]))
    # Tipo Datos
    elementos.append(Paragraph("Tipos de dato por columna y tabla:", estilos['Heading2']))
    t = Table(resultados_tipo_dato)
    t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
    elementos.append(t)
    elementos.append(Paragraph("<br/><br/>", estilos["Normal"]))
    # claves
    elementos.append(Paragraph("Claves primarias y foraneas:", estilos['Heading2']))
    t = Table(resultados_claves)
    t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
    elementos.append(t)
    elementos.append(Paragraph("<br/><br/>", estilos["Normal"]))
    # Vistas y Procedimientos
    elementos.append(Paragraph("Vistas y Procedimientos:", estilos['Heading2']))
    t = Table(resultaods_vistas_procedimientos)
    t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
    elementos.append(t)
    elementos.append(Paragraph("<br/><br/>", estilos["Normal"]))

    # Generar el PDF
    doc.build(elementos)
    messagebox.showinfo("PDF Generado", f"Datos exportados a Diccionario_de_datos.pdf")

#----------INTERFAZ GRAFICA-----------
ventana = tk.Tk()
ventana.title("Diccionario de Datos")
ventana.geometry("800x500")

# Labels y textbox para conexión
tk.Label(ventana, text="Host:").grid(row=0, column=0, padx=5, pady=5)
tbhost = tk.Entry(ventana)
tbhost.grid(row=0, column=1, padx=5, pady=5)

tk.Label(ventana, text="usuario:").grid(row=1, column=0, padx=5, pady=5)
tbusuario = tk.Entry(ventana)
tbusuario.grid(row=1, column=1, padx=5, pady=5)

tk.Label(ventana, text="Contraseña:").grid(row=2, column=0, padx=5, pady=5)
tbcontrasena = tk.Entry(ventana, show="*")
tbcontrasena.grid(row=2, column=1, padx=5, pady=5)

tk.Label(ventana, text="Base de Datos:").grid(row=3, column=0, padx=5, pady=5)
tbbase = tk.Entry(ventana)
tbbase.grid(row=3, column=1, padx=5, pady=5)

# Botones de consultas
tk.Button(ventana, text="Listar Tablas", command=mostrar_tablas).grid(row=4, column=0, padx=5, pady=5)
tk.Button(ventana, text="Ver Columnas", command=mostrar_columnas).grid(row=4, column=1, padx=5, pady=5)
tk.Button(ventana, text="Ver Claves", command=mostrar_claves).grid(row=5, column=0, padx=5, pady=5)
tk.Button(ventana, text="Ver Vistas y Procedimientos", command=mostrar_vistas_procedimientos).grid(row=5, column=1, padx=5, pady=5)
tk.Button(ventana, text="Generar PDF", command=generar_pdf).grid(row=7, column=1, padx=5, pady=5)

# Treeview para mostrar resultados en forma de tabla
tabla = ttk.Treeview(ventana)
tabla.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

# Scrollbar para la tabla
scrollbar = ttk.Scrollbar(ventana, orient="vertical", command=tabla.yview)
scrollbar.grid(row=6, column=2, sticky="ns")
tabla.configure(yscrollcommand=scrollbar.set)

ventana.mainloop()