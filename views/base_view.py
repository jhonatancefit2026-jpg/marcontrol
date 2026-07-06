"""
Vista base — gestión de temas y widgets reutilizables
"""
import tkinter as tk
from tkinter import ttk
from config import THEMES


class ThemeManager:
    _current_theme = 'light'
    _observers = []

    @classmethod
    def get_theme(cls):
        return THEMES[cls._current_theme]

    @classmethod
    def get_theme_name(cls):
        return cls._current_theme

    @classmethod
    def toggle_theme(cls):
        cls._current_theme = 'dark' if cls._current_theme == 'light' else 'light'
        cls._notify_observers()

    @classmethod
    def set_theme(cls, nombre):
        if nombre in THEMES:
            cls._current_theme = nombre
            cls._notify_observers()

    @classmethod
    def subscribe(cls, callback):
        cls._observers.append(callback)

    @classmethod
    def unsubscribe(cls, callback):
        if callback in cls._observers:
            cls._observers.remove(callback)

    @classmethod
    def _notify_observers(cls):
        for cb in cls._observers:
            try:
                cb()
            except Exception:
                pass


def estilo_ttk(tema=None):
    """Configura los estilos ttk globales para el tema actual."""
    if tema is None:
        tema = ThemeManager.get_theme()
    style = ttk.Style()
    style.theme_use('clam')

    # Treeview
    style.configure("Treeview",
                     background=tema['table_bg'],
                     foreground=tema['fg'],
                     fieldbackground=tema['table_bg'],
                     rowheight=26,
                     font=("Calibri", 10))
    style.configure("Treeview.Heading",
                     background=tema['tree_head'],
                     foreground=tema['tree_head_fg'],
                     font=("Calibri", 10, "bold"),
                     relief="flat")
    style.map("Treeview",
              background=[("selected", tema['table_select'])],
              foreground=[("selected", tema['fg'])])
    style.map("Treeview.Heading",
              background=[("active", tema['primary'])])

    # Combobox
    style.configure("TCombobox",
                     fieldbackground=tema['input_bg'],
                     background=tema['input_bg'],
                     foreground=tema['fg'],
                     selectbackground=tema['primary'],
                     selectforeground=tema['primary_fg'])

    # Scrollbar
    style.configure("TScrollbar",
                     background=tema['border'],
                     troughcolor=tema['bg'],
                     arrowcolor=tema['fg'])

    # Entry dentro de ttk (DateEntry etc.)
    style.configure("TEntry",
                     fieldbackground=tema['input_bg'],
                     foreground=tema['fg'],
                     insertcolor=tema['fg'])

    # Notebook
    style.configure("TNotebook",
                     background=tema['bg'],
                     tabmargins=[2, 5, 2, 0])
    style.configure("TNotebook.Tab",
                     background=tema['secondary'],
                     foreground=tema['fg'],
                     padding=[10, 4],
                     font=("Calibri", 10))
    style.map("TNotebook.Tab",
              background=[("selected", tema['primary'])],
              foreground=[("selected", tema['primary_fg'])])


class BotonAccion(tk.Button):
    """Botón estilizado para acciones."""
    def __init__(self, parent, texto, comando, tipo='primary', **kwargs):
        tema = ThemeManager.get_theme()
        colores = {
            'primary': (tema['btn_bg'], tema['btn_fg'], tema['btn_hover']),
            'danger':  (tema['btn_danger'], '#FFFFFF', '#9B1C1C'),
            'success': (tema['btn_success'], '#FFFFFF', '#145A32'),
            'warning': (tema['btn_warning'], '#FFFFFF', '#7B5E00'),
            'neutral': (tema['border'], tema['fg'], tema['secondary']),
        }
        bg, fg, hover = colores.get(tipo, colores['primary'])
        super().__init__(parent, text=texto, command=comando,
                         bg=bg, fg=fg,
                         font=("Calibri", 10, "bold"),
                         relief="flat", bd=0, cursor="hand2",
                         padx=12, pady=6,
                         activebackground=hover, activeforeground=fg,
                         **kwargs)
        self._bg = bg
        self._hover = hover
        self.bind("<Enter>", lambda e: self.config(bg=hover))
        self.bind("<Leave>", lambda e: self.config(bg=bg))


class EntradaLabeled(tk.Frame):
    """Frame con label + entry estilizado."""
    def __init__(self, parent, etiqueta, variable=None, tipo='entry',
                 opciones=None, requerido=False, **kwargs):
        tema = ThemeManager.get_theme()
        super().__init__(parent, bg=tema['frame_bg'], **kwargs)

        sufijo = " *" if requerido else ""
        self.label = tk.Label(self, text=f"{etiqueta}{sufijo}",
                              font=("Calibri", 9),
                              fg=tema['label_fg'],
                              bg=tema['frame_bg'],
                              anchor="w")
        self.label.pack(anchor="w", pady=(0, 2))

        if tipo == 'combo' and opciones is not None:
            self.widget = ttk.Combobox(self, textvariable=variable,
                                       values=opciones, state="readonly",
                                       font=("Calibri", 10))
        elif tipo == 'text':
            self.widget = tk.Text(self, height=3,
                                  bg=tema['input_bg'], fg=tema['fg'],
                                  font=("Calibri", 10),
                                  relief="solid", bd=1,
                                  insertbackground=tema['fg'])
        else:
            self.widget = tk.Entry(self, textvariable=variable,
                                   bg=tema['input_bg'], fg=tema['fg'],
                                   font=("Calibri", 10),
                                   relief="solid", bd=1,
                                   insertbackground=tema['fg'])
        self.widget.pack(fill="x")

    def get(self):
        if isinstance(self.widget, tk.Text):
            return self.widget.get("1.0", "end-1c")
        return self.widget.get()

    def set(self, valor):
        if isinstance(self.widget, tk.Text):
            self.widget.delete("1.0", "end")
            self.widget.insert("1.0", str(valor) if valor else "")
        elif isinstance(self.widget, ttk.Combobox):
            self.widget.set(str(valor) if valor else "")
        else:
            if hasattr(self.widget, 'variable') and self.widget.cget('textvariable'):
                var = self.widget.nametowidget(self.widget.cget('textvariable'))
                var.set(str(valor) if valor else "")
            else:
                self.widget.delete(0, "end")
                self.widget.insert(0, str(valor) if valor else "")
