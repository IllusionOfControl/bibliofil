import sqlite3

from bibliofil.models import BiblioFile, BiblioExtStat


class Database:
    def __init__(self, db_path: str):
        self._conn = sqlite3.connect(db_path)
        self._conn.execute("PRAGMA foreign_keys = ON")
        self._prepare_schema()

    def _prepare_schema(self):
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, extension TEXT, path TEXT, size INTEGER,
                md5 TEXT, created_at DATETIME, archive_id INTEGER,
                is_archive INTEGER,
                FOREIGN KEY (archive_id) REFERENCES files (id) ON DELETE CASCADE
            )
        """)
        self._conn.execute("CREATE INDEX IF NOT EXISTS idx_md5 ON files(md5)")

    def insert_file(self, biblio_file: BiblioFile) -> int:
        stmt = (
            "INSERT INTO files (name, extension, path, size, md5, created_at, archive_id, is_archive)"
            + "VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        )
        cursor = self._conn.cursor()
        cursor.execute(stmt, biblio_file.to_tuple())
        entity_id = cursor.lastrowid

        self._conn.commit()
        return entity_id

    def get_total_size(self) -> int:
        stmt = "SELECT SUM(size) FROM files"
        cursor = self._conn.cursor()
        cursor.execute(stmt)
        return cursor.fetchone()[0] or 1

    def get_extension_stats(self, limit: int) -> list[BiblioExtStat]:
        stmt = "SELECT extension, COUNT(*), SUM(size) FROM files GROUP BY extension ORDER BY SUM(size) DESC"
        if limit > 0:
            stmt += " LIMIT {}".format(limit)

        cursor = self._conn.cursor()
        cursor.execute(stmt)
        return [BiblioExtStat(*row) for row in cursor.fetchall()]

    def get_duplicates(
        self, include: list[str], exclude: list[str], min_size: int, max_size: int
    ) -> list[BiblioFile]:
        where_clause = "WHERE md5 IS NOT NULL AND md5 != ''"
        params = []

        if include:
            where_clause += f" AND extension IN ({','.join(['?'] * len(include))})"
            params.extend(include)
        if exclude:
            where_clause += f" AND extension NOT IN ({','.join(['?'] * len(exclude))})"
            params.extend(exclude)
        if min_size > 0:
            where_clause += f" AND size >= ?"
            params.append(min_size)
        if max_size > 0:
            where_clause += f" AND size <= ?"
            params.append(max_size)

        where_clause += f" AND archive_id IS NULL"

        stmt = f"""
            WITH dh AS (SELECT md5 FROM files {where_clause} GROUP BY md5 HAVING COUNT(*) > 1)
            SELECT f.id, f.name, f.extension, f.path, f.size, f.md5, f.archive_id 
            FROM files f JOIN dh ON f.md5 = dh.md5 
            ORDER BY f.size DESC, f.md5, f.created_at
        """
        cursor = self._conn.cursor()
        cursor.execute(stmt, params)
        return [BiblioFile(*row) for row in cursor.fetchall()]

    def delete_file(self, entity_id: int):
        stmt = "DELETE FROM files WHERE id = ? OR archive_id = ?"
        cursor = self._conn.cursor()
        cursor.execute(stmt, [entity_id, entity_id])
        self._conn.commit()
