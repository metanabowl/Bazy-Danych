# Updated books router
from fastapi import APIRouter, HTTPException
from app.db.connection import get_read_connection, get_write_connection
from app.models.schemas import BookResponse, BookCreate, AuthorResponse
from typing import List

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/", response_model=List[BookResponse])
def get_books():
    conn = get_read_connection()
    cursor = conn.cursor(dictionary=True)

    # Join with authors table to get author info
    cursor.execute("""
        SELECT 
            b.id, b.title, b.author_id, b.language_id, 
            b.published_year, b.pages, b.isbn, b.description,
            a.id as author_id_nested, a.first_name, a.last_name, a.nationality_id
        FROM books b
        LEFT JOIN authors a ON b.author_id = a.id
    """)

    results = cursor.fetchall()
    conn.close()

    books = []
    for row in results:
        book_data = {
            "id": row["id"],
            "title": row["title"],
            "author_id": row["author_id"],
            "language_id": row["language_id"],
            "published_year": row["published_year"],
            "pages": row["pages"],
            "isbn": row["isbn"],
            "description": row["description"],
            "cover_url": None,  # Set default
            "categories": [],  # Set default
            "average_rating": None,  # Set default
            "author": {
                "id": row["author_id_nested"],
                "first_name": row["first_name"],
                "last_name": row["last_name"],
                "nationality_id": row["nationality_id"]
            } if row["author_id_nested"] else None
        }
        books.append(BookResponse(**book_data))

    return books


@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int):
    conn = get_read_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            b.id, b.title, b.author_id, b.language_id, 
            b.published_year, b.pages, b.isbn, b.description,
            a.id as author_id_nested, a.first_name, a.last_name, a.nationality_id
        FROM books b
        LEFT JOIN authors a ON b.author_id = a.id
        WHERE b.id = %s
    """, (book_id,))

    result = cursor.fetchone()
    conn.close()

    if not result:
        raise HTTPException(status_code=404, detail="Book not found")

    book_data = {
        "id": result["id"],
        "title": result["title"],
        "author_id": result["author_id"],
        "language_id": result["language_id"],
        "published_year": result["published_year"],
        "pages": result["pages"],
        "isbn": result["isbn"],
        "description": result["description"],
        "cover_url": None,
        "categories": [],
        "average_rating": None,
        "author": {
            "id": result["author_id_nested"],
            "first_name": result["first_name"],
            "last_name": result["last_name"],
            "nationality_id": result["nationality_id"]
        } if result["author_id_nested"] else None
    }

    return BookResponse(**book_data)


@router.post("/", response_model=dict)
def create_book(book: BookCreate):
    conn = get_write_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO books (title, author_id, language_id, published_year, pages, isbn, description) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (book.title, book.author_id, book.language_id, book.published_year, book.pages, book.isbn, book.description)
    )
    conn.commit()
    conn.close()
    return {"message": "Book created successfully"}