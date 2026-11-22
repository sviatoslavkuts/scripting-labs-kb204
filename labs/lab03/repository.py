from contextlib import closing
from typing import Any

from labs.lab03.database import get_connection


def get_categories() -> list[dict[str, Any]]:
    """Отримаємо список усіх категорій за зростанням id."""
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM categories ORDER BY id ASC")
        rows = cursor.fetchall()
        return [{"id": row[0], "name": row[1]} for row in rows]


def create_category(name: str) -> dict[str, Any]:
    """Ствоюємо нову категорію."""
    with closing(get_connection()) as conn, conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        cat_id = cursor.lastrowid
        return {"id": cat_id, "name": name}


def delete_empty_category(category_id: int) -> bool:
    """Видаляємо порожню категорію (заборонено, якщо є зв'язані записи через ON DELETE RESTRICT)."""
    with closing(get_connection()) as conn, conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM categories WHERE id = ?", (category_id,))
        if not cursor.fetchone():
            return False
        cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        return cursor.rowcount > 0


def get_record_by_id(record_id: int) -> dict[str, Any] | None:
    """Отримаємо один запис за id з'єднанням із категорією (JOIN)."""
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT r.id, r.code, r.title, r.category_id, r.value, r.status, c.name
            FROM records r
            JOIN categories c ON r.category_id = c.id
            WHERE r.id = ?
            """,
            (record_id,),
        )
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "code": row[1],
            "title": row[2],
            "category_id": row[3],
            "value": row[4],
            "status": row[5],
            "category_name": row[6],
        }


def get_records(
    category_id: int | None = None,
    status: str | None = None,
    min_value: float | None = None,
    q: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """Отримаємо список записів із фільтрами, пагінацією та сортуванням за id."""
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        query = """
            SELECT r.id, r.code, r.title, r.category_id, r.value, r.status, c.name
            FROM records r
            JOIN categories c ON r.category_id = c.id
            WHERE 1=1
        """
        params: list[Any] = []

        if category_id is not None:
            query += " AND r.category_id = ?"
            params.append(category_id)

        if status is not None:
            query += " AND r.status = ?"
            params.append(status)

        if min_value is not None:
            query += " AND r.value >= ?"
            params.append(min_value)

        if q is not None:
            query += " AND instr(r.title, ?) > 0"
            params.append(q)

        query += " ORDER BY r.id ASC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()
        result = []
        for row in rows:
            result.append(
                {
                    "id": row[0],
                    "code": row[1],
                    "title": row[2],
                    "category_id": row[3],
                    "value": row[4],
                    "status": row[5],
                    "category_name": row[6],
                }
            )
        return result


def create_record(
    code: str, title: str, category_id: int, value: float, status: str
) -> dict[str, Any]:
    """Створюємо новий запис."""
    with closing(get_connection()) as conn, conn:
        cursor = conn.cursor()
        cursor.execute(
            """
                INSERT INTO records (code, title, category_id, value, status)
                VALUES (?, ?, ?, ?, ?)
                """,
            (code, title, category_id, value, status),
        )
        rec_id = cursor.lastrowid
    return get_record_by_id(rec_id)


def update_record(
    record_id: int, code: str, title: str, category_id: int, value: float, status: str
) -> dict[str, Any] | None:
    """Повністю замінюємо змінювані поля запису за id."""
    with closing(get_connection()) as conn, conn:
        cursor = conn.cursor()
        cursor.execute(
            """
                UPDATE records
                SET code = ?, title = ?, category_id = ?, value = ?, status = ?
                WHERE id = ?
                """,
            (code, title, category_id, value, status, record_id),
        )
        if cursor.rowcount == 0:
            return None
    return get_record_by_id(record_id)


def delete_record(record_id: int) -> bool:
    """Видаляємо запис за id."""
    with closing(get_connection()) as conn, conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM records WHERE id = ?", (record_id,))
        return cursor.rowcount > 0


def bulk_create_records(records_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Пакетне створення записів в одній транзакції (атомарність)."""
    created_records = []
    with closing(get_connection()) as conn, conn:
            cursor = conn.cursor()
            for rec in records_data:
                cursor.execute(
                    """
                    INSERT INTO records (code, title, category_id, value, status)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        rec["code"],
                        rec["title"],
                        rec["category_id"],
                        rec["value"],
                        rec["status"],
                    ),
                )
                rec_id = cursor.lastrowid
                cursor.execute(
                    """
                    SELECT r.id, r.code, r.title, r.category_id, r.value, r.status, c.name
                    FROM records r
                    JOIN categories c ON r.category_id = c.id
                    WHERE r.id = ?
                    """,
                    (rec_id,),
                )
                row = cursor.fetchone()
                created_records.append(
                    {
                        "id": row[0],
                        "code": row[1],
                        "title": row[2],
                        "category_id": row[3],
                        "value": row[4],
                        "status": row[5],
                        "category_name": row[6],
                    }
                )
    return created_records
