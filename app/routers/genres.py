from fastapi import APIRouter
from app.db.connection import get_read_connection, get_write_connection
from app.models.schemas import Genre

router = APIRouter(prefix="/genres", tags=["genres"])

@router.get("/")
def get_all():
    conn = get_read_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM genres")
    result = cursor.fetchall()
    conn.close()
    return result

@router.get("/{id}")
def get_by_id(id: int):
    conn = get_read_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM genres WHERE id = %s", (id,))
    result = cursor.fetchone()
    conn.close()
    return result

@router.post("/")
def create(item: Genre):
    conn = get_write_connection()
    cursor = conn.cursor()
    data = item.dict()
    keys = list(data.keys())
    values = list(data.values())
    cursor.execute(
        "INSERT INTO genres (" + ", ".join(keys) + ") VALUES (" + ", ".join(["%s"] * len(keys)) + ")",
        values
    )
    conn.commit()
    conn.close()
    return {"message": "Genres created successfully"}
