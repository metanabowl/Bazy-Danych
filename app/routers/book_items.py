from fastapi import APIRouter
from app.db.connection import get_read_connection, get_write_connection
from app.models.schemas import BookItem

router = APIRouter(prefix="/book_items", tags=["book_items"])

@router.get("/")
def get_all():
    conn = get_read_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM book_items")
    result = cursor.fetchall()
    conn.close()
    return result

@router.get("/{id}")
def get_by_id(id: int):
    conn = get_read_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM book_items WHERE id = %s", (id,))
    result = cursor.fetchone()
    conn.close()
    return result

@router.post("/")
def create(item: BookItem):
    conn = get_write_connection()
    cursor = conn.cursor()
    data = item.dict()
    keys = list(data.keys())
    values = list(data.values())
    cursor.execute(
        "INSERT INTO book_items (" + ", ".join(keys) + ") VALUES (" + ", ".join(["%s"] * len(keys)) + ")",
        values
    )
    conn.commit()
    conn.close()
    return {"message": "Book items created successfully"}
