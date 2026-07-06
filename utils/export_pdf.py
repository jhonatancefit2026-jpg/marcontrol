"""
Exportación a PDF usando ReportLab
Formato profesional para MarControl
"""
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle, Paragraph,
                                 Spacer, HRFlowable)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import KeepTogether
from datetime import datetime
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox

# Paleta de colores corporativa
AZUL_PRIMARIO  = colors.HexColor('#1A56DB')
AZUL_OSCURO    = colors.HexColor('#1A3BBB')
GRIS_CABECERA  = colors.HexColor('#2D3748')
GRIS_CLARO     = colors.HexColor('#F7FAFC')
GRIS_ALT       = colors.HexColor('#EBF4FF')
NEGRO          = colors.HexColor('#1A202C')
BLANCO         = colors.white
BORDE          = colors.HexColor('#CBD5E0')


def _estilos():
    sts = getSampleStyleSheet()

    titulo = ParagraphStyle(
        'Titulo',
        parent=sts['Heading1'],
        fontSize=20,
        fontName='Helvetica-Bold',
        textColor=BLANCO,
        alignment=TA_CENTER,
        spaceAfter=4,
        spaceBefore=0,
    )
    subtitulo = ParagraphStyle(
        'Subtitulo',
        parent=sts['Normal'],
        fontSize=9,
        fontName='Helvetica',
        textColor=colors.HexColor('#4A5568'),
        alignment=TA_CENTER,
        spaceAfter=12,
    )
    normal = ParagraphStyle(
        'NormalMC',
        parent=sts['Normal'],
        fontSize=9,
        fontName='Helvetica',
        textColor=NEGRO,
    )
    pie = ParagraphStyle(
        'Pie',
        parent=sts['Normal'],
        fontSize=8,
        fontName='Helvetica-Oblique',
        textColor=colors.HexColor('#718096'),
        alignment=TA_CENTER,
    )
    return {'titulo': titulo, 'subtitulo': subtitulo, 'normal': normal, 'pie': pie}


def exportar_a_pdf(titulo, columnas, datos, filtro_info=None, nombre_sugerido=None,
                   orientacion='portrait'):
    """
    Genera un PDF profesional con los datos proporcionados.

    :param titulo: Título del reporte
    :param columnas: Lista de nombres de columnas
    :param datos: Lista de listas con los datos
    :param filtro_info: Texto del filtro aplicado
    :param nombre_sugerido: Nombre sugerido para guardar
    :param orientacion: 'portrait' o 'landscape'
    """
    ruta = filedialog.asksaveasfilename(
        title="Guardar como PDF",
        defaultextension=".pdf",
        filetypes=[("PDF", "*.pdf"), ("Todos", "*.*")],
        initialfile=nombre_sugerido or f"{titulo.replace(' ', '_')}.pdf"
    )
    if not ruta:
        return False

    try:
        tamano = landscape(letter) if orientacion == 'landscape' else letter
        doc = SimpleDocTemplate(
            ruta,
            pagesize=tamano,
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        estilos = _estilos()
        elementos = []

        # ── BANNER TÍTULO ─────────────────────────────────────────
        # Tabla de una celda como banner azul
        banner_data = [[Paragraph(f"MarControl — {titulo}", estilos['titulo'])]]
        banner = Table(banner_data, colWidths=[doc.width])
        banner.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), AZUL_PRIMARIO),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('ROUNDEDCORNERS', [6, 6, 0, 0]),
        ]))
        elementos.append(banner)

        # ── SUBTÍTULO ─────────────────────────────────────────────
        fecha_gen = datetime.now().strftime("%d/%m/%Y  %H:%M")
        texto_sub = f"Generado: {fecha_gen}"
        if filtro_info:
            texto_sub += f"   |   Filtro aplicado: {filtro_info}"
        texto_sub += f"   |   Total: {len(datos)} registros"

        sub_data = [[Paragraph(texto_sub, estilos['subtitulo'])]]
        sub_tabla = Table(sub_data, colWidths=[doc.width])
        sub_tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), GRIS_ALT),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elementos.append(sub_tabla)
        elementos.append(Spacer(1, 0.3 * cm))

        # ── TABLA DE DATOS ────────────────────────────────────────
        n_cols = len(columnas)
        ancho_col = doc.width / n_cols

        # Cabecera
        cabecera = [Paragraph(f"<b>{c.upper()}</b>",
                               ParagraphStyle('ch', fontSize=8, fontName='Helvetica-Bold',
                                              textColor=BLANCO, alignment=TA_CENTER))
                    for c in columnas]

        tabla_datos = [cabecera]
        for fila in datos:
            fila_formateada = [
                Paragraph(str(v) if v is not None else "",
                          ParagraphStyle('td', fontSize=8, fontName='Helvetica',
                                         textColor=NEGRO, alignment=TA_LEFT))
                for v in fila
            ]
            tabla_datos.append(fila_formateada)

        # Estilo alternado
        estilo_tabla = TableStyle([
            # Cabecera
            ('BACKGROUND', (0, 0), (-1, 0), GRIS_CABECERA),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [BLANCO, GRIS_CLARO]),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDE),
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, AZUL_PRIMARIO),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])

        tabla = Table(tabla_datos, colWidths=[ancho_col] * n_cols, repeatRows=1)
        tabla.setStyle(estilo_tabla)
        elementos.append(tabla)

        # ── PIE DE PÁGINA ─────────────────────────────────────────
        elementos.append(Spacer(1, 0.4 * cm))
        elementos.append(HRFlowable(width="100%", thickness=1, color=BORDE))
        elementos.append(Spacer(1, 0.2 * cm))
        pie_txt = "MarControl v1.0 — Sistema de Control Pesquero — Documento generado automáticamente"
        elementos.append(Paragraph(pie_txt, estilos['pie']))

        # ── GENERAR PDF ───────────────────────────────────────────
        def _numero_pagina(canvas, document):
            canvas.saveState()
            canvas.setFont('Helvetica', 8)
            canvas.setFillColor(colors.HexColor('#718096'))
            texto = f"Página {document.page}"
            canvas.drawRightString(tamano[0] - 1.5 * cm, 1 * cm, texto)
            canvas.restoreState()

        doc.build(elementos, onFirstPage=_numero_pagina, onLaterPages=_numero_pagina)

        messagebox.showinfo("PDF generado",
                            f"Archivo guardado:\n{ruta}\n\n{len(datos)} registros exportados.")
        return True

    except Exception as e:
        messagebox.showerror("Error al exportar PDF", f"No se pudo generar el PDF:\n{e}")
        return False


