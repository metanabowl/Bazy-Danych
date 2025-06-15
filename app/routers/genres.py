# Updated genres router
from fastapi import APIRouter, HTTPException
from app.db.connection import get_read_connection, get_write_connection
from app.models.schemas import GenreResponse, GenreCreate
from typing import List

router = APIRouter(prefix="/genres", tags=["genres"])


@router.get("/", response_model=List[GenreResponse])
def get_all():
    conn = get_read_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM genres")
    results = cursor.fetchall()
    conn.close()

    return [GenreResponse(**row) for row in results]


@router.get("/{id}", response_model=GenreResponse)
def get_by_id(id: int):
    conn = get_read_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM genres WHERE id = %s", (id,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        raise HTTPException(status_code=404, detail="Genre not found")

    return GenreResponse(**result)


@router.post("/", response_model=dict)
def create(item: GenreCreate):
    conn = get_write_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO genres (name) VALUES (%s)",
        (item.name,)
    )
    conn.commit()
    conn.close()
    return {"message": "Genre created successfully"}