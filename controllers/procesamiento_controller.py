"""
Controlador de Procesamiento — usa SP ProcesarLotePescado para registrar lotes
"""
import tkinter.messagebox as messagebox
from models.procesamiento_model import ProcesamientoModel
from utils.validators import (validar_numerico, validar_fecha,
                               validar_texto, fecha_a_mysql)
from utils.export_excel import exportar_filtrado
from utils.export_pdf import exportar_pdf_filtrado


class ProcesamientoController:
    COLUMNAS = ["ID", "Lote", "Captura N°", "Especie",
                "Fecha", "Método", "Materia Prima(kg)",
                "Rendimiento(%)", "Producto Final", "Cantidad Prod.(kg)", "Responsable"]

    def __init__(self, vista):
        self.vista = vista
        self.model = ProcesamientoModel()
        self._datos_completos = []

    def cargar_tabla(self):
        registros = self.model.obtener_todos()
        filas = []
        for r in registros:
            filas.append((
                r['id'], r['lote_codigo'],
                r.get('captura_num', ''), r.get('especie', ''),
                str(r.get('fecha', '') or ''),
                r.get('metodo_procesamiento', ''),
                str(r.get('materia_prima_kg', '')),
                str(r.get('rendimiento', '')),
                r.get('tipo_producto_final', ''),
                str(r.get('cantidad_producida_kg', '')),
                r.get('responsable', '')
            ))
        self.vista.mostrar_en_tabla(filas)
        self._datos_completos = filas

    def nuevo(self):
        capturas = self.model.obtener_capturas_combo()
        especies = self.model.obtener_especies_combo()
        lote_sugerido = self.model.generar_lote()
        self.vista.abrir_formulario(modo='nuevo',
                                     capturas=capturas,
                                     especies=especies,
                                     lote_sugerido=lote_sugerido)

    def editar(self, proc_id):
        datos = self.model.obtener_por_id(proc_id)
        if not datos:
            messagebox.showerror("Error", "Registro no encontrado.")
            return
        capturas = self.model.obtener_capturas_combo()
        especies = self.model.obtener_especies_combo()
        self.vista.abrir_formulario(modo='editar', datos=datos,
                                     capturas=capturas, especies=especies)

    def guardar(self, datos, modo, proc_id=None):
        errores = self._validar(datos)
        if errores:
            messagebox.showerror("Errores de validación", "\n".join(errores))
            return False

        if modo == 'editar':
            if not messagebox.askyesno("Confirmar", "¿Guardar cambios en este lote?"):
                return False

        try:
            if modo == 'nuevo':
                # Usar SP ProcesarLotePescado para registrar el lote
                self.model.registrar_lote(
                    captura_id=int(datos['captura_id']),
                    rendimiento=float(datos['rendimiento']),
                    calidad=datos.get('tipo_producto_final', 'Estándar')
                )
                # También crear el registro completo en procesamiento
                cantidad = self.model.calcular_cantidad(
                    datos['materia_prima_kg'], datos['rendimiento'])
                datos_completos = {
                    'lote_codigo': datos.get('lote_codigo') or self.model.generar_lote(),
                    'captura_id': int(datos['captura_id']),
                    'fecha': fecha_a_mysql(datos['fecha']),
                    'especie_id': int(datos['especie_id']) if datos.get('especie_id') else None,
                    'materia_prima_kg': float(datos['materia_prima_kg']),
                    'metodo_procesamiento': datos.get('metodo_procesamiento', 'congelado'),
                    'rendimiento': float(datos['rendimiento']),
                    'tipo_producto_final': datos.get('tipo_producto_final', '').strip(),
                    'cantidad_producida_kg': cantidad,
                    'responsable': datos.get('responsable', '').strip(),
                }
                self.model.crear_completo(datos_completos)
                messagebox.showinfo("Éxito", f"Lote registrado. Cantidad producida: {cantidad} kg")
            else:
                cantidad = self.model.calcular_cantidad(
                    datos['materia_prima_kg'], datos['rendimiento'])
                datos_mysql = {
                    'lote_codigo': datos['lote_codigo'],
                    'captura_id': int(datos['captura_id']),
                    'fecha': fecha_a_mysql(datos['fecha']),
                    'especie_id': int(datos['especie_id']) if datos.get('especie_id') else None,
                    'materia_prima_kg': float(datos['materia_prima_kg']),
                    'metodo_procesamiento': datos.get('metodo_procesamiento', 'congelado'),
                    'rendimiento': float(datos['rendimiento']),
                    'tipo_producto_final': datos.get('tipo_producto_final', '').strip(),
                    'cantidad_producida_kg': cantidad,
                    'responsable': datos.get('responsable', '').strip(),
                }
                self.model.actualizar(proc_id, datos_mysql)
                messagebox.showinfo("Éxito", "Lote actualizado correctamente.")
            self.cargar_tabla()
            return True
        except Exception as e:
            messagebox.showerror("Error al guardar", str(e))
            return False

    def eliminar(self, proc_id):
        if not messagebox.askyesno("Confirmar eliminación",
                                    "¿Eliminar este registro de procesamiento?"):
            return
        try:
            self.model.eliminar(proc_id)
            messagebox.showinfo("Eliminado", "Registro eliminado.")
            self.cargar_tabla()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")

    def calcular_cantidad_preview(self, materia_prima, rendimiento):
        """Preview en tiempo real de cantidad producida."""
        return self.model.calcular_cantidad(materia_prima, rendimiento)

    def _validar(self, datos):
        errores = []

        if not datos.get('captura_id'):
            errores.append("Debe seleccionar una captura de origen.")

        ok, msg = validar_fecha(datos.get('fecha', ''), "Fecha de proceso")
        if not ok:
            errores.append(msg)

        ok, msg = validar_numerico(datos.get('materia_prima_kg', ''),
                                    "Materia prima (kg)", min_val=0.01, decimal=True)
        if not ok:
            errores.append(msg)

        ok, msg = validar_numerico(datos.get('rendimiento', ''),
                                    "Rendimiento", min_val=1, max_val=100, decimal=True)
        if not ok:
            errores.append(msg)

        if not datos.get('metodo_procesamiento'):
            errores.append("Debe seleccionar el método de procesamiento.")

        ok, msg = validar_texto(datos.get('tipo_producto_final', ''),
                                 "Tipo de producto final", min_len=2, max_len=100)
        if not ok:
            errores.append(msg)

        return errores

    def exportar_excel(self):
        exportar_filtrado(
            titulo="Procesamiento",
            columnas=self.COLUMNAS,
            datos_completos=self._datos_completos,
            campo_fecha_idx=4,
            campo_categoria_idx=5,
            nombre_sugerido="Procesamiento_MarControl.xlsx"
        )

    def exportar_pdf(self):
        exportar_pdf_filtrado(
            titulo="Procesamiento de Lotes",
            columnas=self.COLUMNAS,
            datos_completos=self._datos_completos,
            campo_fecha_idx=4,
            campo_categoria_idx=5,
            nombre_sugerido="Procesamiento_MarControl.pdf",
            orientacion='landscape'
        )
