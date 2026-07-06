"""
Módulo de conexión a la base de datos MarControl (MySQL)
Patrón Singleton para reutilizar la conexión
"""
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG


class Database:
    _instance = None

    def __init__(self):
        self.connection = None
        self.connect()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = Database()
        return cls._instance

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            if self.connection.is_connected():
                print("[DB] Conexión exitosa a MarControl")
        except Error as e:
            print(f"[DB ERROR] No se pudo conectar: {e}")
            self.connection = None

    def get_connection(self):
        try:
            if self.connection is None or not self.connection.is_connected():
                self.connect()
        except Exception:
            self.connect()
        return self.connection

    def execute_query(self, query, params=None, fetch=False, many=False):
        """Ejecuta una consulta SQL directa."""
        conn = self.get_connection()
        if not conn:
            return None
        try:
            cursor = conn.cursor(dictionary=True)
            if many:
                cursor.executemany(query, params or [])
            else:
                cursor.execute(query, params or ())
            if fetch:
                result = cursor.fetchall()
                cursor.close()
                return result
            conn.commit()
            last_id = cursor.lastrowid
            cursor.close()
            return last_id
        except Error as e:
            print(f"[DB ERROR] Query falló: {e}\nQuery: {query}\nParams: {params}")
            conn.rollback()
            raise

    def call_procedure(self, proc_name, args=()):
        """Llama a un stored procedure."""
        conn = self.get_connection()
        if not conn:
            raise Exception("Sin conexión a la base de datos")
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.callproc(proc_name, args)
            results = []
            for result in cursor.stored_results():
                results.extend(result.fetchall())
            conn.commit()
            cursor.close()
            return results
        except Error as e:
            print(f"[DB ERROR] Procedure {proc_name} falló: {e}")
            conn.rollback()
            raise

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("[DB] Conexión cerrada")
