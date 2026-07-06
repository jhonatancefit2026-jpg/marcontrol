"""
Vista de Embarcaciones — Módulo 1
CRUD completo con: tkcalendar, Pillow, validación, 2 temas, exportación
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os

from views.base_view import ThemeManager, estilo_ttk, BotonAccion
from controllers.embarcacion_controller import EmbarcacionController


class VistaEmbarcaciones(tk.Frame):
    def __init__(self, parent):
        tema = ThemeManager.get_theme()
        super().__init__(parent, bg=tema['bg'])
        self.controller = EmbarcacionController(self)
        self._construir_ui()
        self.controller.cargar_tabla()
        ThemeManager.subscribe(self._aplicar_tema)

    def _construir_ui(self):
        tema = ThemeManager.get_theme()

        # ── HEADER ────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=tema['header_bg'], height=60)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="⛵  Gestión de Embarcaciones",
                 font=("Calibri", 16, "bold"),
                 bg=tema['header_bg'], fg=tema['header_fg']).pack(side="left", padx=20, pady=12)

        # ── BARRA DE HERRAMIENTAS ──────────────────────────────────
        toolbar = tk.Frame(self, bg=tema['bg'], pady=8)
        toolbar.pack(fill="x", padx=16)

        self.btn_nuevo    = BotonAccion(toolbar, "➕ Nueva", self._nuevo, tipo='primary')
        self.btn_editar   = BotonAccion(toolbar, "✏️ Editar", self._editar, tipo='warning')
        self.btn_eliminar = BotonAccion(toolbar, "🗑️ Eliminar", self._eliminar, tipo='danger')
        self.btn_excel    = BotonAccion(toolbar, "📊 Excel", self.controller.exportar_excel, tipo='success')
        self.btn_pdf      = BotonAccion(toolbar, "📄 PDF", self.controller.exportar_pdf, tipo='neutral')

        for btn in (self.btn_nuevo, self.btn_editar, self.btn_eliminar,
                    self.btn_excel, self.btn_pdf):
            btn.pack(side="left", padx=4)

        # Búsqueda
        tk.Label(toolbar, text="🔍", bg=tema['bg'], fg=tema['fg'],
                 font=("Calibri", 12)).pack(side="right", padx=(0, 4))
        self.var_buscar = tk.StringVar()
        self.var_buscar.trace("w", lambda *a: self._filtrar())
        self.ent_buscar = tk.Entry(toolbar, textvariable=self.var_buscar,
                                    width=22, font=("Calibri", 10),
                                    bg=tema['input_bg'], fg=tema['fg'],
                                    relief="solid", bd=1,
                                    insertbackground=tema['fg'])
        self.ent_buscar.pack(side="right", padx=4)
        tk.Label(toolbar, text="Buscar:", bg=tema['bg'], fg=tema['label_fg'],
                 font=("Calibri", 10)).pack(side="right")

        # ── TABLA ─────────────────────────────────────────────────
        frm_tabla = tk.Frame(self, bg=tema['bg'])
        frm_tabla.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        columnas = ("id", "matricula", "nombre", "tipo", "ano",
                    "material", "eslora", "capacidad", "potencia", "estado", "inspeccion")
        self.tree = ttk.Treeview(frm_tabla, columns=columnas,
                                  show="headings", selectmode="browse")

        cabeceras = [("id", "ID", 50), ("matricula", "Matrícula", 90),
                     ("nombre", "Nombre", 130), ("tipo", "Tipo", 100),
                     ("ano", "Año", 55), ("material", "Material", 80),
                     ("eslora", "Eslora(m)", 75), ("capacidad", "Capac.(tn)", 80),
                     ("potencia", "Pot.(kw)", 70), ("estado", "Estado", 90),
                     ("inspeccion", "Últ. Inspección", 120)]

        for col, encabezado, ancho in cabeceras:
            self.tree.heading(col, text=encabezado,
                               command=lambda c=col: self._ordenar(c))
            self.tree.column(col, width=ancho, anchor="center")

        sb_v = ttk.Scrollbar(frm_tabla, orient="vertical", command=self.tree.yview)
        sb_h = ttk.Scrollbar(frm_tabla, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=sb_v.set, xscrollcommand=sb_h.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        sb_v.grid(row=0, column=1, sticky="ns")
        sb_h.grid(row=1, column=0, sticky="ew")
        frm_tabla.grid_rowconfigure(0, weight=1)
        frm_tabla.grid_columnconfigure(0, weight=1)

        self.tree.bind("<Double-1>", lambda e: self._editar())

        # Alternar colores de filas
        self.tree.tag_configure("par", background=tema['table_bg'])
        self.tree.tag_configure("impar", background=tema['table_alt'])

        # Estado de ordenamiento
        self._orden_col = None
        self._orden_asc = True

        # Barra de estado
        self.lbl_estado = tk.Label(self, text="Cargando...",
                                    font=("Calibri", 9),
                                    bg=tema['bg'], fg=tema['label_fg'],
                                    anchor="w")
        self.lbl_estado.pack(fill="x", padx=16, pady=(0, 8))

    # ── ACCIONES ──────────────────────────────────────────────────

    def _nuevo(self):
        self.controller.nuevo()

    def _editar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Seleccione una embarcación.")
            return
        item = self.tree.item(sel[0])
        emb_id = item['values'][0]
        self.controller.editar(emb_id)

    def _eliminar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Seleccione una embarcación.")
            return
        item = self.tree.item(sel[0])
        emb_id = item['values'][0]
        self.controller.eliminar(emb_id)

    def _filtrar(self):
        texto = self.var_buscar.get().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)
        filas = [f for f in self._todas_filas
                 if any(texto in str(v).lower() for v in f)]
        self._poblar_tree(filas)

    def _ordenar(self, columna):
        if self._orden_col == columna:
            self._orden_asc = not self._orden_asc
        else:
            self._orden_col = columna
            self._orden_asc = True
        idx = self.tree["columns"].index(columna)
        filas = sorted(self._todas_filas,
                       key=lambda f: str(f[idx]).lower(),
                       reverse=not self._orden_asc)
        self._poblar_tree(filas)

    # ── DATOS ──────────────────────────────────────────────────────

    def mostrar_en_tabla(self, filas):
        self._todas_filas = filas
        self._poblar_tree(filas)
        self.lbl_estado.config(text=f"{len(filas)} embarcaciones registradas")

    def _poblar_tree(self, filas):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, fila in enumerate(filas):
            tag = "par" if i % 2 == 0 else "impar"
            self.tree.insert("", "end", values=fila, tags=(tag,))

    # ── FORMULARIO ────────────────────────────────────────────────

    def abrir_formulario(self, modo, datos=None):
        tema = ThemeManager.get_theme()
        ventana = tk.Toplevel(self)
        ventana.title("Nueva Embarcación" if modo == 'nuevo' else "Editar Embarcación")
        ventana.geometry("760x680")
        ventana.grab_set()
        ventana.resizable(True, True)
        ventana.config(bg=tema['bg'])

        try:
            ventana.iconbitmap("assets/favicon.ico")
        except Exception:
            pass

        # ── CABECERA DEL FORMULARIO ────────────────────────────────
        hdr = tk.Frame(ventana, bg=tema['header_bg'], height=50)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        titulo = "Nueva Embarcación" if modo == 'nuevo' else "Editar Embarcación"
        tk.Label(hdr, text=f"⛵  {titulo}", font=("Calibri", 13, "bold"),
                 bg=tema['header_bg'], fg=tema['header_fg']).pack(side="left", padx=16, pady=10)

        # Canvas + Scrollbar para el formulario
        canvas = tk.Canvas(ventana, bg=tema['bg'], highlightthickness=0)
        sb = ttk.Scrollbar(ventana, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        frm = tk.Frame(canvas, bg=tema['bg'], padx=24, pady=16)
        window_id = canvas.create_window((0, 0), window=frm, anchor="nw")

        def _on_resize(e):
            canvas.itemconfig(window_id, width=e.width)
        canvas.bind("<Configure>", _on_resize)
        frm.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))

        # ── GRID DE CAMPOS ─────────────────────────────────────────
        vars_form = {}

        def campo(parent, etq, key, row, col, tipo='entry', opciones=None,
                  colspan=1, requerido=False):
            lbl = tk.Label(parent, text=f"{etq}{'*' if requerido else ''}:",
                           font=("Calibri", 9, "bold"), bg=tema['bg'],
                           fg=tema['label_fg'], anchor="w")
            lbl.grid(row=row*2, column=col, sticky="w", padx=8, pady=(8, 0),
                     columnspan=colspan)

            var = tk.StringVar()
            vars_form[key] = var

            if tipo == 'combo':
                widget = ttk.Combobox(parent, textvariable=var,
                                       values=opciones, state="readonly",
                                       font=("Calibri", 10), width=22)
            elif tipo == 'calendar':
                try:
                    from tkcalendar import DateEntry
                    widget = DateEntry(parent, textvariable=var,
                                        font=("Calibri", 10),
                                        date_pattern='yyyy-mm-dd',
                                        background=tema['primary'],
                                        foreground='white',
                                        borderwidth=1)
                except ImportError:
                    widget = tk.Entry(parent, textvariable=var,
                                       font=("Calibri", 10),
                                       bg=tema['input_bg'], fg=tema['fg'],
                                       relief="solid", bd=1,
                                       insertbackground=tema['fg'])
            else:
                widget = tk.Entry(parent, textvariable=var,
                                   font=("Calibri", 10),
                                   bg=tema['input_bg'], fg=tema['fg'],
                                   relief="solid", bd=1, width=24,
                                   insertbackground=tema['fg'])

            widget.grid(row=row*2+1, column=col, sticky="ew",
                        padx=8, pady=(0, 4), columnspan=colspan)
            return var

        for c in range(3):
            frm.grid_columnconfigure(c, weight=1)

        # Fila 0
        campo(frm, "Matrícula",    "matricula",       0, 0, requerido=True)
        campo(frm, "Nombre",       "nombre",          0, 1, requerido=True)
        campo(frm, "Tipo",         "tipo",            0, 2, tipo='combo',
              opciones=['arrastrero', 'cerquero', 'palangrero', 'otro'])
        # Fila 1
        campo(frm, "Año construc.", "ano_construccion", 1, 0)
        campo(frm, "Material casco","material_casco",  1, 1)
        campo(frm, "Estado",       "estado",           1, 2, tipo='combo',
              opciones=['operativa', 'mantenimiento', 'baja'])
        # Fila 2
        campo(frm, "Eslora (m)",   "eslora",          2, 0)
        campo(frm, "Manga (m)",    "manga",           2, 1)
        campo(frm, "Calado (m)",   "calado",          2, 2)
        # Fila 3
        campo(frm, "Capacidad bodega (tn)", "capacidad_bodega_tn", 3, 0)
        campo(frm, "Potencia motor (kw)",   "potencia_motor_kw",   3, 1)
        campo(frm, "Velocidad max (kn)",    "velocidad_max_kn",    3, 2)
        # Fila 4
        campo(frm, "Autonomía (días)", "autonomia_dias", 4, 0)
        campo(frm, "Equipos navegación", "equipos_navegacion", 4, 1, colspan=2)
        # Fila 5 - Fecha con tkcalendar
        campo(frm, "Fecha última inspección", "fecha_ultima_inspeccion",
              5, 0, tipo='calendar')

        # ── SECCIÓN DE IMAGEN ──────────────────────────────────────
        sep = tk.Frame(frm, bg=tema['border'], height=1)
        sep.grid(row=12, column=0, columnspan=3, sticky="ew", padx=8, pady=(16, 8))

        tk.Label(frm, text="📷  Foto de la embarcación",
                 font=("Calibri", 10, "bold"), bg=tema['bg'],
                 fg=tema['fg']).grid(row=13, column=0, sticky="w", padx=8)

        self._foto_ruta_var = tk.StringVar()
        vars_form['foto_ruta'] = self._foto_ruta_var

        frm_img = tk.Frame(frm, bg=tema['frame_bg'], relief="solid", bd=1)
        frm_img.grid(row=14, column=0, columnspan=3, padx=8, pady=4, sticky="ew")

        self._lbl_img_preview = tk.Label(frm_img, bg=tema['frame_bg'],
                                          text="Sin imagen",
                                          font=("Calibri", 9),
                                          fg=tema['label_fg'],
                                          width=20, height=6)
        self._lbl_img_preview.pack(side="left", padx=12, pady=8)

        frm_img_ctrl = tk.Frame(frm_img, bg=tema['frame_bg'])
        frm_img_ctrl.pack(side="left", padx=8)

        lbl_ruta = tk.Label(frm_img_ctrl, textvariable=self._foto_ruta_var,
                             font=("Calibri", 8), bg=tema['frame_bg'],
                             fg=tema['label_fg'], wraplength=300)
        lbl_ruta.pack(anchor="w")

        def seleccionar_imagen():
            ruta = filedialog.askopenfilename(
                title="Seleccionar foto",
                filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.gif"),
                            ("Todos", "*.*")])
            if ruta:
                # Validar con Pillow
                try:
                    img = Image.open(ruta)
                    # Redimensionar para preview: máx 120x90
                    img.thumbnail((120, 90), Image.LANCZOS)
                    # Verificar formato soportado
                    if img.format not in ('JPEG', 'PNG', 'GIF', None):
                        messagebox.showwarning("Formato", "Use JPG, PNG o GIF.")
                        return
                    foto_tk = ImageTk.PhotoImage(img)
                    self._lbl_img_preview.config(image=foto_tk, text="")
                    self._lbl_img_preview._img = foto_tk  # evitar GC
                    self._foto_ruta_var.set(ruta)
                except Exception as ex:
                    messagebox.showerror("Error", f"No se pudo cargar la imagen:\n{ex}")

        def quitar_imagen():
            self._foto_ruta_var.set("")
            self._lbl_img_preview.config(image="", text="Sin imagen")
            self._lbl_img_preview._img = None

        tk.Button(frm_img_ctrl, text="📁 Seleccionar imagen",
                  font=("Calibri", 9), bg=tema['primary'], fg="white",
                  relief="flat", cursor="hand2",
                  command=seleccionar_imagen).pack(anchor="w", pady=4)
        tk.Button(frm_img_ctrl, text="✖ Quitar imagen",
                  font=("Calibri", 9), bg=tema['btn_danger'], fg="white",
                  relief="flat", cursor="hand2",
                  command=quitar_imagen).pack(anchor="w")

        # ── RELLENO DE DATOS EN EDICIÓN ────────────────────────────
        if datos:
            campos_map = {
                'matricula': 'matricula', 'nombre': 'nombre',
                'tipo': 'tipo', 'ano_construccion': 'ano_construccion',
                'material_casco': 'material_casco', 'estado': 'estado',
                'eslora': 'eslora', 'manga': 'manga', 'calado': 'calado',
                'capacidad_bodega_tn': 'capacidad_bodega_tn',
                'potencia_motor_kw': 'potencia_motor_kw',
                'velocidad_max_kn': 'velocidad_max_kn',
                'autonomia_dias': 'autonomia_dias',
                'equipos_navegacion': 'equipos_navegacion',
                'fecha_ultima_inspeccion': 'fecha_ultima_inspeccion',
            }
            for key, db_key in campos_map.items():
                if key in vars_form and datos.get(db_key) is not None:
                    vars_form[key].set(str(datos[db_key]))

            if datos.get('foto_ruta'):
                self._foto_ruta_var.set(datos['foto_ruta'])
                try:
                    img = Image.open(datos['foto_ruta'])
                    img.thumbnail((120, 90), Image.LANCZOS)
                    foto_tk = ImageTk.PhotoImage(img)
                    self._lbl_img_preview.config(image=foto_tk, text="")
                    self._lbl_img_preview._img = foto_tk
                except Exception:
                    pass

        # ── BOTONES ───────────────────────────────────────────────
        frm_btns = tk.Frame(ventana, bg=tema['bg'], pady=12)
        frm_btns.pack(fill="x")

        def guardar():
            form_datos = {k: v.get() for k, v in vars_form.items()}
            form_datos['foto_ruta'] = self._foto_ruta_var.get()
            exito = self.controller.guardar(
                form_datos, modo,
                embarcacion_id=datos['id'] if datos else None
            )
            if exito:
                ventana.destroy()

        tk.Button(frm_btns, text="💾  Guardar",
                  font=("Calibri", 11, "bold"),
                  bg=tema['btn_bg'], fg="white",
                  relief="flat", cursor="hand2",
                  padx=20, pady=8,
                  command=guardar).pack(side="left", padx=16)

        tk.Button(frm_btns, text="✖  Cancelar",
                  font=("Calibri", 11),
                  bg=tema['border'], fg=tema['fg'],
                  relief="flat", cursor="hand2",
                  padx=20, pady=8,
                  command=ventana.destroy).pack(side="left")

        # Nota campos obligatorios
        tk.Label(frm_btns, text="* Campos obligatorios",
                 font=("Calibri", 8, "italic"),
                 bg=tema['bg'], fg=tema['label_fg']).pack(side="right", padx=16)

    def _aplicar_tema(self):
        self.controller.cargar_tabla()

    def __del__(self):
        try:
            ThemeManager.unsubscribe(self._aplicar_tema)
        except Exception:
            pass
