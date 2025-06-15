# Updated book_items router
from fastapi import APIRouter, HTTPException
from app.db.connection import get_read_connection, get_write_connection
from app.models.schemas import BookItemResponse, BookItemCreate
from typing import List

router = APIRouter(prefix="/book_items", tags=["book_items"])


@router.get("/", response_model=List[BookItemResponse])
def get_all():
    conn = get_read_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM book_items")
    results = cursor.fetchall()
    conn.close()

    return [BookItemResponse(**row) for row in results]


@router.get("/{id}", response_model=BookItemResponse)
def get_by_id(id: int):
    conn = get_read_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM book_items WHERE id = %s", (id,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        raise HTTPException(status_code=404, detail="Book item not found")

    return BookItemResponse(**result)


@router.post("/", response_model=dict)
def create(item: BookItemCreate):
    conn = get_write_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO book_items (book_id, status) VALUES (%s, %s)",
        (item.book_id, item.status)
    )
    conn.commit()
    conn.close()
    return {"message": "Book item created successfully"}