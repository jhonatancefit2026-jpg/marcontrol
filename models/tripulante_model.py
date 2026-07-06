"""
Modelo de Tripulantes — acceso a datos con MySQL
"""
from database import Database


class TripulanteModel:
    def __init__(self):
        self.db = Database.get_instance()

    def obtener_todos(self):
        query = """
            SELECT id, dni, nombres, apellidos, fecha_nacimiento,
                   direccion, telefono, libreta_embarque, cargo,
                   experiencia_anios, estado_salud, disponible
            FROM tripulantes
            ORDER BY apellidos, nombres
        """
        return self.db.execute_query(query, fetch=True) or []

    def obtener_por_id(self, tripulante_id):
        query = "SELECT * FROM tripulantes WHERE id = %s"
        r = self.db.execute_query(query, (tripulante_id,), fetch=True)
        return r[0] if r else None

    def crear(self, datos):
        query = """
            INSERT INTO tripulantes
              (dni, nombres, apellidos, fecha_nacimiento, direccion,
               telefono, libreta_embarque, cargo, experiencia_anios,
               estado_salud, disponible, foto_ruta)
            VALUES
              (%(dni)s, %(nombres)s, %(apellidos)s, %(fecha_nacimiento)s, %(direccion)s,
               %(telefono)s, %(libreta_embarque)s, %(cargo)s, %(experiencia_anios)s,
               %(estado_salud)s, %(disponible)s, %(foto_ruta)s)
        """
        return self.db.execute_query(query, datos)

    def actualizar(self, tripulante_id, datos):
        query = """
            UPDATE tripulantes SET
              dni=%(dni)s, nombres=%(nombres)s, apellidos=%(apellidos)s,
              fecha_nacimiento=%(fecha_nacimiento)s, direccion=%(direccion)s,
              telefono=%(telefono)s, libreta_embarque=%(libreta_embarque)s,
              cargo=%(cargo)s, experiencia_anios=%(experiencia_anios)s,
              estado_salud=%(estado_salud)s, disponible=%(disponible)s,
              foto_ruta=%(foto_ruta)s
            WHERE id=%(id)s
        """
        datos['id'] = tripulante_id
        return self.db.execute_query(query, datos)

    def eliminar(self, tripulante_id):
        return self.db.execute_query("DELETE FROM tripulantes WHERE id=%s", (tripulante_id,))

    def verificar_dni_duplicado(self, dni, excluir_id=None):
        if excluir_id:
            r = self.db.execute_query(
                "SELECT id FROM tripulantes WHERE dni=%s AND id!=%s",
                (dni, excluir_id), fetch=True)
        else:
            r = self.db.execute_query(
                "SELECT id FROM tripulantes WHERE dni=%s", (dni,), fetch=True)
        return bool(r)

    def asignar_a_embarcacion(self, embarcacion_id, tripulante_id):
        """Llama al Stored Procedure AsignarTripulantes."""
        return self.db.call_procedure('AsignarTripulantes', (embarcacion_id, tripulante_id))

    def obtener_certificados(self, tripulante_id):
        q = """
            SELECT c.codigo, c.descripcion,
                   tc.fecha_emision, tc.fecha_vencimiento
            FROM tripulante_certificados tc
            JOIN certificados c ON tc.certificado_id = c.id
            WHERE tc.tripulante_id = %s
        """
        return self.db.execute_query(q, (tripulante_id,), fetch=True) or []

    def obtener_para_combo(self):
        q = """SELECT id, CONCAT(nombres, ' ', apellidos) AS nombre_completo
               FROM tripulantes WHERE disponible=1 ORDER BY apellidos"""
        return self.db.execute_query(q, fetch=True) or []
