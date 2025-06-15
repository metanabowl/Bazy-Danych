# Updated users router
from fastapi import APIRouter, HTTPException
from app.db.connection import get_read_connection, get_write_connection
from app.models.schemas import UserResponse, UserCreate
from typing import List

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserResponse])
def get_all():
    conn = get_read_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username, email, role FROM users")  # Don't return password_hash
    results = cursor.fetchall()
    conn.close()

    return [UserResponse(**row) for row in results]


@router.get("/{id}", response_model=UserResponse)
def get_by_id(id: int):
    conn = get_read_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username, email, role FROM users WHERE id = %s", (id,))  # Don't return password_hash
    result = cursor.fetchone()
    conn.close()

    if not result:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(**result)


@router.post("/", response_model=dict)
def create(item: UserCreate):
    conn = get_write_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, email, password_hash, role) VALUES (%s, %s, %s, %s)",
        (item.username, item.email, item.password_hash, item.role)
    )
    conn.commit()
    conn.close()
    return {"message": "User created successfully"}