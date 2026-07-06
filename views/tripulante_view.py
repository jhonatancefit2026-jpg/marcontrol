"""
Vista de Tripulantes — Módulo 2
CRUD completo con imagen, tkcalendar, certificados, exportación
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

from views.base_view import ThemeManager, BotonAccion
from controllers.tripulante_controller import TripulanteController


class VistaTripulantes(tk.Frame):
    def __init__(self, parent):
        tema = ThemeManager.get_theme()
        super().__init__(parent, bg=tema['bg'])
        self.controller = TripulanteController(self)
        self._construir_ui()
        self.controller.cargar_tabla()
        ThemeManager.subscribe(self._aplicar_tema)

    def _construir_ui(self):
        tema = ThemeManager.get_theme()

        # Header
        hdr = tk.Frame(self, bg=tema['header_bg'], height=60)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="👥  Gestión de Tripulantes",
                 font=("Calibri", 16, "bold"),
                 bg=tema['header_bg'], fg=tema['header_fg']).pack(side="left", padx=20, pady=12)

        # Toolbar
        toolbar = tk.Frame(self, bg=tema['bg'], pady=8)
        toolbar.pack(fill="x", padx=16)

        BotonAccion(toolbar, "➕ Nuevo",     self._nuevo,      tipo='primary').pack(side="left", padx=4)
        BotonAccion(toolbar, "✏️ Editar",    self._editar,     tipo='warning').pack(side="left", padx=4)
        BotonAccion(toolbar, "🗑️ Eliminar",  self._eliminar,   tipo='danger').pack(side="left", padx=4)
        BotonAccion(toolbar, "📋 Certifs.",  self._ver_certs,  tipo='neutral').pack(side="left", padx=4)
        BotonAccion(toolbar, "📊 Excel",     self.controller.exportar_excel, tipo='success').pack(side="left", padx=4)
        BotonAccion(toolbar, "📄 PDF",       self.controller.exportar_pdf,   tipo='neutral').pack(side="left", padx=4)

        # Búsqueda
        tk.Label(toolbar, text="🔍", bg=tema['bg'], fg=tema['fg'],
                 font=("Calibri", 12)).pack(side="right", padx=(0, 4))
        self.var_buscar = tk.StringVar()
        self.var_buscar.trace("w", lambda *a: self._filtrar())
        tk.Entry(toolbar, textvariable=self.var_buscar, width=22,
                 font=("Calibri", 10), bg=tema['input_bg'], fg=tema['fg'],
                 relief="solid", bd=1, insertbackground=tema['fg']).pack(side="right", padx=4)
        tk.Label(toolbar, text="Buscar:", bg=tema['bg'], fg=tema['label_fg'],
                 font=("Calibri", 10)).pack(side="right")

        # Tabla
        frm_tabla = tk.Frame(self, bg=tema['bg'])
        frm_tabla.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        cols = ("id", "dni", "nombres", "apellidos", "cargo",
                "exp", "libreta", "telefono", "fnac", "salud", "disp")
        self.tree = ttk.Treeview(frm_tabla, columns=cols,
                                  show="headings", selectmode="browse")

        cabeceras = [("id","ID",45),("dni","DNI",90),("nombres","Nombres",100),
                     ("apellidos","Apellidos",110),("cargo","Cargo",100),
                     ("exp","Exp.(años)",80),("libreta","Libreta",90),
                     ("telefono","Teléfono",110),("fnac","F. Nacim.",100),
                     ("salud","Est. Salud",90),("disp","Disp.",55)]
        for col, cab, w in cabeceras:
            self.tree.heading(col, text=cab,
                               command=lambda c=col: self._ordenar(c))
            self.tree.column(col, width=w, anchor="center")

        sb_v = ttk.Scrollbar(frm_tabla, orient="vertical",   command=self.tree.yview)
        sb_h = ttk.Scrollbar(frm_tabla, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=sb_v.set, xscrollcommand=sb_h.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        sb_v.grid(row=0, column=1, sticky="ns")
        sb_h.grid(row=1, column=0, sticky="ew")
        frm_tabla.grid_rowconfigure(0, weight=1)
        frm_tabla.grid_columnconfigure(0, weight=1)
        self.tree.bind("<Double-1>", lambda e: self._editar())

        self.tree.tag_configure("par",   background=tema['table_bg'])
        self.tree.tag_configure("impar", background=tema['table_alt'])
        self._orden_col = None
        self._orden_asc = True

        self.lbl_estado = tk.Label(self, text="Cargando...",
                                    font=("Calibri", 9),
                                    bg=tema['bg'], fg=tema['label_fg'], anchor="w")
        self.lbl_estado.pack(fill="x", padx=16, pady=(0, 8))

    # ── ACCIONES ──────────────────────────────────────────────────

    def _nuevo(self):
        self.controller.nuevo()

    def _editar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Seleccione un tripulante.")
            return
        tid = self.tree.item(sel[0])['values'][0]
        self.controller.editar(tid)

    def _eliminar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Seleccione un tripulante.")
            return
        tid = self.tree.item(sel[0])['values'][0]
        self.controller.eliminar(tid)

    def _ver_certs(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Seleccione un tripulante.")
            return
        tid = self.tree.item(sel[0])['values'][0]
        self.controller.ver_certificados(tid)

    def _filtrar(self):
        texto = self.var_buscar.get().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)
        filas = [f for f in self._todas_filas
                 if any(texto in str(v).lower() for v in f)]
        self._poblar_tree(filas)

    def _ordenar(self, col):
        if self._orden_col == col:
            self._orden_asc = not self._orden_asc
        else:
            self._orden_col = col
            self._orden_asc = True
        idx = self.tree["columns"].index(col)
        filas = sorted(self._todas_filas,
                       key=lambda f: str(f[idx]).lower(),
                       reverse=not self._orden_asc)
        self._poblar_tree(filas)

    def mostrar_en_tabla(self, filas):
        self._todas_filas = filas
        self._poblar_tree(filas)
        self.lbl_estado.config(text=f"{len(filas)} tripulantes registrados")

    def _poblar_tree(self, filas):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, fila in enumerate(filas):
            tag = "par" if i % 2 == 0 else "impar"
            self.tree.insert("", "end", values=fila, tags=(tag,))

    def mostrar_certificados(self, certs):
        tema = ThemeManager.get_theme()
        v = tk.Toplevel(self)
        v.title("Certificados del Tripulante")
        v.geometry("560x380")
        v.grab_set()
        v.config(bg=tema['bg'])

        tk.Label(v, text="📋  Certificados y Habilitaciones",
                 font=("Calibri", 13, "bold"),
                 bg=tema['header_bg'], fg=tema['header_fg']).pack(fill="x", padx=0, pady=0, ipadx=12, ipady=10)

        cols = ("codigo", "descripcion", "emision", "vencimiento")
        tree = ttk.Treeview(v, columns=cols, show="headings")
        for col, cab, w in [("codigo","Código",80),("descripcion","Descripción",200),
                              ("emision","Emisión",100),("vencimiento","Vencimiento",100)]:
            tree.heading(col, text=cab)
            tree.column(col, width=w, anchor="center")
        for c in certs:
            tree.insert("", "end", values=(c['codigo'], c['descripcion'],
                                            str(c.get('fecha_emision', '') or ''),
                                            str(c.get('fecha_vencimiento', '') or '')))
        tree.pack(fill="both", expand=True, padx=16, pady=12)
        if not certs:
            tk.Label(v, text="No hay certificados registrados.",
                     bg=tema['bg'], fg=tema['label_fg'],
                     font=("Calibri", 10, "italic")).pack()
        tk.Button(v, text="Cerrar", bg=tema['btn_bg'], fg="white",
                  relief="flat", font=("Calibri", 10),
                  command=v.destroy, padx=16, pady=6).pack(pady=8)

    # ── FORMULARIO ────────────────────────────────────────────────

    def abrir_formulario(self, modo, datos=None):
        tema = ThemeManager.get_theme()
        v = tk.Toplevel(self)
        v.title("Nuevo Tripulante" if modo == 'nuevo' else "Editar Tripulante")
        v.geometry("740x650")
        v.grab_set()
        v.config(bg=tema['bg'])
        try:
            v.iconbitmap("assets/favicon.ico")
        except Exception:
            pass

        hdr = tk.Frame(v, bg=tema['header_bg'], height=50)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text=f"👥  {'Nuevo' if modo=='nuevo' else 'Editar'} Tripulante",
                 font=("Calibri", 13, "bold"),
                 bg=tema['header_bg'], fg=tema['header_fg']).pack(side="left", padx=16, pady=10)

        canvas = tk.Canvas(v, bg=tema['bg'], highlightthickness=0)
        sb = ttk.Scrollbar(v, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)

        frm = tk.Frame(canvas, bg=tema['bg'], padx=20, pady=12)
        wid = canvas.create_window((0, 0), window=frm, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(wid, width=e.width))
        frm.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))

        vars_form = {}

        def campo(parent, etq, key, row, col, tipo='entry',
                  opciones=None, colspan=1, requerido=False):
            tk.Label(parent, text=f"{etq}{'*' if requerido else ''}:",
                     font=("Calibri", 9, "bold"), bg=tema['bg'],
                     fg=tema['label_fg'], anchor="w").grid(
                row=row*2, column=col, sticky="w", padx=8, pady=(8, 0),
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
                                        date_pattern='yyyy-mm-dd',
                                        font=("Calibri", 10),
                                        background=tema['primary'],
                                        foreground='white', borderwidth=1)
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

        for c in range(3):
            frm.grid_columnconfigure(c, weight=1)

        campo(frm, "DNI / Documento",     "dni",              0, 0, requerido=True)
        campo(frm, "Nombres",             "nombres",          0, 1, requerido=True)
        campo(frm, "Apellidos",           "apellidos",        0, 2, requerido=True)
        campo(frm, "Cargo",               "cargo",            1, 0, tipo='combo',
              opciones=['Capitán', 'Primer Oficial', 'Jefe de Máquinas',
                         'Marinero', 'Marinera', 'Cocinero', 'Otro'])
        campo(frm, "Experiencia (años)",  "experiencia_anios", 1, 1)
        campo(frm, "Libreta Embarque",    "libreta_embarque", 1, 2)
        campo(frm, "Teléfono",            "telefono",         2, 0)
        campo(frm, "F. Nacimiento",       "fecha_nacimiento", 2, 1, tipo='calendar')
        campo(frm, "Estado de salud",     "estado_salud",     2, 2, tipo='combo',
              opciones=['Bueno', 'Regular', 'Requiere atención'])
        campo(frm, "Dirección",           "direccion",        3, 0, colspan=2)
        campo(frm, "Disponible",          "disponible",       3, 2, tipo='combo',
              opciones=['1', '0'])

        # Imagen
        sep = tk.Frame(frm, bg=tema['border'], height=1)
        sep.grid(row=8, column=0, columnspan=3, sticky="ew", padx=8, pady=(12, 6))
        tk.Label(frm, text="📷  Foto del tripulante",
                 font=("Calibri", 10, "bold"),
                 bg=tema['bg'], fg=tema['fg']).grid(row=9, column=0, sticky="w", padx=8)

        self._foto_trip_var = tk.StringVar()
        vars_form['foto_ruta'] = self._foto_trip_var

        frm_img = tk.Frame(frm, bg=tema['frame_bg'], relief="solid", bd=1)
        frm_img.grid(row=10, column=0, columnspan=3, padx=8, pady=4, sticky="ew")

        lbl_preview = tk.Label(frm_img, bg=tema['frame_bg'],
                                text="Sin foto", font=("Calibri", 9),
                                fg=tema['label_fg'], width=15, height=5)
        lbl_preview.pack(side="left", padx=10, pady=8)

        frm_img_c = tk.Frame(frm_img, bg=tema['frame_bg'])
        frm_img_c.pack(side="left", padx=8)
        tk.Label(frm_img_c, textvariable=self._foto_trip_var,
                 font=("Calibri", 8), bg=tema['frame_bg'],
                 fg=tema['label_fg'], wraplength=280).pack(anchor="w")

        def sel_img():
            ruta = filedialog.askopenfilename(
                title="Seleccionar foto",
                filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.gif"), ("Todos", "*.*")])
            if ruta:
                try:
                    img = Image.open(ruta)
                    img.thumbnail((100, 80), Image.LANCZOS)
                    foto_tk = ImageTk.PhotoImage(img)
                    lbl_preview.config(image=foto_tk, text="")
                    lbl_preview._img = foto_tk
                    self._foto_trip_var.set(ruta)
                except Exception as ex:
                    messagebox.showerror("Error", f"No se pudo cargar la imagen:\n{ex}")

        tk.Button(frm_img_c, text="📁 Seleccionar",
                  bg=tema['primary'], fg="white",
                  font=("Calibri", 9), relief="flat",
                  cursor="hand2", command=sel_img).pack(anchor="w", pady=3)
        tk.Button(frm_img_c, text="✖ Quitar",
                  bg=tema['btn_danger'], fg="white",
                  font=("Calibri", 9), relief="flat", cursor="hand2",
                  command=lambda: [self._foto_trip_var.set(""),
                                   lbl_preview.config(image="", text="Sin foto")]).pack(anchor="w")

        # Rellenar en edición
        if datos:
            map_keys = ['dni', 'nombres', 'apellidos', 'cargo', 'experiencia_anios',
                        'libreta_embarque', 'telefono', 'fecha_nacimiento',
                        'estado_salud', 'direccion', 'disponible']
            for k in map_keys:
                if k in vars_form and datos.get(k) is not None:
                    vars_form[k].set(str(datos[k]))
            if datos.get('foto_ruta'):
                self._foto_trip_var.set(datos['foto_ruta'])
                try:
                    img = Image.open(datos['foto_ruta'])
                    img.thumbnail((100, 80), Image.LANCZOS)
                    ft = ImageTk.PhotoImage(img)
                    lbl_preview.config(image=ft, text="")
                    lbl_preview._img = ft
                except Exception:
                    pass

        # Botones
        frm_btns = tk.Frame(v, bg=tema['bg'], pady=10)
        frm_btns.pack(fill="x")

        def guardar():
            form_datos = {k: val.get() for k, val in vars_form.items()}
            form_datos['foto_ruta'] = self._foto_trip_var.get()
            ok = self.controller.guardar(form_datos, modo,
                                          tripulante_id=datos['id'] if datos else None)
            if ok:
                v.destroy()

        tk.Button(frm_btns, text="💾  Guardar",
                  font=("Calibri", 11, "bold"),
                  bg=tema['btn_bg'], fg="white",
                  relief="flat", cursor="hand2",
                  padx=20, pady=8, command=guardar).pack(side="left", padx=16)
        tk.Button(frm_btns, text="✖  Cancelar",
                  font=("Calibri", 11),
                  bg=tema['border'], fg=tema['fg'],
                  relief="flat", cursor="hand2",
                  padx=20, pady=8, command=v.destroy).pack(side="left")
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
