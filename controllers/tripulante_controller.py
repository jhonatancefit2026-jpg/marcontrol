"""
Controlador de Tripulantes — Patrón MVC
"""
import tkinter.messagebox as messagebox
from models.tripulante_model import TripulanteModel
from utils.validators import (validar_texto, validar_numerico, validar_dni,
                               validar_telefono, validar_fecha, validar_imagen,
                               fecha_a_mysql)
from utils.export_excel import exportar_filtrado
from utils.export_pdf import exportar_pdf_filtrado


class TripulanteController:
    COLUMNAS = ["ID", "DNI", "Nombres", "Apellidos", "Cargo",
                "Experiencia(años)", "Libreta Embarque", "Teléfono",
                "F. Nacimiento", "Estado Salud", "Disponible"]

    def __init__(self, vista):
        self.vista = vista
        self.model = TripulanteModel()
        self._datos_completos = []

    def cargar_tabla(self):
        registros = self.model.obtener_todos()
        filas = []
        for r in registros:
            filas.append((
                r['id'], r['dni'], r.get('nombres', ''),
                r.get('apellidos', ''), r.get('cargo', ''),
                r.get('experiencia_anios', ''), r.get('libreta_embarque', ''),
                r.get('telefono', ''), str(r.get('fecha_nacimiento', '') or ''),
                r.get('estado_salud', ''),
                'Sí' if r.get('disponible') else 'No'
            ))
        self.vista.mostrar_en_tabla(filas)
        self._datos_completos = filas

    def nuevo(self):
        self.vista.abrir_formulario(modo='nuevo')

    def editar(self, tripulante_id):
        datos = self.model.obtener_por_id(tripulante_id)
        if not datos:
            messagebox.showerror("Error", "Registro no encontrado.")
            return
        self.vista.abrir_formulario(modo='editar', datos=datos)

    def guardar(self, datos, modo, tripulante_id=None):
        errores = self._validar(datos, tripulante_id if modo == 'editar' else None)
        if errores:
            messagebox.showerror("Errores de validación", "\n".join(errores))
            return False

        if modo == 'editar':
            if not messagebox.askyesno("Confirmar", "¿Guardar cambios en este tripulante?"):
                return False

        datos_mysql = {
            'dni': datos['dni'].strip().upper(),
            'nombres': datos['nombres'].strip(),
            'apellidos': datos['apellidos'].strip(),
            'fecha_nacimiento': fecha_a_mysql(datos['fecha_nacimiento']) if datos.get('fecha_nacimiento') else None,
            'direccion': datos.get('direccion', '').strip(),
            'telefono': datos.get('telefono', '').strip(),
            'libreta_embarque': datos.get('libreta_embarque', '').strip(),
            'cargo': datos.get('cargo', '').strip(),
            'experiencia_anios': int(datos['experiencia_anios']) if datos.get('experiencia_anios') else 0,
            'estado_salud': datos.get('estado_salud', 'Bueno').strip(),
            'disponible': 1 if datos.get('disponible') else 0,
            'foto_ruta': datos.get('foto_ruta', '') or '',
        }

        try:
            if modo == 'nuevo':
                self.model.crear(datos_mysql)
                messagebox.showinfo("Éxito", "Tripulante registrado correctamente.")
            else:
                self.model.actualizar(tripulante_id, datos_mysql)
                messagebox.showinfo("Éxito", "Tripulante actualizado correctamente.")
            self.cargar_tabla()
            return True
        except Exception as e:
            messagebox.showerror("Error al guardar", str(e))
            return False

    def eliminar(self, tripulante_id):
        if not messagebox.askyesno("Confirmar eliminación",
                                    "¿Eliminar este tripulante?\nEsta acción no se puede deshacer."):
            return
        try:
            self.model.eliminar(tripulante_id)
            messagebox.showinfo("Eliminado", "Tripulante eliminado.")
            self.cargar_tabla()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar:\n{e}")

    def ver_certificados(self, tripulante_id):
        certs = self.model.obtener_certificados(tripulante_id)
        self.vista.mostrar_certificados(certs)

    def asignar_embarcacion(self, embarcacion_id, tripulante_id):
        """Llama al SP AsignarTripulantes."""
        try:
            self.model.asignar_a_embarcacion(embarcacion_id, tripulante_id)
            messagebox.showinfo("Asignado",
                                "Tripulante asignado a la embarcación correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo asignar:\n{e}")

    def _validar(self, datos, excluir_id=None):
        errores = []

        ok, msg = validar_dni(datos.get('dni', ''))
        if not ok:
            errores.append(msg)
        elif self.model.verificar_dni_duplicado(datos['dni'].strip(), excluir_id):
            errores.append("Ya existe un tripulante con ese DNI.")

        ok, msg = validar_texto(datos.get('nombres', ''), "Nombres", min_len=2)
        if not ok:
            errores.append(msg)

        ok, msg = validar_texto(datos.get('apellidos', ''), "Apellidos", min_len=2)
        if not ok:
            errores.append(msg)

        if datos.get('telefono'):
            ok, msg = validar_telefono(datos['telefono'], "Teléfono")
            if not ok:
                errores.append(msg)

        if datos.get('fecha_nacimiento'):
            ok, msg = validar_fecha(datos['fecha_nacimiento'], "Fecha de nacimiento")
            if not ok:
                errores.append(msg)

        if datos.get('experiencia_anios'):
            ok, msg = validar_numerico(datos['experiencia_anios'], "Experiencia",
                                        min_val=0, max_val=60)
            if not ok:
                errores.append(msg)

        if datos.get('foto_ruta'):
            ok, msg = validar_imagen(datos['foto_ruta'], "Foto de tripulante")
            if not ok:
                errores.append(msg)

        return errores

    def exportar_excel(self):
        exportar_filtrado(
            titulo="Tripulantes",
            columnas=self.COLUMNAS,
            datos_completos=self._datos_completos,
            campo_categoria_idx=4,
            nombre_sugerido="Tripulantes_MarControl.xlsx"
        )

    def exportar_pdf(self):
        exportar_pdf_filtrado(
            titulo="Tripulantes",
            columnas=self.COLUMNAS,
            datos_completos=self._datos_completos,
            campo_categoria_idx=4,
            nombre_sugerido="Tripulantes_MarControl.pdf",
            orientacion='landscape'
        )
