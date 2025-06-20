import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.tableview import Tableview
from tkinter import messagebox
import pymysql
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# ---------- Funciones ----------
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

def mostrar_tablas():
    conexion = conectar_db()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute(f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA ='{tbbase.get()}';")
            resultados = cursor.fetchall()

            actualizar_tabla(["Tabla"], resultados)
            conexion.close()
        except pymysql.MySQLError as error:
            messagebox.showerror("Error de consulta", f"Error: {error}")

def mostrar_columnas():
    conexion = conectar_db()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute(f"""SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE
                               FROM INFORMATION_SCHEMA.COLUMNS
                               WHERE TABLE_SCHEMA = '{tbbase.get()}'
                               ORDER BY TABLE_NAME;""")
            resultados = cursor.fetchall()
            actualizar_tabla(["Tabla", "Campo", "Tipo de Dato"], resultados)
            conexion.close()
        except pymysql.MySQLError as error:
            messagebox.showerror("Error de consulta", f"Error: {error}")

def mostrar_claves():
    conexion = conectar_db()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute(f"""SELECT TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME,
                                      REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                               FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                               WHERE TABLE_SCHEMA = '{tbbase.get()}';""")
            resultados = cursor.fetchall()
            actualizar_tabla(
                ["Tabla", "Campo", "Tipo de Clave", "Referencia Tabla", "Referencia Campo"],
                resultados
            )
            conexion.close()
        except pymysql.MySQLError as error:
            messagebox.showerror("Error de consulta", f"Error: {error}")

def mostrar_vistas_procedimientos():
    conexion = conectar_db()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute(f"""
                (SELECT 'Vista' AS Tipo, TABLE_NAME AS Nombre
                 FROM INFORMATION_SCHEMA.VIEWS
                 WHERE TABLE_SCHEMA = '{tbbase.get()}')
                 UNION
                (SELECT 'Procedimiento', ROUTINE_NAME
                 FROM INFORMATION_SCHEMA.ROUTINES
                 WHERE ROUTINE_SCHEMA = '{tbbase.get()}');
            """)
            resultados = cursor.fetchall()
            actualizar_tabla(["Tipo", "Nombre"], resultados)
            conexion.close()
        except pymysql.MySQLError as error:
            messagebox.showerror("Error de consulta", f"Error: {error}")

def actualizar_tabla(columnas, datos):
    tabla.delete(*tabla.get_children())
    tabla.config(columns=columnas, show="headings")

    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, anchor="center")

    for row in datos:
        tabla.insert("", "end", values=row)

def generar_pdf():
    doc = SimpleDocTemplate("Diccionario_de_datos.pdf", pagesize=letter)
    estilos = getSampleStyleSheet()
    elementos = [Paragraph("Diccionario de Datos", estilos['Title'])]

    consultas = {
        "Tablas": f"(SELECT 'Tabla') UNION (SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA ='{tbbase.get()}')",
        "Tipos de dato por columna y tabla":
            f"(SELECT 'Tabla', 'Nombre de Columna', 'Tipo de Dato') "
            f"UNION (SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE "
            f"FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = '{tbbase.get()}' ORDER BY TABLE_NAME)",
        "Claves primarias y foraneas":
            f"(SELECT 'Tabla', 'Nombre de Columna', 'Tipo de Clave', 'Referencia con Tabla', 'Referencia con Campo') "
            f"UNION (SELECT TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME "
            f"FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA = '{tbbase.get()}')",
        "Vistas y Procedimientos":
            f"(SELECT 'Tipo', 'Nombre') "
            f"UNION (SELECT 'Vista', TABLE_NAME FROM INFORMATION_SCHEMA.VIEWS WHERE TABLE_SCHEMA = '{tbbase.get()}') "
            f"UNION (SELECT 'Procedimiento', ROUTINE_NAME FROM INFORMATION_SCHEMA.ROUTINES WHERE ROUTINE_SCHEMA = '{tbbase.get()}')"
    }

    for titulo, query in consultas.items():
        conexion = conectar_db()
        if conexion:
            try:
                cursor = conexion.cursor()
                cursor.execute(query)
                datos = cursor.fetchall()
                conexion.close()

                elementos.append(Paragraph(f"{titulo}:", estilos["Heading2"]))
                t = Table(datos)
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
            except pymysql.MySQLError as error:
                messagebox.showerror("Error de consulta", f"Error: {error}")

    doc.build(elementos)
    messagebox.showinfo("PDF Generado", "Datos exportados a Diccionario_de_datos.pdf")

# ---------- Interfaz con ttkbootstrap ----------
ventana = tb.Window(themename="solar")
ventana.title("Diccionario de Datos")
ventana.geometry("1000x600")

frm = tb.Frame(ventana, padding=10)
frm.pack(fill=BOTH, expand=True)

# Entradas
tb.Label(frm, text="Host:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
tbhost = tb.Entry(frm)
tbhost.grid(row=0, column=1, padx=5, pady=5)

tb.Label(frm, text="Usuario:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
tbusuario = tb.Entry(frm)
tbusuario.grid(row=1, column=1, padx=5, pady=5)

tb.Label(frm, text="Contraseña:").grid(row=2, column=0, padx=5, pady=5, sticky=W)
tbcontrasena = tb.Entry(frm, show="*")
tbcontrasena.grid(row=2, column=1, padx=5, pady=5)

tb.Label(frm, text="Base de Datos:").grid(row=3, column=0, padx=5, pady=5, sticky=W)
tbbase = tb.Entry(frm)
tbbase.grid(row=3, column=1, padx=5, pady=5)

# Botones
boton_frame = tb.Frame(frm)
boton_frame.grid(row=0, column=2, rowspan=4, padx=10, pady=10)

tb.Button(boton_frame, text="Listar Tablas", command=mostrar_tablas, bootstyle=PRIMARY).pack(pady=2)
tb.Button(boton_frame, text="Ver Columnas", command=mostrar_columnas, bootstyle=PRIMARY).pack(pady=2)
tb.Button(boton_frame, text="Ver Claves", command=mostrar_claves, bootstyle=PRIMARY).pack(pady=2)
tb.Button(boton_frame, text="Vistas y Procedimientos", command=mostrar_vistas_procedimientos, bootstyle=PRIMARY).pack(pady=2)
tb.Button(boton_frame, text="Generar PDF", command=generar_pdf, bootstyle=SUCCESS).pack(pady=10)

# Tabla
tabla = tb.Treeview(frm)
tabla.grid(row=4, column=0, columnspan=3, sticky="nsew", pady=10)

# Scroll
scroll = tb.Scrollbar(frm, orient="vertical", command=tabla.yview)
tabla.configure(yscrollcommand=scroll.set)
scroll.grid(row=4, column=3, sticky="ns")

# Expansión de la tabla
frm.grid_rowconfigure(4, weight=1)
frm.grid_columnconfigure(2, weight=1)

ventana.mainloop()