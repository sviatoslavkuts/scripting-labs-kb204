import sqlite3
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from labs.lab03 import repository
from labs.lab03.schemas import RecordCreate, RecordRead, RecordReplace

router = APIRouter(prefix="/records", tags=["Records"])


@router.get("", response_model=List[RecordRead])
def get_records(
    category_id: Optional[int] = Query(default=None, gt=0),
    status: Optional[str] = None,
    min_value: Optional[float] = Query(default=None, ge=0, le=10),
    q: Optional[str] = Query(default=None, min_length=1, max_length=120),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """Отримаємо список записів із фільтрами та пагінацією."""
    return repository.get_records(
        category_id=category_id,
        status=status,
        min_value=min_value,
        q=q,
        limit=limit,
        offset=offset,
    )


@router.get("/{record_id}", response_model=RecordRead)
def get_record(record_id: int):
    """Отримаємо один запис за id."""
    if record_id <= 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Некоректний ID.")
    
    record = repository.get_record_by_id(record_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Запис не знайдено.")
    return record


@router.post("", response_model=RecordRead, status_code=status.HTTP_201_CREATED)
def create_record(record: RecordCreate):
    """Створюємо новий запис."""
    try:
        return repository.create_record(
            code=record.code,
            title=record.title,
            category_id=record.category_id,
            value=record.value,
            status=record.status,
        )
    except sqlite3.IntegrityError as e:
        err_msg = str(e).lower()
        if "foreign key" in err_msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Вказана категорія не існує.")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Дублікат унікального значення (code).")


@router.put("/{record_id}", response_model=RecordRead)
def update_record(record_id: int, record: RecordReplace):
    """Повністю замінюємо змінювані поля запису за id."""
    if record_id <= 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Некоректний ID.")

    try:
        updated = repository.update_record(
            record_id=record_id,
            code=record.code,
            title=record.title,
            category_id=record.category_id,
            value=record.value,
            status=record.status,
        )
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Запис не знайдено.")
        return updated
    except sqlite3.IntegrityError as e:
        err_msg = str(e).lower()
        if "foreign key" in err_msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Вказана категорія не існує.")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Дублікат унікального значення (code).")


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(record_id: int):
    """Видалити запис за id."""
    if record_id <= 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Некоректний ID.")

    success = repository.delete_record(record_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Запис не знайдено.")


@router.post("/bulk", response_model=List[RecordRead], status_code=status.HTTP_201_CREATED)
def bulk_create_records(records: List[RecordCreate]):
    """Пакетне створення записів з атомарним збереженням (1-100 елементів)."""
    if not (1 <= len(records) <= 100):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Кількість елементів у пакеті має бути від 1 до 100.",
        )

    records_data = [
        {
            "code": r.code,
            "title": r.title,
            "category_id": r.category_id,
            "value": r.value,
            "status": r.status,
        }
        for r in records
    ]

    try:
        return repository.bulk_create_records(records_data)
    except sqlite3.IntegrityError as e:
        err_msg = str(e).lower()
        if "foreign key" in err_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Один із записів посилається на неіснуючу категорію (транзакцію скасовано).",
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Виявлено дублікат коду всередині пакету або в базі (транзакцію скасовано).",
        )