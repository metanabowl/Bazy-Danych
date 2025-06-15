from fastapi import APIRouter
from app.db.connection import get_read_connection, get_write_connection
from app.models.schemas import Author

router = APIRouter(prefix="/authors", tags=["authors"])

# Remove the trailing slash from route definitions
@router.get("")  # Changed from "/" to ""
def get_all():
    conn = get_read_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM authors")
    result = cursor.fetchall()
    conn.close()
    return result

@router.get("/{id}")  # This stays the same
def get_by_id(id: int):
    conn = get_read_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM authors WHERE id = %s", (id,))
    result = cursor.fetchone()
    conn.close()
    return result

@router.post("")  # Changed from "/" to ""
def create(item: Author):
    conn = get_write_connection()
    cursor = conn.cursor()
    data = item.dict()
    keys = list(data.keys())
    values = list(data.values())
    cursor.execute(
        "INSERT INTO authors (" + ", ".join(keys) + ") VALUES (" + ", ".join(["%s"] * len(keys)) + ")",
        values
    )
    conn.commit()
    conn.close()
    return {"message": "Authors created successfully"}