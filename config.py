"""
Configuración global de MarControl
"""

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'marcontrol',
    'port': 3306
}

APP_TITLE = "MarControl — Sistema de Control Pesquero"
APP_VERSION = "1.0.0"
FAVICON_PATH = "assets/favicon.ico"

THEMES = {
    'light': {
        'bg': '#F0F4F8',
        'fg': '#1A202C',
        'primary': '#1A56DB',
        'primary_dark': '#1A3BBB',
        'primary_fg': '#FFFFFF',
        'secondary': '#E8F0FE',
        'accent': '#E97316',
        'table_bg': '#FFFFFF',
        'table_alt': '#F7FAFC',
        'table_select': '#DBEAFE',
        'border': '#CBD5E0',
        'error': '#C53030',
        'success': '#276749',
        'warning': '#B7791F',
        'sidebar_bg': '#1A3BBB',
        'sidebar_fg': '#FFFFFF',
        'sidebar_hover': '#2251CC',
        'sidebar_active': '#3D63E0',
        'input_bg': '#FFFFFF',
        'frame_bg': '#FFFFFF',
        'header_bg': '#1A56DB',
        'header_fg': '#FFFFFF',
        'btn_bg': '#1A56DB',
        'btn_fg': '#FFFFFF',
        'btn_hover': '#1A3BBB',
        'btn_danger': '#C53030',
        'btn_success': '#276749',
        'btn_warning': '#B7791F',
        'tree_head': '#2D3748',
        'tree_head_fg': '#FFFFFF',
        'label_fg': '#4A5568',
        'entry_focus': '#2B6CB0',
    },
    'dark': {
        'bg': '#0F172A',
        'fg': '#E2E8F0',
        'primary': '#3B82F6',
        'primary_dark': '#2563EB',
        'primary_fg': '#FFFFFF',
        'secondary': '#1E293B',
        'accent': '#F97316',
        'table_bg': '#1E293B',
        'table_alt': '#0F172A',
        'table_select': '#1D4ED8',
        'border': '#334155',
        'error': '#FC8181',
        'success': '#68D391',
        'warning': '#F6AD55',
        'sidebar_bg': '#020617',
        'sidebar_fg': '#E2E8F0',
        'sidebar_hover': '#1E3A5F',
        'sidebar_active': '#1D4ED8',
        'input_bg': '#1E293B',
        'frame_bg': '#1E293B',
        'header_bg': '#0F172A',
        'header_fg': '#E2E8F0',
        'btn_bg': '#3B82F6',
        'btn_fg': '#FFFFFF',
        'btn_hover': '#2563EB',
        'btn_danger': '#EF4444',
        'btn_success': '#22C55E',
        'btn_warning': '#F59E0B',
        'tree_head': '#0F172A',
        'tree_head_fg': '#93C5FD',
        'label_fg': '#94A3B8',
        'entry_focus': '#3B82F6',
    }
}
