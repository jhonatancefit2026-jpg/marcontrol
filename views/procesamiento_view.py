"""
Vista de Procesamiento — Módulo 4
CRUD, SP ProcesarLotePescado, preview de cantidad, tkcalendar, exportación
"""
import tkinter as tk
from tkinter import ttk, messagebox

from views.base_view import ThemeManager, BotonAccion
from controllers.procesamiento_controller import ProcesamientoController


class VistaProcesamiento(tk.Frame):
    def __init__(self, parent):
        tema = ThemeManager.get_theme()
        super().__init__(parent, bg=tema['bg'])
        self.controller = ProcesamientoController(self)
        self._construir_ui()
        self.controller.cargar_tabla()
        ThemeManager.subscribe(self._aplicar_tema)

    def _construir_ui(self):
        tema = ThemeManager.get_theme()

        hdr = tk.Frame(self, bg=tema['header_bg'], height=60)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="🏭  Procesamiento de Lotes",
                 font=("Calibri", 16, "bold"),
                 bg=tema['header_bg'], fg=tema['header_fg']).pack(side="left", padx=20, pady=12)

        tb = tk.Frame(self, bg=tema['bg'], pady=8)
        tb.pack(fill="x", padx=16)

        BotonAccion(tb, "➕ Nuevo Lote",  self._nuevo,      tipo='primary').pack(side="left", padx=4)
        BotonAccion(tb, "✏️ Editar",       self._editar,     tipo='warning').pack(side="left", padx=4)
        BotonAccion(tb, "🗑️ Eliminar",     self._eliminar,   tipo='danger').pack(side="left", padx=4)
        BotonAccion(tb, "📊 Excel",        self.controller.exportar_excel, tipo='success').pack(side="left", padx=4)
        BotonAccion(tb, "📄 PDF",          self.controller.exportar_pdf,   tipo='neutral').pack(side="left", padx=4)

        tk.Label(tb, text="🔍", bg=tema['bg'], fg=tema['fg'],
                 font=("Calibri", 12)).pack(side="right", padx=(0, 4))
        self.var_buscar = tk.StringVar()
        self.var_buscar.trace("w", lambda *a: self._filtrar())
        tk.Entry(tb, textvariable=self.var_buscar, width=22,
                 font=("Calibri", 10), bg=tema['input_bg'], fg=tema['fg'],
                 relief="solid", bd=1, insertbackground=tema['fg']).pack(side="right", padx=4)
        tk.Label(tb, text="Buscar:", bg=tema['bg'], fg=tema['label_fg'],
                 font=("Calibri", 10)).pack(side="right")

        # Tabla
        frm_t = tk.Frame(self, bg=tema['bg'])
        frm_t.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        cols = ("id","lote","captura","especie","fecha","metodo",
                "materia","rend","producto","cant","resp")
        self.tree = ttk.Treeview(frm_t, columns=cols, show="headings", selectmode="browse")

        cabs = [("id","ID",45),("lote","Lote",110),("captura","Captura",110),
                ("especie","Especie",90),("fecha","Fecha",100),
                ("metodo","Método",90),("materia","Mat.Prima(kg)",100),
                ("rend","Rend.%",65),("producto","Producto Final",120),
                ("cant","Cant.Prod(kg)",100),("resp","Responsable",100)]
        for col, cab, w in cabs:
            self.tree.heading(col, text=cab, command=lambda c=col: self._ordenar(c))
            self.tree.column(col, width=w, anchor="center")

        sb_v = ttk.Scrollbar(frm_t, orient="vertical",   command=self.tree.yview)
        sb_h = ttk.Scrollbar(frm_t, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=sb_v.set, xscrollcommand=sb_h.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        sb_v.grid(row=0, column=1, sticky="ns")
        sb_h.grid(row=1, column=0, sticky="ew")
        frm_t.grid_rowconfigure(0, weight=1)
        frm_t.grid_columnconfigure(0, weight=1)
        self.tree.bind("<Double-1>", lambda e: self._editar())
        self.tree.tag_configure("par",   background=tema['table_bg'])
        self.tree.tag_configure("impar", background=tema['table_alt'])
        self._orden_col = None
        self._orden_asc = True

        self.lbl_estado = tk.Label(self, text="Cargando...",
                                    font=("Calibri", 9), bg=tema['bg'],
                                    fg=tema['label_fg'], anchor="w")
        self.lbl_estado.pack(fill="x", padx=16, pady=(0, 8))

    def _nuevo(self):
        self.controller.nuevo()

    def _editar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Seleccione un lote.")
            return
        pid = self.tree.item(sel[0])['values'][0]
        self.controller.editar(pid)

    def _eliminar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Seleccione un lote.")
            return
        pid = self.tree.item(sel[0])['values'][0]
        self.controller.eliminar(pid)

    def _filtrar(self):
        texto = self.var_buscar.get().lower()
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
        self.lbl_estado.config(text=f"{len(filas)} lotes de procesamiento")

    def _poblar_tree(self, filas):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, f in enumerate(filas):
            self.tree.insert("", "end", values=f,
                              tags=("par" if i % 2 == 0 else "impar",))

    # ── FORMULARIO ────────────────────────────────────────────────

    def abrir_formulario(self, modo, datos=None, capturas=None,
                          especies=None, lote_sugerido=None):
        tema = ThemeManager.get_theme()
        v = tk.Toplevel(self)
        v.title("Nuevo Lote" if modo == 'nuevo' else "Editar Lote")
        v.geometry("660x580")
        v.grab_set()
        v.config(bg=tema['bg'])
        try:
            v.iconbitmap("assets/favicon.ico")
        except Exception:
            pass

        hdr = tk.Frame(v, bg=tema['header_bg'], height=50)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text=f"🏭  {'Nuevo Lote' if modo=='nuevo' else 'Editar Lote'}",
                 font=("Calibri", 13, "bold"),
                 bg=tema['header_bg'], fg=tema['header_fg']).pack(side="left", padx=16, pady=10)

        frm = tk.Frame(v, bg=tema['bg'], padx=24, pady=16)
        frm.pack(fill="both", expand=True)
        for c in range(2):
            frm.grid_columnconfigure(c, weight=1)

        vars_form = {}

        nota = tk.Label(frm,
                        text="ℹ️  Al crear, se llamará al SP 'ProcesarLotePescado'",
                        font=("Calibri", 9, "italic"),
                        bg=tema['secondary'], fg=tema['primary'],
                        padx=8, pady=4)
        nota.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        row_n = [1]  # Mutable row counter

        def campo(etq, key, col, tipo='entry', opciones=None,
                  colspan=1, requerido=False, readonly=False):
            r = row_n[0]
            tk.Label(frm, text=f"{etq}{'*' if requerido else ''}:",
                     font=("Calibri", 9, "bold"), bg=tema['bg'],
                     fg=tema['label_fg'], anchor="w").grid(
                row=r*2, column=col, sticky="w", padx=8, pady=(8, 0),
                columnspan=colspan)
            var = tk.StringVar()
            vars_form[key] = var

            if tipo == 'combo':
                widget = ttk.Combobox(frm, textvariable=var,
                                       values=opciones, state="readonly",
                                       font=("Calibri", 10))
            elif tipo == 'calendar':
                try:
                    from tkcalendar import DateEntry
                    widget = DateEntry(frm, textvariable=var,
                                        date_pattern='yyyy-mm-dd',
                                        font=("Calibri", 10),
                                        background=tema['primary'],
                                        foreground='white', borderwidth=1)
                except ImportError:
                    widget = tk.Entry(frm, textvariable=var,
                                       font=("Calibri", 10),
                                       bg=tema['input_bg'], fg=tema['fg'],
                                       relief="solid", bd=1,
                                       insertbackground=tema['fg'])
            else:
                state = 'readonly' if readonly else 'normal'
                widget = tk.Entry(frm, textvariable=var,
                                   font=("Calibri", 10),
                                   bg=tema['input_bg'] if not readonly else tema['secondary'],
                                   fg=tema['fg'],
                                   relief="solid", bd=1, width=26,
                                   state=state,
                                   insertbackground=tema['fg'])
            widget.grid(row=r*2+1, column=col, sticky="ew",
                        padx=8, pady=(0, 4), columnspan=colspan)
            return var, widget

        # Campos
        cap_nombres = [c['numero_registro'] for c in (capturas or [])]
        esp_nombres = [e['nombre'] for e in (especies or [])]

        r = row_n
        tk.Label(frm, text="Código de Lote*:", font=("Calibri", 9, "bold"),
                 bg=tema['bg'], fg=tema['label_fg'], anchor="w").grid(
            row=2, column=0, sticky="w", padx=8, pady=(8, 0))
        var_lote = tk.StringVar(value=lote_sugerido or "")
        vars_form['lote_codigo'] = var_lote
        tk.Entry(frm, textvariable=var_lote, font=("Calibri", 10),
                 bg=tema['input_bg'], fg=tema['fg'], relief="solid", bd=1,
                 insertbackground=tema['fg']).grid(
            row=3, column=0, sticky="ew", padx=8, pady=(0, 4))

        tk.Label(frm, text="Captura origen*:", font=("Calibri", 9, "bold"),
                 bg=tema['bg'], fg=tema['label_fg'], anchor="w").grid(
            row=2, column=1, sticky="w", padx=8, pady=(8, 0))
        var_cap_nom = tk.StringVar()
        var_cap_id  = tk.StringVar()
        vars_form['captura_id'] = var_cap_id
        combo_cap = ttk.Combobox(frm, textvariable=var_cap_nom,
                                   values=cap_nombres, state="readonly",
                                   font=("Calibri", 10))
        combo_cap.grid(row=3, column=1, sticky="ew", padx=8, pady=(0, 4))

        def on_cap(*a):
            nom = var_cap_nom.get()
            for c in (capturas or []):
                if c['numero_registro'] == nom:
                    var_cap_id.set(str(c['id']))
                    break
        var_cap_nom.trace("w", on_cap)

        # Especie
        tk.Label(frm, text="Especie:", font=("Calibri", 9, "bold"),
                 bg=tema['bg'], fg=tema['label_fg']).grid(
            row=4, column=0, sticky="w", padx=8, pady=(8, 0))
        var_esp_nom = tk.StringVar()
        var_esp_id  = tk.StringVar()
        vars_form['especie_id'] = var_esp_id
        combo_esp = ttk.Combobox(frm, textvariable=var_esp_nom,
                                   values=esp_nombres, state="readonly",
                                   font=("Calibri", 10))
        combo_esp.grid(row=5, column=0, sticky="ew", padx=8, pady=(0, 4))

        def on_esp(*a):
            nom = var_esp_nom.get()
            for e in (especies or []):
                if e['nombre'] == nom:
                    var_esp_id.set(str(e['id']))
                    break
        var_esp_nom.trace("w", on_esp)

        # Fecha
        tk.Label(frm, text="Fecha proceso*:", font=("Calibri", 9, "bold"),
                 bg=tema['bg'], fg=tema['label_fg']).grid(
            row=4, column=1, sticky="w", padx=8, pady=(8, 0))
        var_fecha = tk.StringVar()
        vars_form['fecha'] = var_fecha
        try:
            from tkcalendar import DateEntry
            cal = DateEntry(frm, textvariable=var_fecha,
                             date_pattern='yyyy-mm-dd',
                             font=("Calibri", 10),
                             background=tema['primary'],
                             foreground='white', borderwidth=1)
        except ImportError:
            cal = tk.Entry(frm, textvariable=var_fecha,
                            font=("Calibri", 10),
                            bg=tema['input_bg'], fg=tema['fg'],
                            relief="solid", bd=1,
                            insertbackground=tema['fg'])
        cal.grid(row=5, column=1, sticky="ew", padx=8, pady=(0, 4))

        # Materia prima y rendimiento
        tk.Label(frm, text="Materia prima (kg)*:", font=("Calibri", 9, "bold"),
                 bg=tema['bg'], fg=tema['label_fg']).grid(
            row=6, column=0, sticky="w", padx=8, pady=(8, 0))
        var_mp = tk.StringVar()
        vars_form['materia_prima_kg'] = var_mp
        tk.Entry(frm, textvariable=var_mp, font=("Calibri", 10),
                 bg=tema['input_bg'], fg=tema['fg'], relief="solid", bd=1,
                 insertbackground=tema['fg']).grid(
            row=7, column=0, sticky="ew", padx=8, pady=(0, 4))

        tk.Label(frm, text="Rendimiento (%) *:", font=("Calibri", 9, "bold"),
                 bg=tema['bg'], fg=tema['label_fg']).grid(
            row=6, column=1, sticky="w", padx=8, pady=(8, 0))
        var_rend = tk.StringVar()
        vars_form['rendimiento'] = var_rend
        tk.Entry(frm, textvariable=var_rend, font=("Calibri", 10),
                 bg=tema['input_bg'], fg=tema['fg'], relief="solid", bd=1,
                 insertbackground=tema['fg']).grid(
            row=7, column=1, sticky="ew", padx=8, pady=(0, 4))

        # Preview cantidad producida
        lbl_preview = tk.Label(frm, text="Cantidad estimada: — kg",
                                font=("Calibri", 10, "bold"),
                                bg=tema['secondary'], fg=tema['primary'],
                                padx=10, pady=6, relief="flat")
        lbl_preview.grid(row=8, column=0, columnspan=2, sticky="ew", padx=8, pady=(4, 8))

        def actualizar_preview(*a):
            try:
                cant = self.controller.calcular_cantidad_preview(
                    var_mp.get(), var_rend.get())
                lbl_preview.config(text=f"📦  Cantidad producida estimada: {cant:,.2f} kg")
            except Exception:
                lbl_preview.config(text="Cantidad estimada: ingrese materia prima y rendimiento")

        var_mp.trace("w", actualizar_preview)
        var_rend.trace("w", actualizar_preview)

        # Método y producto
        tk.Label(frm, text="Método*:", font=("Calibri", 9, "bold"),
                 bg=tema['bg'], fg=tema['label_fg']).grid(
            row=9, column=0, sticky="w", padx=8, pady=(8, 0))
        var_metodo = tk.StringVar()
        vars_form['metodo_procesamiento'] = var_metodo
        ttk.Combobox(frm, textvariable=var_metodo,
                      values=['congelado', 'enlatado', 'salado', 'otro'],
                      state="readonly", font=("Calibri", 10)).grid(
            row=10, column=0, sticky="ew", padx=8, pady=(0, 4))

        tk.Label(frm, text="Tipo producto final*:", font=("Calibri", 9, "bold"),
                 bg=tema['bg'], fg=tema['label_fg']).grid(
            row=9, column=1, sticky="w", padx=8, pady=(8, 0))
        var_prod = tk.StringVar()
        vars_form['tipo_producto_final'] = var_prod
        tk.Entry(frm, textvariable=var_prod, font=("Calibri", 10),
                 bg=tema['input_bg'], fg=tema['fg'], relief="solid", bd=1,
                 insertbackground=tema['fg']).grid(
            row=10, column=1, sticky="ew", padx=8, pady=(0, 4))

        tk.Label(frm, text="Responsable:", font=("Calibri", 9, "bold"),
                 bg=tema['bg'], fg=tema['label_fg']).grid(
            row=11, column=0, sticky="w", padx=8, pady=(8, 0))
        var_resp = tk.StringVar()
        vars_form['responsable'] = var_resp
        tk.Entry(frm, textvariable=var_resp, font=("Calibri", 10),
                 bg=tema['input_bg'], fg=tema['fg'], relief="solid", bd=1,
                 insertbackground=tema['fg']).grid(
            row=12, column=0, columnspan=2, sticky="ew", padx=8, pady=(0, 4))

        # Rellenar en edición
        if datos:
            map_k = {'lote_codigo': var_lote, 'fecha': var_fecha,
                     'materia_prima_kg': var_mp, 'rendimiento': var_rend,
                     'metodo_procesamiento': var_metodo,
                     'tipo_producto_final': var_prod, 'responsable': var_resp}
            for k, var in map_k.items():
                if datos.get(k) is not None:
                    var.set(str(datos[k]))
            if datos.get('captura_id'):
                var_cap_id.set(str(datos['captura_id']))
                for c in (capturas or []):
                    if c['id'] == datos['captura_id']:
                        var_cap_nom.set(c['numero_registro'])
                        break
            if datos.get('especie_id'):
                var_esp_id.set(str(datos['especie_id']))
                for e in (especies or []):
                    if e['id'] == datos['especie_id']:
                        var_esp_nom.set(e['nombre'])
                        break

        # Botones
        frm_btns = tk.Frame(v, bg=tema['bg'], pady=10)
        frm_btns.pack(fill="x")

        def guardar():
            form_datos = {k: val.get() for k, val in vars_form.items()}
            ok = self.controller.guardar(form_datos, modo,
                                          proc_id=datos['id'] if datos else None)
            if ok:
                v.destroy()

        tk.Button(frm_btns, text="💾  Guardar",
                  font=("Calibri", 11, "bold"),
                  bg=tema['btn_bg'], fg="white",
                  relief="flat", cursor="hand2",
                  padx=20, pady=8, command=guardar).pack(side="left", padx=16)
        tk.Button(frm_btns, text="✖  Cancelar",
                  font=("Calibri", 11), bg=tema['border'], fg=tema['fg'],
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
