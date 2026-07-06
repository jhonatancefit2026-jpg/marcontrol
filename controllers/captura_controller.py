"""
Controlador de Capturas — usa SP RegistrarCaptura para inserciones
"""
import tkinter.messagebox as messagebox
from models.captura_model import CapturaModel
from utils.validators import (validar_numerico, validar_fecha,
                               validar_fecha_rango, validar_texto,
                               fecha_a_mysql)
from utils.export_excel import exportar_filtrado
from utils.export_pdf import exportar_pdf_filtrado


class CapturaController:
    COLUMNAS = ["ID", "N° Registro", "Embarcación", "Zona",
                "Fecha Inicio", "Fecha Fin", "Método",
                "Especies", "Total Kg", "Condiciones"]

    def __init__(self, vista):
        self.vista = vista
        self.model = CapturaModel()
        self._datos_completos = []

    def cargar_tabla(self):
        registros = self.model.obtener_todos()
        filas = []
        for r in registros:
            filas.append((
                r['id'], r['numero_registro'],
                r.get('embarcacion', ''), r.get('zona', ''),
                str(r.get('fecha_inicio', '') or ''),
                str(r.get('fecha_fin', '') or ''),
                r.get('metodo_pesca', ''),
                r.get('especies', ''),
                str(r.get('total_kg', 0)),
                r.get('condiciones_climaticas', '')
            ))
        self.vista.mostrar_en_tabla(filas)
        self._datos_completos = filas

    def nuevo(self):
        zonas = self.model.obtener_zonas()
        especies = self.model.obtener_especies()
        from models.embarcacion_model import EmbarcacionModel
        embarcaciones = EmbarcacionModel().obtener_para_combo()
        self.vista.abrir_formulario(modo='nuevo',
                                     zonas=zonas,
                                     especies=especies,
                                     embarcaciones=embarcaciones)

    def editar(self, captura_id):
        datos = self.model.obtener_por_id(captura_id)
        if not datos:
            messagebox.showerror("Error", "Registro no encontrado.")
            return
        zonas = self.model.obtener_zonas()
        especies = self.model.obtener_especies()
        from models.embarcacion_model import EmbarcacionModel
        embarcaciones = EmbarcacionModel().obtener_para_combo()
        self.vista.abrir_formulario(modo='editar', datos=datos,
                                     zonas=zonas, especies=especies,
                                     embarcaciones=embarcaciones)

    def guardar(self, datos, modo, captura_id=None):
        errores = self._validar(datos)
        if errores:
            messagebox.showerror("Errores de validación", "\n".join(errores))
            return False

        if modo == 'editar':
            if not messagebox.askyesno("Confirmar", "¿Guardar cambios en esta captura?"):
                return False

        try:
            if modo == 'nuevo':
                # Usa el Stored Procedure RegistrarCaptura
                self.model.registrar(
                    embarcacion_id=int(datos['embarcacion_id']),
                    zona_id=int(datos['zona_id']),
                    fecha_inicio=fecha_a_mysql(datos['fecha_inicio']),
                    fecha_fin=fecha_a_mysql(datos['fecha_fin']),
                    especie_id=int(datos['especie_id']),
                    cantidad_kg=float(datos['cantidad_kg'])
                )
                messagebox.showinfo("Éxito", "Captura registrada mediante SP RegistrarCaptura.")
            else:
                datos_mysql = {
                    'embarcacion_id': int(datos['embarcacion_id']),
                    'zona_id': int(datos['zona_id']),
                    'fecha_inicio': fecha_a_mysql(datos['fecha_inicio']),
                    'fecha_fin': fecha_a_mysql(datos['fecha_fin']),
                    'metodo_pesca': datos.get('metodo_pesca', '').strip(),
                    'condiciones_climaticas': datos.get('condiciones_climaticas', '').strip(),
                }
                self.model.actualizar(captura_id, datos_mysql)
                messagebox.showinfo("Éxito", "Captura actualizada correctamente.")
            self.cargar_tabla()
            return True
        except Exception as e:
            messagebox.showerror("Error al guardar", str(e))
            return False

    def eliminar(self, captura_id):
        if not messagebox.askyesno("Confirmar eliminación",
                                    "¿Eliminar esta captura?\nTambién se eliminarán sus detalles."):
            return
        try:
            self.model.eliminar(captura_id)
            messagebox.showinfo("Eliminado", "Captura eliminada.")
            self.cargar_tabla()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")

    def ver_detalle(self, captura_id):
        detalle = self.model.obtener_detalle(captura_id)
        valor = self.model.calcular_valor(captura_id)
        self.vista.mostrar_detalle(detalle, valor)

    def _validar(self, datos):
        errores = []

        if not datos.get('embarcacion_id'):
            errores.append("Debe seleccionar una embarcación.")

        if not datos.get('zona_id'):
            errores.append("Debe seleccionar una zona de pesca.")

        if datos.get('fecha_inicio') and datos.get('fecha_fin'):
            ok, msg = validar_fecha_rango(datos['fecha_inicio'], datos['fecha_fin'])
            if not ok:
                errores.append(msg)
        else:
            if not datos.get('fecha_inicio'):
                errores.append("Fecha inicio es obligatoria.")
            if not datos.get('fecha_fin'):
                errores.append("Fecha fin es obligatoria.")

        if not datos.get('especie_id'):
            errores.append("Debe seleccionar una especie.")

        if datos.get('cantidad_kg'):
            ok, msg = validar_numerico(datos['cantidad_kg'], "Cantidad (kg)",
                                        min_val=0.01, decimal=True)
            if not ok:
                errores.append(msg)
        else:
            errores.append("Cantidad en kg es obligatoria.")

        return errores

    def exportar_excel(self):
        exportar_filtrado(
            titulo="Capturas",
            columnas=self.COLUMNAS,
            datos_completos=self._datos_completos,
            campo_fecha_idx=4,
            campo_categoria_idx=6,
            nombre_sugerido="Capturas_MarControl.xlsx"
        )

    def exportar_pdf(self):
        exportar_pdf_filtrado(
            titulo="Capturas",
            columnas=self.COLUMNAS,
            datos_completos=self._datos_completos,
            campo_fecha_idx=4,
            campo_categoria_idx=6,
            nombre_sugerido="Capturas_MarControl.pdf",
            orientacion='landscape'
        )
