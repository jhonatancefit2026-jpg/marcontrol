"""
Módulo de validaciones para campos del formulario
"""
import re
from datetime import datetime


def validar_numerico(valor, campo="Campo", min_val=None, max_val=None, decimal=False):
    """Valida que el valor sea numérico."""
    if not valor or str(valor).strip() == "":
        return False, f"{campo} es obligatorio."
    try:
        num = float(valor) if decimal else int(valor)
        if min_val is not None and num < min_val:
            return False, f"{campo} debe ser mayor o igual a {min_val}."
        if max_val is not None and num > max_val:
            return False, f"{campo} debe ser menor o igual a {max_val}."
        return True, ""
    except ValueError:
        tipo = "decimal" if decimal else "entero"
        return False, f"{campo} debe ser un número {tipo} válido."


def validar_texto(valor, campo="Campo", min_len=1, max_len=200, requerido=True):
    """Valida que el valor sea texto con longitud válida."""
    if not valor or str(valor).strip() == "":
        if requerido:
            return False, f"{campo} es obligatorio."
        return True, ""
    valor = str(valor).strip()
    if len(valor) < min_len:
        return False, f"{campo} debe tener al menos {min_len} caracteres."
    if len(valor) > max_len:
        return False, f"{campo} no puede superar {max_len} caracteres."
    return True, ""


def validar_email(email, campo="Email"):
    """Valida formato de correo electrónico con regex."""
    if not email or str(email).strip() == "":
        return True, ""  # Email opcional por defecto
    patron = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    if re.match(patron, str(email).strip()):
        return True, ""
    return False, f"{campo} no tiene un formato válido (ej: usuario@dominio.com)."


def validar_telefono(telefono, campo="Teléfono"):
    """Valida formato de teléfono."""
    if not telefono or str(telefono).strip() == "":
        return True, ""
    patron = r'^\+?[\d\s\-]{7,20}$'
    if re.match(patron, str(telefono).strip()):
        return True, ""
    return False, f"{campo} no tiene un formato válido."


def validar_fecha(fecha_str, campo="Fecha"):
    """Valida que la fecha tenga formato DD/MM/YYYY o YYYY-MM-DD."""
    if not fecha_str or str(fecha_str).strip() == "":
        return False, f"{campo} es obligatoria."
    formatos = ['%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y']
    for fmt in formatos:
        try:
            datetime.strptime(str(fecha_str).strip(), fmt)
            return True, ""
        except ValueError:
            continue
    return False, f"{campo} debe tener formato DD/MM/YYYY."


def validar_fecha_rango(fecha_inicio, fecha_fin, campo_ini="Fecha inicio", campo_fin="Fecha fin"):
    """Valida que la fecha de inicio sea anterior a la de fin."""
    ok1, msg1 = validar_fecha(fecha_inicio, campo_ini)
    if not ok1:
        return False, msg1
    ok2, msg2 = validar_fecha(fecha_fin, campo_fin)
    if not ok2:
        return False, msg2
    formatos = ['%d/%m/%Y', '%Y-%m-%d']
    d1, d2 = None, None
    for fmt in formatos:
        try:
            d1 = datetime.strptime(str(fecha_inicio).strip(), fmt)
            break
        except ValueError:
            continue
    for fmt in formatos:
        try:
            d2 = datetime.strptime(str(fecha_fin).strip(), fmt)
            break
        except ValueError:
            continue
    if d1 and d2 and d1 > d2:
        return False, f"{campo_ini} debe ser anterior a {campo_fin}."
    return True, ""


def validar_imagen(ruta, campo="Imagen"):
    """Valida que la imagen tenga formato soportado."""
    if not ruta or str(ruta).strip() == "":
        return True, ""  # imagen opcional
    extensiones_validas = ['.jpg', '.jpeg', '.png', '.gif']
    import os
    _, ext = os.path.splitext(ruta)
    if ext.lower() not in extensiones_validas:
        return False, f"{campo}: formato no soportado. Use JPG, PNG o GIF."
    if not os.path.isfile(ruta):
        return False, f"{campo}: el archivo no existe."
    # Validar tamaño máximo: 5 MB
    tam = os.path.getsize(ruta)
    if tam > 5 * 1024 * 1024:
        return False, f"{campo}: el archivo supera el tamaño máximo de 5 MB."
    return True, ""


def validar_matricula(matricula):
    """Valida formato de matrícula (letras, números, guión)."""
    if not matricula or str(matricula).strip() == "":
        return False, "Matrícula es obligatoria."
    patron = r'^[A-Za-z0-9\-]{3,30}$'
    if re.match(patron, str(matricula).strip()):
        return True, ""
    return False, "Matrícula solo puede contener letras, números y guiones (3-30 caracteres)."


def validar_dni(dni):
    """Valida formato de DNI/documento."""
    if not dni or str(dni).strip() == "":
        return False, "DNI/Documento es obligatorio."
    patron = r'^[A-Za-z0-9]{5,20}$'
    if re.match(patron, str(dni).strip()):
        return True, ""
    return False, "DNI debe contener solo letras y números (5-20 caracteres)."


def parsear_fecha(fecha_str):
    """Convierte una fecha de varios formatos a objeto datetime."""
    formatos = ['%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y']
    for fmt in formatos:
        try:
            return datetime.strptime(str(fecha_str).strip(), fmt)
        except ValueError:
            continue
    return None


def fecha_a_mysql(fecha_str):
    """Convierte fecha de interfaz a formato MySQL YYYY-MM-DD."""
    dt = parsear_fecha(fecha_str)
    if dt:
        return dt.strftime('%Y-%m-%d')
    return fecha_str
