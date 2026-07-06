"""
Modelo de Capturas — usa Stored Procedure RegistrarCaptura para INSERT
"""
from database import Database


class CapturaModel:
    def __init__(self):
        self.db = Database.get_instance()

    def obtener_todos(self):
        query = """
            SELECT c.id, c.numero_registro,
                   e.nombre AS embarcacion,
                   z.nombre AS zona,
                   c.fecha_inicio, c.fecha_fin,
                   c.metodo_pesca, c.condiciones_climaticas,
                   GROUP_CONCAT(es.nombre SEPARATOR ', ') AS especies,
                   COALESCE(SUM(cd.cantidad_kg), 0) AS total_kg
            FROM capturas c
            JOIN embarcaciones e ON c.embarcacion_id = e.id
            JOIN zonas_pesca z   ON c.zona_id = z.id
            LEFT JOIN captura_detalle cd ON cd.captura_id = c.id
            LEFT JOIN especies es ON cd.especie_id = es.id
            GROUP BY c.id
            ORDER BY c.fecha_inicio DESC
        """
        return self.db.execute_query(query, fetch=True) or []

    def obtener_por_id(self, captura_id):
        q = """
            SELECT c.*, e.nombre AS nom_embarcacion, z.nombre AS nom_zona
            FROM capturas c
            JOIN embarcaciones e ON c.embarcacion_id = e.id
            JOIN zonas_pesca z   ON c.zona_id = z.id
            WHERE c.id = %s
        """
        r = self.db.execute_query(q, (captura_id,), fetch=True)
        return r[0] if r else None

    def registrar(self, embarcacion_id, zona_id, fecha_inicio, fecha_fin,
                  especie_id, cantidad_kg):
        """Llama al Stored Procedure RegistrarCaptura."""
        return self.db.call_procedure(
            'RegistrarCaptura',
            (embarcacion_id, zona_id, fecha_inicio, fecha_fin, especie_id, float(cantidad_kg))
        )

    def actualizar(self, captura_id, datos):
        query = """
            UPDATE capturas SET
              embarcacion_id=%(embarcacion_id)s,
              zona_id=%(zona_id)s,
              fecha_inicio=%(fecha_inicio)s,
              fecha_fin=%(fecha_fin)s,
              metodo_pesca=%(metodo_pesca)s,
              condiciones_climaticas=%(condiciones_climaticas)s
            WHERE id=%(id)s
        """
        datos['id'] = captura_id
        return self.db.execute_query(query, datos)

    def eliminar(self, captura_id):
        self.db.execute_query("DELETE FROM captura_detalle WHERE captura_id=%s", (captura_id,))
        return self.db.execute_query("DELETE FROM capturas WHERE id=%s", (captura_id,))

    def obtener_zonas(self):
        return self.db.execute_query("SELECT id, nombre FROM zonas_pesca ORDER BY nombre", fetch=True) or []

    def obtener_especies(self):
        return self.db.execute_query("SELECT id, nombre FROM especies ORDER BY nombre", fetch=True) or []

    def calcular_valor(self, captura_id):
        """Llama a FN_CalcularValorCaptura."""
        r = self.db.execute_query(
            "SELECT FN_CalcularValorCaptura(%s) AS valor", (captura_id,), fetch=True)
        return float(r[0]['valor']) if r and r[0]['valor'] else 0.0

    def obtener_detalle(self, captura_id):
        q = """
            SELECT es.nombre AS especie, cd.cantidad_kg
            FROM captura_detalle cd
            JOIN especies es ON cd.especie_id = es.id
            WHERE cd.captura_id = %s
        """
        return self.db.execute_query(q, (captura_id,), fetch=True) or []

    def generar_numero_registro(self):
        """Genera un número de registro único."""
        from datetime import datetime
        fecha = datetime.now().strftime('%Y%m%d')
        q = "SELECT COUNT(*)+1 AS seq FROM capturas WHERE DATE(fecha_inicio)=CURDATE()"
        r = self.db.execute_query(q, fetch=True)
        seq = r[0]['seq'] if r else 1
        return f"CAP-{fecha}-{seq:02d}"
