"""
Modelo de Embarcaciones — acceso a datos con MySQL
Usa SQL directo para SELECT/UPDATE/DELETE
"""
from database import Database


class EmbarcacionModel:
    def __init__(self):
        self.db = Database.get_instance()

    def obtener_todos(self):
        query = """
            SELECT id, matricula, nombre, tipo, ano_construccion,
                   material_casco, eslora, manga, calado,
                   capacidad_bodega_tn, potencia_motor_kw,
                   velocidad_max_kn, autonomia_dias,
                   equipos_navegacion, fecha_ultima_inspeccion,
                   estado
            FROM embarcaciones
            ORDER BY nombre
        """
        return self.db.execute_query(query, fetch=True) or []

    def obtener_por_id(self, embarcacion_id):
        query = "SELECT * FROM embarcaciones WHERE id = %s"
        result = self.db.execute_query(query, (embarcacion_id,), fetch=True)
        return result[0] if result else None

    def crear(self, datos):
        """
        datos: dict con campos de embarcacion (sin id).
        """
        query = """
            INSERT INTO embarcaciones
              (matricula, nombre, tipo, ano_construccion, material_casco,
               eslora, manga, calado, capacidad_bodega_tn, potencia_motor_kw,
               velocidad_max_kn, autonomia_dias, equipos_navegacion,
               fecha_ultima_inspeccion, estado, foto_ruta)
            VALUES
              (%(matricula)s, %(nombre)s, %(tipo)s, %(ano_construccion)s, %(material_casco)s,
               %(eslora)s, %(manga)s, %(calado)s, %(capacidad_bodega_tn)s, %(potencia_motor_kw)s,
               %(velocidad_max_kn)s, %(autonomia_dias)s, %(equipos_navegacion)s,
               %(fecha_ultima_inspeccion)s, %(estado)s, %(foto_ruta)s)
        """
        return self.db.execute_query(query, datos)

    def actualizar(self, embarcacion_id, datos):
        query = """
            UPDATE embarcaciones SET
              matricula=%(matricula)s, nombre=%(nombre)s, tipo=%(tipo)s,
              ano_construccion=%(ano_construccion)s, material_casco=%(material_casco)s,
              eslora=%(eslora)s, manga=%(manga)s, calado=%(calado)s,
              capacidad_bodega_tn=%(capacidad_bodega_tn)s, potencia_motor_kw=%(potencia_motor_kw)s,
              velocidad_max_kn=%(velocidad_max_kn)s, autonomia_dias=%(autonomia_dias)s,
              equipos_navegacion=%(equipos_navegacion)s,
              fecha_ultima_inspeccion=%(fecha_ultima_inspeccion)s,
              estado=%(estado)s, foto_ruta=%(foto_ruta)s
            WHERE id=%(id)s
        """
        datos['id'] = embarcacion_id
        return self.db.execute_query(query, datos)

    def eliminar(self, embarcacion_id):
        query = "DELETE FROM embarcaciones WHERE id = %s"
        return self.db.execute_query(query, (embarcacion_id,))

    def verificar_matricula_duplicada(self, matricula, excluir_id=None):
        if excluir_id:
            q = "SELECT id FROM embarcaciones WHERE matricula=%s AND id!=%s"
            r = self.db.execute_query(q, (matricula, excluir_id), fetch=True)
        else:
            q = "SELECT id FROM embarcaciones WHERE matricula=%s"
            r = self.db.execute_query(q, (matricula,), fetch=True)
        return bool(r)

    def obtener_para_combo(self):
        """Retorna lista (id, nombre) para ComboBox."""
        q = "SELECT id, nombre FROM embarcaciones WHERE estado='operativa' ORDER BY nombre"
        return self.db.execute_query(q, fetch=True) or []

    def verificar_disponibilidad(self, embarcacion_id):
        """Llama a la función MySQL FN_VerificarDisponibilidadEmbarcacion."""
        q = "SELECT FN_VerificarDisponibilidadEmbarcacion(%s) AS disponible"
        r = self.db.execute_query(q, (embarcacion_id,), fetch=True)
        return bool(r[0]['disponible']) if r else False
