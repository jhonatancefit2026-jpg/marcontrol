"""
main.py — Punto de entrada de MarControl
Sistema de Control Pesquero — Python MVC + Tkinter + MySQL
"""
import os
import sys

# Asegurar que el directorio del proyecto esté en el PYTHONPATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)


def verificar_dependencias():
    """Verifica que todas las dependencias estén instaladas."""
    dependencias = {
        'mysql.connector': 'mysql-connector-python',
        'PIL':             'Pillow',
        'openpyxl':        'openpyxl',
        'reportlab':       'reportlab',
        'tkcalendar':      'tkcalendar',
    }
    faltantes = []
    for modulo, paquete in dependencias.items():
        try:
            __import__(modulo)
        except ImportError:
            faltantes.append(paquete)
    return faltantes


def generar_favicon_si_no_existe():
    """Genera el favicon si no existe."""
    ruta = os.path.join(BASE_DIR, "assets", "favicon.ico")
    if not os.path.exists(ruta):
        try:
            os.makedirs(os.path.join(BASE_DIR, "assets"), exist_ok=True)
            from assets.favicon_gen import generar_favicon
            generar_favicon(ruta)
        except Exception as e:
            print(f"[Favicon] No se pudo generar el favicon: {e}")


def main():
    # Verificar dependencias
    faltantes = verificar_dependencias()
    if faltantes:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Dependencias faltantes",
            "Instale las siguientes dependencias para ejecutar MarControl:\n\n"
            + "\n".join(f"  pip install {p}" for p in faltantes)
            + "\n\nO ejecute: pip install -r requirements.txt"
        )
        root.destroy()
        sys.exit(1)

    # Generar favicon
    generar_favicon_si_no_existe()

    # Verificar conexión a base de datos
    try:
        from database import Database
        db = Database.get_instance()
        conn = db.get_connection()
        if conn is None:
            raise Exception("No se pudo establecer conexión.")
        print("[Main] Conexión a MarControl verificada correctamente.")
    except Exception as e:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        respuesta = messagebox.askokcancel(
            "Error de conexión",
            f"No se pudo conectar a la base de datos MySQL:\n{e}\n\n"
            "Verifique:\n"
            "  • MySQL está ejecutándose\n"
            "  • La base de datos 'marcontrol' existe\n"
            "  • Las credenciales en config.py son correctas\n\n"
            "¿Desea continuar de todas formas (modo sin base de datos)?"
        )
        root.destroy()
        if not respuesta:
            sys.exit(1)

    # Lanzar aplicación
    from views.main_view import VentanaPrincipal
    app = VentanaPrincipal()
    app.mainloop()


if __name__ == "__main__":
    main()
