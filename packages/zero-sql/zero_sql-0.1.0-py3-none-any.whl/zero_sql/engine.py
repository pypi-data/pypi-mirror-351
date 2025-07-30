import sqlite3
from typing import Optional, Union, List, Dict, Any

class ZeroSQL:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _execute(self, query: str, params: tuple = ()) -> List[tuple]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                if query.strip().upper().startswith("SELECT"):
                    return cursor.fetchall()
                conn.commit()
                return []
        except Exception as e:
            raise RuntimeError(f"Database error: {e}")

    def get(self, table: str, columns: Optional[List[str]] = None,
            where: Optional[Dict[str, Any]] = None,
            like: Optional[Dict[str, str]] = None,
            limit: Optional[int] = None, order_by: Optional[str] = None) -> List[tuple]:
        cols = ", ".join(columns) if columns else "*"
        query = f"SELECT {cols} FROM {table}"
        params = []

        if where:
            where_clause = " AND ".join([f"{k}=?" for k in where])
            query += f" WHERE {where_clause}"
            params.extend(where.values())

        if like:
            like_clause = " AND ".join([f"{k} LIKE ?" for k in like])
            if "WHERE" in query:
                query += f" AND {like_clause}"
            else:
                query += f" WHERE {like_clause}"
            params.extend([f"%{v}%" for v in like.values()])

        if order_by:
            query += f" ORDER BY {order_by}"

        if limit:
            query += f" LIMIT {limit}"

        return self._execute(query, tuple(params))

    def add(self, table: str, data: Dict[str, Any]) -> None:
        keys = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        query = f"INSERT INTO {table} ({keys}) VALUES ({placeholders})"
        self._execute(query, tuple(data.values()))

    def update(self, table: str, where: Dict[str, Any], data: Dict[str, Any]) -> None:
        set_clause = ", ".join([f"{k}=?" for k in data])
        where_clause = " AND ".join([f"{k}=?" for k in where])
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        self._execute(query, tuple(data.values()) + tuple(where.values()))

    def remove(self, table: str, where: Dict[str, Any]) -> None:
        where_clause = " AND ".join([f"{k}=?" for k in where])
        query = f"DELETE FROM {table} WHERE {where_clause}"
        self._execute(query, tuple(where.values()))

    def raw(self, query: str, params: tuple = ()) -> Union[List[tuple], None]:
        return self._execute(query, params)

    def create_table(self, table_name: str, columns: Dict[str, str], constraints: Optional[str] = None) -> None:
        cols = ", ".join([f"{k} {v}" for k, v in columns.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({cols}"
        if constraints:
            query += f", {constraints}"
        query += ")"
        self._execute(query)

    def list_tables(self) -> List[str]:
        result = self._execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [row[0] for row in result]

    def drop_table(self, table_name: str) -> None:
        query = f"DROP TABLE IF EXISTS {table_name}"
        self._execute(query)

    def rename_table(self, old_name: str, new_name: str) -> None:
        query = f"ALTER TABLE {old_name} RENAME TO {new_name}"
        self._execute(query)