def exportar_pdf_filtrado(titulo, columnas, datos_completos, campo_fecha_idx=None,
                          campo_categoria_idx=None, nombre_sugerido=None, orientacion='portrait'):
    """Igual que exportar_filtrado de Excel pero para PDF."""
    from tkinter import Toplevel, Label, Entry, Button, StringVar, Frame, ttk

    ventana = Toplevel()
    ventana.title("Filtros de exportación PDF")
    ventana.geometry("400x300")
    ventana.grab_set()
    ventana.resizable(False, False)

    resultado = {'datos': datos_completos, 'filtro': None}

    Label(ventana, text="Filtros de exportación PDF",
          font=("Calibri", 14, "bold")).pack(pady=10)

    frame = Frame(ventana, padx=20)
    frame.pack(fill="x")

    var_desde = StringVar()
    var_hasta = StringVar()
    var_cat = StringVar()

    if campo_fecha_idx is not None:
        Label(frame, text="Fecha desde (DD/MM/YYYY):").grid(row=0, column=0, sticky="w", pady=4)
        Entry(frame, textvariable=var_desde, width=20).grid(row=0, column=1, padx=5)
        Label(frame, text="Fecha hasta (DD/MM/YYYY):").grid(row=1, column=0, sticky="w", pady=4)
        Entry(frame, textvariable=var_hasta, width=20).grid(row=1, column=1, padx=5)

    if campo_categoria_idx is not None:
        categorias = sorted(set(str(f[campo_categoria_idx]) for f in datos_completos if f[campo_categoria_idx]))
        Label(frame, text="Categoría:").grid(row=2, column=0, sticky="w", pady=4)
        combo = ttk.Combobox(frame, textvariable=var_cat, values=["Todas"] + categorias, width=18)
        combo.set("Todas")
        combo.grid(row=2, column=1, padx=5)

    def aplicar():
        datos_filtrados = list(datos_completos)
        info_filtro = []
        if campo_fecha_idx is not None:
            from utils.validators import parsear_fecha
            desde = var_desde.get().strip()
            hasta = var_hasta.get().strip()
            if desde:
                d_desde = parsear_fecha(desde)
                if d_desde:
                    datos_filtrados = [f for f in datos_filtrados
                                       if parsear_fecha(str(f[campo_fecha_idx])) and
                                       parsear_fecha(str(f[campo_fecha_idx])) >= d_desde]
                    info_filtro.append(f"Desde {desde}")
            if hasta:
                d_hasta = parsear_fecha(hasta)
                if d_hasta:
                    datos_filtrados = [f for f in datos_filtrados
                                       if parsear_fecha(str(f[campo_fecha_idx])) and
                                       parsear_fecha(str(f[campo_fecha_idx])) <= d_hasta]
                    info_filtro.append(f"Hasta {hasta}")
        if campo_categoria_idx is not None:
            cat = var_cat.get()
            if cat and cat != "Todas":
                datos_filtrados = [f for f in datos_filtrados
                                   if str(f[campo_categoria_idx]) == cat]
                info_filtro.append(f"Categoría: {cat}")
        resultado['datos'] = datos_filtrados
        resultado['filtro'] = " | ".join(info_filtro) if info_filtro else None
        ventana.destroy()

    def sin_filtro():
        ventana.destroy()

    frame_btn = Frame(ventana)
    frame_btn.pack(pady=20)
    Button(frame_btn, text="Aplicar filtro", command=aplicar,
           bg="#1A56DB", fg="white", width=14).pack(side="left", padx=5)
    Button(frame_btn, text="Sin filtro", command=sin_filtro,
           bg="#4A5568", fg="white", width=14).pack(side="left", padx=5)

    ventana.wait_window()
    exportar_a_pdf(titulo, columnas, resultado['datos'],
                   filtro_info=resultado['filtro'],
                   nombre_sugerido=nombre_sugerido,
                   orientacion=orientacion)
