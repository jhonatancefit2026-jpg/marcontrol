# 🐟 MarControl — Sistema de Control Pesquero

---

## 📋 Descripción

MarControl es un sistema de gestión pesquera desarrollado en **Python** con arquitectura **MVC**, interfaz gráfica **Tkinter**, base de datos **MySQL** y todas las características de calidad de software requeridas en la guía de aprendizaje.

---

## 🏗️ Arquitectura del Sistema

```
marcontrol_app/
│
├── main.py                        # Punto de entrada
├── config.py                      # Configuración global y temas
├── database.py                    # Capa de acceso a datos (Singleton)
├── requirements.txt               # Dependencias
│
├── models/                        # Capa Modelo (M)
│   ├── embarcacion_model.py       # CRUD embarcaciones
│   ├── tripulante_model.py        # CRUD tripulantes + SP AsignarTripulantes
│   ├── captura_model.py           # CRUD capturas + SP RegistrarCaptura
│   └── procesamiento_model.py     # CRUD procesamiento + SP ProcesarLotePescado
│
├── views/                         # Capa Vista (V)
│   ├── base_view.py               # ThemeManager, widgets reutilizables
│   ├── main_view.py               # Ventana principal + sidebar
│   ├── embarcacion_view.py        # Módulo 1: Embarcaciones
│   ├── tripulante_view.py         # Módulo 2: Tripulantes
│   ├── captura_view.py            # Módulo 3: Capturas
│   └── procesamiento_view.py      # Módulo 4: Procesamiento
│
├── controllers/                   # Capa Controlador (C)
│   ├── embarcacion_controller.py
│   ├── tripulante_controller.py
│   ├── captura_controller.py
│   └── procesamiento_controller.py
│
├── utils/                         # Utilidades transversales
│   ├── validators.py              # Validaciones de campos
│   ├── export_excel.py            # Exportación Excel (openpyxl)
│   └── export_pdf.py              # Exportación PDF (reportlab)
│
└── assets/
    ├── favicon.ico                # Favicon generado con Pillow
    └── favicon_gen.py             # Generador de favicon
```

### Patrón MVC
- **Modelo:** Accede a MySQL, ejecuta SPs y funciones almacenadas
- **Vista:** Tkinter — formularios, tablas, validación visual
- **Controlador:** Orquesta entre Modelo y Vista, aplica reglas de negocio

---

## ✅ Requisitos Técnicos Cumplidos

| Requisito | Implementación |
|-----------|---------------|
| **Arquitectura MVC** | Carpetas models / views / controllers separadas |
| **≥ 4 módulos** | Embarcaciones, Tripulantes, Capturas, Procesamiento |
| **Base de datos marcontrol** | MySQL con Stored Procedures, Triggers, Views, Funciones |
| **Stored Procedures** | `RegistrarCaptura`, `ProcesarLotePescado`, `AsignarTripulantes` |
| **Funciones MySQL** | `FN_CalcularValorCaptura`, `FN_VerificarDisponibilidadEmbarcacion` |
| **CRUD completo** | Todos los módulos |
| **Exportar Excel** | openpyxl — formato profesional, filtros por fecha y categoría |
| **Exportar PDF** | reportlab — diseño corporativo, filtros, número de página |
| **Filtros de exportación** | Por rango de fechas y categoría en todos los módulos |
| **tkcalendar** | DateEntry en todos los campos de fecha |
| **Validación numérica** | Solo acepta números, rechazo de caracteres inválidos |
| **Validación texto** | Longitud mínima/máxima, caracteres especiales |
| **Validación email** | Regex RFC compliant |
| **Validación teléfono** | Formato internacional |
| **Confirmación** | Diálogos antes de eliminar y actualizar |
| **Pillow (imágenes)** | Redimensionamiento, carga JPG/PNG/GIF, thumbnail en formularios |
| **≥ 2 formularios con imagen** | Embarcaciones y Tripulantes |
| **Validación de imagen** | Formato, tamaño máximo 5 MB |
| **Favicon personalizado** | Generado con Pillow (pez azul marino) |
| **Iconografía en botones** | Emojis como iconos en todos los botones |
| **2 temas visuales** | Claro / Oscuro — intercambiables en tiempo real |

---

## 🚀 Instalación

### Base de datos
https://github.com/jhonatancefit/marcontrol_app/blob/main/marcontrol.sql

### 1. Clonar el repositorio
```bash
git clone https://github.com/jhonatancefit/marcontrol_app
cd marcontrol_app
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

O individualmente:
```bash
pip install mysql-connector-python Pillow openpyxl reportlab tkcalendar
```

### 3. Configurar base de datos

Edite `config.py` con sus credenciales MySQL:
```python
DB_CONFIG = {
    'user': 'root',
    'password': '',
    'database': 'marcontrol',
}
```

Importe el script SQL:
```bash
mysql -u root -p < marcontrol.sql
```

### 4. Ejecutar
```bash
python main.py
```

---

## 🗄️ Base de Datos

La BD `marcontrol` contiene:

**Tablas principales:** `embarcaciones`, `tripulantes`, `capturas`, `captura_detalle`, `especies`, `zonas_pesca`, `cuotas`, `temporadas`, `procesamiento`, `productos_procesados`, `licencias`, `mantenimientos`, `control_calidad`

**Stored Procedures vinculados:**
- `RegistrarCaptura(emb_id, zona_id, f_inicio, f_fin, especie_id, kg)` → Módulo Capturas
- `ProcesarLotePescado(captura_id, rendimiento, calidad)` → Módulo Procesamiento  
- `AsignarTripulantes(embarcacion_id, tripulante_id)` → Módulo Tripulantes

**Funciones MySQL usadas:**
- `FN_CalcularValorCaptura(captura_id)` → Valor monetario de la captura
- `FN_VerificarDisponibilidadEmbarcacion(id)` → Estado disponible

**Triggers activos:**
- `TR_VerificarCuotaPesca` — Bloquea si cuota excedida
- `TR_ActualizarHistorialEmbarcacion` — Log automático de capturas
- `TR_VerificarCertificacionesTripulantes` — Valida certificados al asignar
- `TR_ActualizarInventarioProcesado` — Actualiza inventario al procesar
- `TR_ControlarCalidadProcesamiento` — Alerta si rendimiento < 70%

---

## 📊 Exportaciones

Cada módulo incluye exportación con filtros:

- **Excel (.xlsx):** Formato profesional, cabeceras coloreadas, filas alternadas, totales
- **PDF (.pdf):** Diseño corporativo, banner azul, número de página, filtros aplicados
- **Filtros disponibles:** Rango de fechas (inicio/fin) y categoría (tipo, estado, método)

---

## 🎨 Temas Visuales

| | Tema Claro | Tema Oscuro |
|---|---|---|
| Fondo | `#F0F4F8` | `#0F172A` |
| Primario | `#1A56DB` | `#3B82F6` |
| Sidebar | `#1A3BBB` | `#020617` |

El botón de cambio de tema está en la parte inferior del sidebar. El cambio se aplica en tiempo real a todos los módulos activos.

---

## 📦 Dependencias

| Paquete | Uso |
|---------|-----|
| `mysql-connector-python` | Conexión MySQL, SPs, Funciones |
| `Pillow` | Manejo de imágenes, generación de favicon |
| `openpyxl` | Exportación a Excel |
| `reportlab` | Exportación a PDF |
| `tkcalendar` | DateEntry para campos de fecha |
| `tkinter` | Interfaz gráfica (incluido en Python) |

---
