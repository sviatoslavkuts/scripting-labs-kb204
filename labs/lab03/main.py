from contextlib import asynccontextmanager
from fastapi import FastAPI

from labs.lab03.database import initialize_database
from labs.lab03.routers import categories, records
from shared.student import GROUP_NAME, STUDENT_NAME, VARIANT_NUMBER


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Життєвий цикл застосунку: ініціалізація бази даних при запуску."""
    initialize_database()
    yield


app = FastAPI(
    title="Реєстр ризиків контейнерної конфігурації (Lab 3)",
    description="Сервіс обліку результатів перевірки конфігурації контейнерного середовища. Одиниця вимірювання: score.",
    version="1.0.0",
    lifespan=lifespan,
)

# Підключення роутерів
app.include_router(categories.router)
app.include_router(records.router)


@app.get("/ping", tags=["System"])
def ping():
    """Перевірка доступності API."""
    return {"status": "ok"}


@app.get("/student", tags=["System"])
def get_student_info():
    """Повертаємо персональні дані студента з shared/student.py."""
    return {
        "student_name": STUDENT_NAME,
        "group_name": GROUP_NAME,
        "variant_number": VARIANT_NUMBER,
    }