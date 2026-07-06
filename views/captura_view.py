"""
Vista de Capturas — Módulo 3
CRUD completo, usa SP RegistrarCaptura, tkcalendar, exportación
"""
import tkinter as tk
from tkinter import ttk, messagebox

from views.base_view import ThemeManager, BotonAccion
from controllers.captura_controller import CapturaController


class VistaCapturas(tk.Frame):
    def __init__(self, parent):
        tema = ThemeManager.get_theme()
        super().__init__(parent, bg=tema['bg'])
        self.controller = CapturaController(self)
        self._construir_ui()
        self.controller.cargar_tabla()
        ThemeManager.subscribe(self._aplicar_tema)

    def _construir_ui(self):
        tema = ThemeManager.get_theme()

        # Header
        hdr = tk.Frame(self, bg=tema['header_bg'], height=60)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="🎣  Registro de Capturas",
                 font=("Calibri", 16, "bold"),
                 bg=tema['header_bg'], fg=tema['header_fg']).pack(side="left", padx=20, pady=12)

        # Toolbar
        tb = tk.Frame(self, bg=tema['bg'], pady=8)
        tb.pack(fill="x", padx=16)

        BotonAccion(tb, "➕ Nueva Captura",  self._nuevo,      tipo='primary').pack(side="left", padx=4)
        BotonAccion(tb, "✏️ Editar",         self._editar,     tipo='warning').pack(side="left", padx=4)
        BotonAccion(tb, "🗑️ Eliminar",       self._eliminar,   tipo='danger').pack(side="left", padx=4)
        BotonAccion(tb, "🔎 Ver detalle",    self._ver_detalle,tipo='neutral').pack(side="left", padx=4)
        BotonAccion(tb, "📊 Excel",          self.controller.exportar_excel, tipo='success').pack(side="left", padx=4)
        BotonAccion(tb, "📄 PDF",            self.controller.exportar_pdf,   tipo='neutral').pack(side="left", padx=4)

        # Búsqueda
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

        cols = ("id", "reg", "emb", "zona", "fi", "ff", "metodo", "especies", "total_kg", "cond")
        self.tree = ttk.Treeview(frm_t, columns=cols, show="headings", selectmode="browse")

        cabeceras = [("id","ID",45),("reg","N° Registro",120),("emb","Embarcación",110),
                     ("zona","Zona",100),("fi","Inicio",120),("ff","Fin",120),
                     ("metodo","Método",90),("especies","Especies",130),
                     ("total_kg","Total Kg",80),("cond","Condiciones",130)]
        for col, cab, w in cabeceras:
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
        self.tree.bind("<Double-1>", lambda e: self._ver_detalle())
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
            messagebox.showwarning("Sin selección", "Seleccione una captura.")
            return
        cid = self.tree.item(sel[0])['values'][0]
        self.controller.editar(cid)

    def _eliminar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Seleccione una captura.")
            return
        cid = self.tree.item(sel[0])['values'][0]
        self.controller.eliminar(cid)

    def _ver_detalle(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Sin selección", "Seleccione una captura.")
            return
        cid = self.tree.item(sel[0])['values'][0]
        self.controller.ver_detalle(cid)

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
        self.lbl_estado.config(text=f"{len(filas)} capturas registradas")

    def _poblar_tree(self, filas):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, f in enumerate(filas):
            self.tree.insert("", "end", values=f,
                              tags=("par" if i % 2 == 0 else "impar",))

    def mostrar_detalle(self, detalle, valor_total):
        tema = ThemeManager.get_theme()
        v = tk.Toplevel(self)
        v.title("Detalle de Captura")
        v.geometry("500x380")
        v.grab_set()
        v.config(bg=tema['bg'])

        tk.Label(v, text="🎣  Detalle de Captura",
                 font=("Calibri", 13, "bold"),
                 bg=tema['header_bg'], fg=tema['header_fg']).pack(fill="x", ipadx=12, ipady=10)

        cols = ("especie", "kg")
        tree = ttk.Treeview(v, columns=cols, show="headings", height=8)
        tree.heading("especie", text="Especie")
        tree.heading("kg", text="Cantidad (kg)")
        tree.column("especie", width=220)
        tree.column("kg", width=140, anchor="center")
        for d in detalle:
            tree.insert("", "end", values=(d['especie'], d['cantidad_kg']))
        tree.pack(fill="x", padx=16, pady=12)

        tk.Label(v, text=f"💰  Valor estimado de captura: ${valor_total:,.2f}",
                 font=("Calibri", 12, "bold"),
                 bg=tema['bg'], fg=tema['primary']).pack(pady=8)
        if not detalle:
            tk.Label(v, text="No hay detalle registrado.",
                     bg=tema['bg'], fg=tema['label_fg'],
                     font=("Calibri", 10, "italic")).pack()
        tk.Button(v, text="Cerrar", bg=tema['btn_bg'], fg="white",
                  relief="flat", font=("Calibri", 10),
                  command=v.destroy, padx=16, pady=6).pack(pady=8)

    # ── FORMULARIO ────────────────────────────────────────────────

    def abrir_formulario(self, modo, datos=None, zonas=None,
                          especies=None, embarcaciones=None):
        tema = ThemeManager.get_theme()
        v = tk.Toplevel(self)
        v.title("Nueva Captura" if modo == 'nuevo' else "Editar Captura")
        v.geometry("640x580")
        v.grab_set()
        v.config(bg=tema['bg'])
        try:
            v.iconbitmap("assets/favicon.ico")
        except Exception:
            pass

        hdr = tk.Frame(v, bg=tema['header_bg'], height=50)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text=f"🎣  {'Nueva' if modo=='nuevo' else 'Editar'} Captura",
                 font=("Calibri", 13, "bold"),
                 bg=tema['header_bg'], fg=tema['header_fg']).pack(side="left", padx=16, pady=10)

        frm = tk.Frame(v, bg=tema['bg'], padx=24, pady=16)
        frm.pack(fill="both", expand=True)

        for c in range(2):
            frm.grid_columnconfigure(c, weight=1)

        vars_form = {}

        # Nota SP
        nota = tk.Label(frm,
                        text="ℹ️  Al crear, se usará el Stored Procedure 'RegistrarCaptura'",
                        font=("Calibri", 9, "italic"),
                        bg=tema['secondary'], fg=tema['primary'],
                        padx=8, pady=4, relief="flat")
        nota.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))

        def campo(etq, key, row, col, tipo='entry',
                  opciones=None, ids=None, colspan=1, requerido=False):
            tk.Label(frm, text=f"{etq}{'*' if requerido else ''}:",
                     font=("Calibri", 9, "bold"), bg=tema['bg'],
                     fg=tema['label_fg'], anchor="w").grid(
                row=row*2+1, column=col, sticky="w", padx=8, pady=(8, 0),
                columnspan=colspan)
            var = tk.StringVar()
            vars_form[key] = var

            if tipo == 'combo_id':
                # Combo con clave=id, valor=nombre
                nombres = [str(o['nombre']) for o in (opciones or [])]
                widget = ttk.Combobox(frm, textvariable=var,
                                       values=nombres, state="readonly",
                                       font=("Calibri", 10))
                widget._opciones_ids = opciones or []
                vars_form[f"_ids_{key}"] = opciones or []
            elif tipo == 'combo':
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
                widget = tk.Entry(frm, textvariable=var,
                                   font=("Calibri", 10),
                                   bg=tema['input_bg'], fg=tema['fg'],
                                   relief="solid", bd=1, width=26,
                                   insertbackground=tema['fg'])
            widget.grid(row=row*2+2, column=col, sticky="ew",
                        padx=8, pady=(0, 4), columnspan=colspan)
            return var, widget

        # Combos con IDs
        emb_nombres  = [e['nombre'] for e in (embarcaciones or [])]
        zona_nombres = [z['nombre'] for z in (zonas or [])]
        esp_nombres  = [e['nombre'] for e in (especies or [])]

        var_emb, wid_emb = campo("Embarcación", "_emb_nombre", 0, 0,
                                   tipo='combo', opciones=emb_nombres, requerido=True)
        var_zona, wid_zona = campo("Zona de Pesca", "_zona_nombre", 0, 1,
                                    tipo='combo', opciones=zona_nombres, requerido=True)
        var_fi, _ = campo("Fecha Inicio", "fecha_inicio", 1, 0, tipo='calendar', requerido=True)
        var_ff, _ = campo("Fecha Fin",    "fecha_fin",    1, 1, tipo='calendar', requerido=True)
        var_met, _ = campo("Método de Pesca", "metodo_pesca", 2, 0,
                            tipo='combo',
                            opciones=['arrastre', 'cerco', 'palangre', 'artesanal'])
        var_cond, _ = campo("Condiciones Climáticas", "condiciones_climaticas", 2, 1)

        # Detalle de captura
        sep = tk.Frame(frm, bg=tema['border'], height=1)
        sep.grid(row=7, column=0, columnspan=2, sticky="ew", padx=8, pady=(8, 4))
        tk.Label(frm, text="Detalle de captura (especie y cantidad)",
                 font=("Calibri", 9, "bold"), bg=tema['bg'],
                 fg=tema['fg']).grid(row=8, column=0, sticky="w", padx=8)

        var_esp, _ = campo("Especie", "_esp_nombre", 4, 0,
                            tipo='combo', opciones=esp_nombres, requerido=True)
        var_kg, _ = campo("Cantidad (kg)", "cantidad_kg", 4, 1, requerido=True)

        # IDs ocultos
        var_emb_id  = tk.StringVar()
        var_zona_id = tk.StringVar()
        var_esp_id  = tk.StringVar()
        vars_form['embarcacion_id'] = var_emb_id
        vars_form['zona_id']        = var_zona_id
        vars_form['especie_id']     = var_esp_id

        def on_emb_change(*a):
            nom = var_emb.get()
            for e in (embarcaciones or []):
                if e['nombre'] == nom:
                    var_emb_id.set(str(e['id']))
                    break

        def on_zona_change(*a):
            nom = var_zona.get()
            for z in (zonas or []):
                if z['nombre'] == nom:
                    var_zona_id.set(str(z['id']))
                    break

        def on_esp_change(*a):
            nom = var_esp.get()
            for e in (especies or []):
                if e['nombre'] == nom:
                    var_esp_id.set(str(e['id']))
                    break

        var_emb.trace("w", on_emb_change)
        var_zona.trace("w", on_zona_change)
        var_esp.trace("w", on_esp_change)

        # Relleno en edición
        if datos:
            if datos.get('embarcacion_id'):
                var_emb_id.set(str(datos['embarcacion_id']))
                for e in (embarcaciones or []):
                    if e['id'] == datos['embarcacion_id']:
                        var_emb.set(e['nombre'])
                        break
            if datos.get('zona_id'):
                var_zona_id.set(str(datos['zona_id']))
                for z in (zonas or []):
                    if z['id'] == datos['zona_id']:
                        var_zona.set(z['nombre'])
                        break
            for k in ['fecha_inicio', 'fecha_fin', 'metodo_pesca', 'condiciones_climaticas']:
                if k in vars_form and datos.get(k):
                    vars_form[k].set(str(datos[k]))

        # Botones
        frm_btns = tk.Frame(v, bg=tema['bg'], pady=10)
        frm_btns.pack(fill="x")

        def guardar():
            form_datos = {k: val.get() for k, val in vars_form.items()
                          if not k.startswith('_')}
            ok = self.controller.guardar(form_datos, modo,
                                          captura_id=datos['id'] if datos else None)
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
