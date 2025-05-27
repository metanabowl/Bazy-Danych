from fastapi import APIRouter
from app.db.connection import get_read_connection, get_write_connection
from app.models.schemas import Book

router = APIRouter(prefix="/books", tags=["books"])

@router.get("/")
def get_books():
    conn = get_read_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books")
    result = cursor.fetchall()
    conn.close()
    return result

@router.get("/{book_id}")
def get_book(book_id: int):
    conn = get_read_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
    result = cursor.fetchone()
    conn.close()
    return result

@router.post("/")
def create_book(book: Book):
    conn = get_write_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO books (id, title, author_id, language_id, published_year, pages, isbn, description) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (book.id, book.title, book.author_id, book.language_id, book.published_year, book.pages, book.isbn, book.description)
    )
    conn.commit()
    conn.close()
    return {"message": "Book created successfully"}
