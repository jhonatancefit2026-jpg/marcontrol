"""
Modelo de Procesamiento — usa Stored Procedure ProcesarLotePescado para INSERT
"""
from database import Database


class ProcesamientoModel:
    def __init__(self):
        self.db = Database.get_instance()

    def obtener_todos(self):
        query = """
            SELECT p.id, p.lote_codigo,
                   c.numero_registro AS captura_num,
                   es.nombre AS especie,
                   p.fecha,
                   p.metodo_procesamiento,
                   p.materia_prima_kg,
                   p.rendimiento,
                   p.tipo_producto_final,
                   p.cantidad_producida_kg,
                   p.responsable
            FROM procesamiento p
            LEFT JOIN capturas c ON p.captura_id = c.id
            LEFT JOIN especies es ON p.especie_id = es.id
            ORDER BY p.fecha DESC
        """
        return self.db.execute_query(query, fetch=True) or []

    def obtener_por_id(self, proc_id):
        q = "SELECT * FROM procesamiento WHERE id = %s"
        r = self.db.execute_query(q, (proc_id,), fetch=True)
        return r[0] if r else None

    def registrar_lote(self, captura_id, rendimiento, calidad):
        """Llama al Stored Procedure ProcesarLotePescado."""
        return self.db.call_procedure(
            'ProcesarLotePescado',
            (int(captura_id), float(rendimiento), str(calidad))
        )

    def crear_completo(self, datos):
        """Inserta directamente un registro de procesamiento completo."""
        query = """
            INSERT INTO procesamiento
              (lote_codigo, captura_id, fecha, especie_id,
               materia_prima_kg, metodo_procesamiento, rendimiento,
               tipo_producto_final, cantidad_producida_kg, responsable)
            VALUES
              (%(lote_codigo)s, %(captura_id)s, %(fecha)s, %(especie_id)s,
               %(materia_prima_kg)s, %(metodo_procesamiento)s, %(rendimiento)s,
               %(tipo_producto_final)s, %(cantidad_producida_kg)s, %(responsable)s)
        """
        return self.db.execute_query(query, datos)

    def actualizar(self, proc_id, datos):
        query = """
            UPDATE procesamiento SET
              lote_codigo=%(lote_codigo)s,
              captura_id=%(captura_id)s,
              fecha=%(fecha)s,
              especie_id=%(especie_id)s,
              materia_prima_kg=%(materia_prima_kg)s,
              metodo_procesamiento=%(metodo_procesamiento)s,
              rendimiento=%(rendimiento)s,
              tipo_producto_final=%(tipo_producto_final)s,
              cantidad_producida_kg=%(cantidad_producida_kg)s,
              responsable=%(responsable)s
            WHERE id=%(id)s
        """
        datos['id'] = proc_id
        return self.db.execute_query(query, datos)

    def eliminar(self, proc_id):
        return self.db.execute_query("DELETE FROM procesamiento WHERE id=%s", (proc_id,))

    def obtener_capturas_combo(self):
        q = "SELECT id, numero_registro FROM capturas ORDER BY fecha_inicio DESC"
        return self.db.execute_query(q, fetch=True) or []

    def obtener_especies_combo(self):
        return self.db.execute_query("SELECT id, nombre FROM especies ORDER BY nombre", fetch=True) or []

    def generar_lote(self):
        from datetime import datetime
        fecha = datetime.now().strftime('%Y%m%d')
        r = self.db.execute_query("SELECT COUNT(*)+1 AS n FROM procesamiento", fetch=True)
        n = r[0]['n'] if r else 1
        return f"LOT-{fecha}-{n:04d}"

    def calcular_cantidad(self, materia_prima_kg, rendimiento):
        """Calcula cantidad producida según rendimiento."""
        try:
            return round(float(materia_prima_kg) * float(rendimiento) / 100, 2)
        except Exception:
            return 0.0
