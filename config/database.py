import json
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from pathlib import Path
from contextlib import contextmanager
from src.utils.logger import get_logger

logger = get_logger(__name__)

class DatabaseConnection:
    _instance = None
    _pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._pool is None:
            self._initialize_pool()

    def _initialize_pool(self):
        credentials = self._load_credentials()

        try:
            self._pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                host=credentials["host"],
                port=credentials["port"],
                database=credentials["database"],
                user=credentials["user"],
                password=credentials["password"]
            )
            logger.info("Database connection pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise

    def _load_credentials(self):
        credentials_path = Path(__file__).parent / "db_credentials.json"

        if not credentials_path.exists():
            logger.warning("Credentials file not found, using defaults")
            return {
                "host": "localhost",
                "port": 5432,
                "database": "tenis_machine",
                "user": "postgres",
                "password": "postgres"
            }

        with open(credentials_path, 'r') as f:
            return json.load(f)

    @contextmanager
    def get_connection(self):
        conn = self._pool.getconn()
        try:
            yield conn
        finally:
            self._pool.putconn(conn)

    @contextmanager
    def get_cursor(self, dict_cursor=True):
        with self.get_connection() as conn:
            cursor_factory = RealDictCursor if dict_cursor else None
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Database error: {e}")
                raise
            finally:
                cursor.close()

    def execute_query(self, query, params=None, fetch=False, dict_cursor=True):
        with self.get_cursor(dict_cursor=dict_cursor) as cursor:
            cursor.execute(query, params)
            if fetch:
                return cursor.fetchall()
            return cursor.rowcount

    def execute_many(self, query, params_list):
        with self.get_cursor(dict_cursor=False) as cursor:
            cursor.executemany(query, params_list)
            return cursor.rowcount

    def close_all_connections(self):
        if self._pool:
            self._pool.closeall()
            logger.info("All database connections closed")

def get_db():
    return DatabaseConnection()
