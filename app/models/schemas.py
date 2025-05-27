from pydantic import BaseModel
from typing import Optional

class Book(BaseModel):
    id: Optional[int]
    title: str
    author_id: int
    language_id: int
    published_year: int
    pages: int
    isbn: str
    description: Optional[str]

class User(BaseModel):
    id: Optional[int]
    username: str
    email: str
    password_hash: str
    role: Optional[str] = "user"

class Author(BaseModel):
    id: Optional[int]
    first_name: str
    last_name: str
    nationality_id: Optional[int]

class Genre(BaseModel):
    id: Optional[int]
    name: str

class BookItem(BaseModel):
    id: Optional[int]
    book_id: Optional[int]
    status: str  # 'available', 'borrowed', 'reserved'

class Rental(BaseModel):
    id: Optional[int]
    user_id: Optional[int]
    book_item_id: Optional[int]
    rented_at: Optional[str]
    returned_at: Optional[str]
