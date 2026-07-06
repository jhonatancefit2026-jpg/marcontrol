"""
Controlador de Embarcaciones — Patrón MVC
Orquesta entre EmbarcacionModel y VistaEmbarcaciones
"""
import tkinter.messagebox as messagebox
from models.embarcacion_model import EmbarcacionModel
from utils.validators import (validar_texto, validar_numerico,
                               validar_fecha, validar_matricula,
                               validar_imagen, fecha_a_mysql)
from utils.export_excel import exportar_filtrado
from utils.export_pdf import exportar_pdf_filtrado


class EmbarcacionController:
    COLUMNAS = ["ID", "Matrícula", "Nombre", "Tipo", "Año",
                "Material", "Eslora(m)", "Capacidad(tn)",
                "Potencia(kw)", "Estado", "Última Insp."]

    def __init__(self, vista):
        self.vista = vista
        self.model = EmbarcacionModel()

    # ── CRUD ────────────────────────────────────────────────────

    def cargar_tabla(self):
        """Carga todos los registros en la tabla."""
        registros = self.model.obtener_todos()
        filas = []
        for r in registros:
            filas.append((
                r['id'], r['matricula'], r['nombre'],
                r.get('tipo', ''), r.get('ano_construccion', ''),
                r.get('material_casco', ''), r.get('eslora', ''),
                r.get('capacidad_bodega_tn', ''),
                r.get('potencia_motor_kw', ''),
                r.get('estado', ''),
                str(r.get('fecha_ultima_inspeccion', '') or '')
            ))
        self.vista.mostrar_en_tabla(filas)
        self._datos_completos = filas

    def nuevo(self):
        """Abre formulario vacío para crear."""
        self.vista.abrir_formulario(modo='nuevo')

    def editar(self, embarcacion_id):
        """Carga datos de la embarcacion en el formulario."""
        datos = self.model.obtener_por_id(embarcacion_id)
        if not datos:
            messagebox.showerror("Error", "Registro no encontrado.")
            return
        self.vista.abrir_formulario(modo='editar', datos=datos)

    def guardar(self, datos, modo, embarcacion_id=None):
        """Valida y guarda (crea o actualiza)."""
        errores = self._validar(datos, embarcacion_id if modo == 'editar' else None)
        if errores:
            messagebox.showerror("Errores de validación", "\n".join(errores))
            return False

        # Confirmar si es edición
        if modo == 'editar':
            if not messagebox.askyesno("Confirmar", "¿Guardar cambios en esta embarcación?"):
                return False

        datos_mysql = {
            'matricula': datos['matricula'].strip().upper(),
            'nombre': datos['nombre'].strip(),
            'tipo': datos['tipo'],
            'ano_construccion': datos.get('ano_construccion') or None,
            'material_casco': datos.get('material_casco', '').strip(),
            'eslora': float(datos['eslora']) if datos.get('eslora') else None,
            'manga': float(datos['manga']) if datos.get('manga') else None,
            'calado': float(datos['calado']) if datos.get('calado') else None,
            'capacidad_bodega_tn': float(datos['capacidad_bodega_tn']) if datos.get('capacidad_bodega_tn') else None,
            'potencia_motor_kw': int(datos['potencia_motor_kw']) if datos.get('potencia_motor_kw') else None,
            'velocidad_max_kn': float(datos['velocidad_max_kn']) if datos.get('velocidad_max_kn') else None,
            'autonomia_dias': int(datos['autonomia_dias']) if datos.get('autonomia_dias') else None,
            'equipos_navegacion': datos.get('equipos_navegacion', '').strip(),
            'fecha_ultima_inspeccion': fecha_a_mysql(datos['fecha_ultima_inspeccion']) if datos.get('fecha_ultima_inspeccion') else None,
            'estado': datos.get('estado', 'operativa'),
            'foto_ruta': datos.get('foto_ruta', '') or '',
        }

        try:
            if modo == 'nuevo':
                self.model.crear(datos_mysql)
                messagebox.showinfo("Éxito", "Embarcación registrada correctamente.")
            else:
                self.model.actualizar(embarcacion_id, datos_mysql)
                messagebox.showinfo("Éxito", "Embarcación actualizada correctamente.")
            self.cargar_tabla()
            return True
        except Exception as e:
            messagebox.showerror("Error al guardar", str(e))
            return False

    def eliminar(self, embarcacion_id):
        """Confirma y elimina una embarcación."""
        if not messagebox.askyesno("Confirmar eliminación",
                                    "¿Eliminar esta embarcación?\nEsta acción no se puede deshacer."):
            return
        try:
            self.model.eliminar(embarcacion_id)
            messagebox.showinfo("Eliminado", "Embarcación eliminada.")
            self.cargar_tabla()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")

    # ── VALIDACIONES ─────────────────────────────────────────────

    def _validar(self, datos, excluir_id=None):
        errores = []

        ok, msg = validar_matricula(datos.get('matricula', ''))
        if not ok:
            errores.append(msg)
        elif self.model.verificar_matricula_duplicada(datos['matricula'].strip().upper(), excluir_id):
            errores.append("Ya existe una embarcación con esa matrícula.")

        ok, msg = validar_texto(datos.get('nombre', ''), "Nombre", min_len=2, max_len=100)
        if not ok:
            errores.append(msg)

        if not datos.get('tipo'):
            errores.append("Debe seleccionar el tipo de embarcación.")

        if datos.get('eslora'):
            ok, msg = validar_numerico(datos['eslora'], "Eslora", min_val=0, decimal=True)
            if not ok:
                errores.append(msg)

        if datos.get('capacidad_bodega_tn'):
            ok, msg = validar_numerico(datos['capacidad_bodega_tn'], "Capacidad bodega",
                                        min_val=0, decimal=True)
            if not ok:
                errores.append(msg)

        if datos.get('potencia_motor_kw'):
            ok, msg = validar_numerico(datos['potencia_motor_kw'], "Potencia motor", min_val=0)
            if not ok:
                errores.append(msg)

        if datos.get('fecha_ultima_inspeccion'):
            ok, msg = validar_fecha(datos['fecha_ultima_inspeccion'], "Fecha de inspección")
            if not ok:
                errores.append(msg)

        if datos.get('foto_ruta'):
            ok, msg = validar_imagen(datos['foto_ruta'], "Foto de embarcación")
            if not ok:
                errores.append(msg)

        return errores

    # ── EXPORTACIÓN ──────────────────────────────────────────────

    def exportar_excel(self):
        datos = getattr(self, '_datos_completos', [])
        exportar_filtrado(
            titulo="Embarcaciones",
            columnas=self.COLUMNAS,
            datos_completos=datos,
            campo_categoria_idx=9,
            nombre_sugerido="Embarcaciones_MarControl.xlsx"
        )

    def exportar_pdf(self):
        datos = getattr(self, '_datos_completos', [])
        exportar_pdf_filtrado(
            titulo="Embarcaciones",
            columnas=self.COLUMNAS,
            datos_completos=datos,
            campo_categoria_idx=9,
            nombre_sugerido="Embarcaciones_MarControl.pdf",
            orientacion='landscape'
        )
