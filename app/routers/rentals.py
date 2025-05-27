from fastapi import APIRouter
from app.db.connection import get_read_connection, get_write_connection
from app.models.schemas import Rental

router = APIRouter(prefix="/rentals", tags=["rentals"])

@router.get("/")
def get_all():
    conn = get_read_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM rentals")
    result = cursor.fetchall()
    conn.close()
    return result

@router.get("/{id}")
def get_by_id(id: int):
    conn = get_read_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM rentals WHERE id = %s", (id,))
    result = cursor.fetchone()
    conn.close()
    return result

@router.post("/")
def create(item: Rental):
    conn = get_write_connection()
    cursor = conn.cursor()
    data = item.dict()
    keys = list(data.keys())
    values = list(data.values())
    cursor.execute(
        "INSERT INTO rentals (" + ", ".join(keys) + ") VALUES (" + ", ".join(["%s"] * len(keys)) + ")",
        values
    )
    conn.commit()
    conn.close()
    return {"message": "Rental created successfully"}
