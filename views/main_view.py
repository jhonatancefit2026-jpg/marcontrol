"""
Vista principal de MarControl
Ventana principal con sidebar de navegación + área de contenido
"""
import tkinter as tk
from tkinter import ttk
from config import APP_TITLE, FAVICON_PATH
from views.base_view import ThemeManager, estilo_ttk


class VentanaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1280x780")
        self.minsize(900, 600)

        # Favicon
        try:
            self.iconbitmap(FAVICON_PATH)
        except Exception:
            pass

        ThemeManager.subscribe(self._aplicar_tema)
        self._construir_ui()
        self._aplicar_tema()

        # Centrar ventana
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 1280) // 2
        y = (self.winfo_screenheight() - 780) // 2
        self.geometry(f"1280x780+{x}+{y}")

    def _construir_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ── SIDEBAR ────────────────────────────────────────────────
        self.sidebar = tk.Frame(self, width=220)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Logo / Título en sidebar
        self.frm_logo = tk.Frame(self.sidebar)
        self.frm_logo.pack(fill="x", pady=0)

        self.lbl_logo_icono = tk.Label(self.frm_logo, text="🐟",
                                       font=("Segoe UI Emoji", 28))
        self.lbl_logo_icono.pack(pady=(20, 4))

        self.lbl_logo = tk.Label(self.frm_logo, text="MarControl",
                                  font=("Calibri", 16, "bold"))
        self.lbl_logo.pack()

        self.lbl_subtitulo = tk.Label(self.frm_logo, text="Sistema Pesquero",
                                       font=("Calibri", 9))
        self.lbl_subtitulo.pack(pady=(0, 16))

        # Separador
        self.sep1 = tk.Frame(self.frm_logo, height=1)
        self.sep1.pack(fill="x", padx=16, pady=(0, 16))

        # Menú de módulos
        self.botones_menu = []
        self._menu_items = [
            ("🏠", "Dashboard",     "dashboard"),
            ("⛵", "Embarcaciones",  "embarcaciones"),
            ("👥", "Tripulantes",    "tripulantes"),
            ("🎣", "Capturas",       "capturas"),
            ("🏭", "Procesamiento",  "procesamiento"),
        ]

        self.frm_menu = tk.Frame(self.sidebar)
        self.frm_menu.pack(fill="x", padx=8)

        for icono, nombre, key in self._menu_items:
            btn = tk.Button(
                self.frm_menu,
                text=f"  {icono}  {nombre}",
                font=("Calibri", 11),
                relief="flat", bd=0,
                anchor="w",
                cursor="hand2",
                padx=12, pady=10,
                command=lambda k=key: self.navegar(k)
            )
            btn.pack(fill="x", pady=2)
            btn._key = key
            self.botones_menu.append(btn)

        # Bottom: tema toggle
        self.frm_bottom = tk.Frame(self.sidebar)
        self.frm_bottom.pack(side="bottom", fill="x", padx=16, pady=16)

        self.sep2 = tk.Frame(self.frm_bottom, height=1)
        self.sep2.pack(fill="x", pady=(0, 12))

        self.btn_tema = tk.Button(
            self.frm_bottom,
            text="🌙  Tema Oscuro",
            font=("Calibri", 10),
            relief="flat", bd=0, cursor="hand2",
            padx=12, pady=8,
            command=self._cambiar_tema,
            anchor="w"
        )
        self.btn_tema.pack(fill="x")

        self.lbl_version = tk.Label(self.frm_bottom, text="v1.0.0",
                                     font=("Calibri", 8))
        self.lbl_version.pack(anchor="e", pady=(8, 0))

        # ── ÁREA DE CONTENIDO ──────────────────────────────────────
        self.frm_contenido = tk.Frame(self)
        self.frm_contenido.grid(row=0, column=1, sticky="nsew")
        self.frm_contenido.grid_rowconfigure(0, weight=1)
        self.frm_contenido.grid_columnconfigure(0, weight=1)

        self._vista_actual = None
        self._modulo_activo = None

        # Mostrar dashboard al inicio
        self.navegar("dashboard")

    def navegar(self, modulo):
        """Cambia la vista activa en el área de contenido."""
        if self._vista_actual:
            self._vista_actual.destroy()

        self._modulo_activo = modulo
        self._actualizar_boton_activo()

        if modulo == "dashboard":
            self._vista_actual = self._crear_dashboard()
        elif modulo == "embarcaciones":
            from views.embarcacion_view import VistaEmbarcaciones
            self._vista_actual = VistaEmbarcaciones(self.frm_contenido)
        elif modulo == "tripulantes":
            from views.tripulante_view import VistaTripulantes
            self._vista_actual = VistaTripulantes(self.frm_contenido)
        elif modulo == "capturas":
            from views.captura_view import VistaCapturas
            self._vista_actual = VistaCapturas(self.frm_contenido)
        elif modulo == "procesamiento":
            from views.procesamiento_view import VistaProcesamiento
            self._vista_actual = VistaProcesamiento(self.frm_contenido)

        if self._vista_actual:
            self._vista_actual.grid(row=0, column=0, sticky="nsew")

    def _crear_dashboard(self):
        """Panel de inicio con resumen del sistema."""
        tema = ThemeManager.get_theme()
        frame = tk.Frame(self.frm_contenido, bg=tema['bg'])
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=1)
        frame.grid_columnconfigure(3, weight=1)

        # Header
        hdr = tk.Frame(frame, bg=tema['header_bg'], height=80)
        hdr.grid(row=0, column=0, columnspan=4, sticky="ew")
        hdr.grid_propagate(False)
        tk.Label(hdr, text="🐟  MarControl — Panel de Control",
                 font=("Calibri", 20, "bold"),
                 bg=tema['header_bg'], fg=tema['header_fg']).pack(side="left", padx=24, pady=20)

        # Subtitle
        tk.Label(frame, text="Sistema de Control Pesquero — Bienvenido",
                 font=("Calibri", 11, "italic"),
                 bg=tema['bg'], fg=tema['label_fg']).grid(row=1, column=0, columnspan=4,
                                                          sticky="w", padx=24, pady=12)

        # Tarjetas de módulos
        tarjetas = [
            ("⛵", "Embarcaciones", "Gestión de la flota pesquera", "embarcaciones", tema['primary']),
            ("👥", "Tripulantes",   "Registro y asignación de tripulantes", "tripulantes", "#7C3AED"),
            ("🎣", "Capturas",      "Control de faenas y capturas", "capturas", "#059669"),
            ("🏭", "Procesamiento", "Lotes y procesamiento de pescado", "procesamiento", "#DC6F00"),
        ]

        for col, (icono, tit, desc, key, color) in enumerate(tarjetas):
            card = tk.Frame(frame, bg=tema['frame_bg'],
                            relief="flat", bd=0,
                            cursor="hand2")
            card.grid(row=2, column=col, padx=12, pady=12, sticky="nsew")
            card.grid_rowconfigure(3, weight=1)

            # Barra de color superior
            barra = tk.Frame(card, bg=color, height=6)
            barra.grid(row=0, column=0, sticky="ew")

            tk.Label(card, text=icono, font=("Segoe UI Emoji", 36),
                     bg=tema['frame_bg']).grid(row=1, column=0, pady=(20, 8))
            tk.Label(card, text=tit, font=("Calibri", 14, "bold"),
                     bg=tema['frame_bg'], fg=tema['fg']).grid(row=2, column=0)
            tk.Label(card, text=desc, font=("Calibri", 9),
                     bg=tema['frame_bg'], fg=tema['label_fg'],
                     wraplength=160).grid(row=3, column=0, pady=(4, 20), padx=16)

            btn = tk.Button(card, text="Abrir módulo →",
                            font=("Calibri", 9, "bold"),
                            bg=color, fg="white",
                            relief="flat", cursor="hand2",
                            padx=10, pady=4,
                            command=lambda k=key: self.navegar(k))
            btn.grid(row=4, column=0, pady=(0, 16))

        return frame

    def _actualizar_boton_activo(self):
        tema = ThemeManager.get_theme()
        for btn in self.botones_menu:
            if btn._key == self._modulo_activo:
                btn.config(bg=tema['sidebar_active'], fg=tema['sidebar_fg'])
            else:
                btn.config(bg=tema['sidebar_bg'], fg=tema['sidebar_fg'])
            btn.config(activebackground=tema['sidebar_hover'])

    def _cambiar_tema(self):
        ThemeManager.toggle_theme()
        if ThemeManager.get_theme_name() == 'dark':
            self.btn_tema.config(text="☀️  Tema Claro")
        else:
            self.btn_tema.config(text="🌙  Tema Oscuro")

    def _aplicar_tema(self):
        tema = ThemeManager.get_theme()
        estilo_ttk(tema)

        self.config(bg=tema['bg'])
        self.sidebar.config(bg=tema['sidebar_bg'])
        self.frm_logo.config(bg=tema['sidebar_bg'])
        self.lbl_logo_icono.config(bg=tema['sidebar_bg'], fg=tema['sidebar_fg'])
        self.lbl_logo.config(bg=tema['sidebar_bg'], fg=tema['sidebar_fg'])
        self.lbl_subtitulo.config(bg=tema['sidebar_bg'], fg=tema['sidebar_fg'])
        self.sep1.config(bg=tema['border'])
        self.frm_menu.config(bg=tema['sidebar_bg'])
        self.frm_bottom.config(bg=tema['sidebar_bg'])
        self.sep2.config(bg=tema['border'])
        self.btn_tema.config(bg=tema['sidebar_bg'], fg=tema['sidebar_fg'],
                              activebackground=tema['sidebar_hover'])
        self.lbl_version.config(bg=tema['sidebar_bg'], fg=tema['sidebar_fg'])
        self.frm_contenido.config(bg=tema['bg'])

        self._actualizar_boton_activo()

        # Redibujar vista actual
        if self._modulo_activo:
            self.navegar(self._modulo_activo)
