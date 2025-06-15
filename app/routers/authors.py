# Updated authors router
from fastapi import APIRouter, HTTPException
from app.db.connection import get_read_connection, get_write_connection
from app.models.schemas import AuthorResponse, AuthorCreate
from typing import List

router = APIRouter(prefix="/authors", tags=["authors"])


@router.get("/", response_model=List[AuthorResponse])
def get_all():
    conn = get_read_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM authors")
    results = cursor.fetchall()
    conn.close()

    return [AuthorResponse(**row) for row in results]


@router.get("/{id}", response_model=AuthorResponse)
def get_by_id(id: int):
    conn = get_read_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM authors WHERE id = %s", (id,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        raise HTTPException(status_code=404, detail="Author not found")

    return AuthorResponse(**result)


@router.post("/", response_model=dict)
def create(item: AuthorCreate):
    conn = get_write_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO authors (first_name, last_name, nationality_id) VALUES (%s, %s, %s)",
        (item.first_name, item.last_name, item.nationality_id)
    )
    conn.commit()
    conn.close()
    return {"message": "Author created successfully"}