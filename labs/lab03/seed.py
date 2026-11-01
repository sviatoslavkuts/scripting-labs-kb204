import json
import sqlite3
from contextlib import closing
from pathlib import Path

from database import get_connection, initialize_database

BASE_DIR = Path(__file__).resolve().parent
SEED_PATH = BASE_DIR / "data" / "seed.json"


def seed_database() -> None:
    """Заповнюємо базу початковими даними з JSON в одній транзакції."""
    initialize_database()

    if not SEED_PATH.exists():
        print(f"[-] Файл початкових даних не знайдено: {SEED_PATH}")
        return

    data = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    categories = data.get("categories", [])
    records = data.get("records", [])

    with closing(get_connection()) as connection:
        try:
            with connection:
                # Перевіряємо, чи база вже заповнена
                cursor = connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM categories")
                cat_count = cursor.fetchone()[0]

                if cat_count > 0:
                    print("[!] База даних уже містить дані. Початкове заповнення пропущено.")
                    return

                # Вставка категорій
                for cat in categories:
                    connection.execute(
                        "INSERT INTO categories (id, name) VALUES (?, ?)",
                        (cat["id"], cat["name"]),
                    )

                # Вставка записів
                for rec in records:
                    connection.execute(
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

            print("[+] Базу даних успішно заповнено початковими даними з seed.json!")
        except sqlite3.IntegrityError as e:
            print(f"[-] Помилка цілісності під час сидингу (транзакцію скасовано): {e}")
            raise
        except sqlite3.Error as e:
            print(f"[-] Помилка бази даних: {e}")
            raise


if __name__ == "__main__":
    seed_database()