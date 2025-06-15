# Updated schemas.py with proper datetime handling and imports
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal  # Add this import

class AuthorResponse(BaseModel):
    id: int  # Non-optional for responses
    first_name: str
    last_name: str
    nationality_id: Optional[int] = None

class AuthorCreate(BaseModel):
    first_name: str
    last_name: str
    nationality_id: Optional[int] = None

class BookResponse(BaseModel):
    id: int  # Non-optional for responses
    title: str
    author_id: int
    language_id: int
    published_year: int
    pages: int
    isbn: str
    description: Optional[str] = None
    # Add missing fields expected by Android
    cover_url: Optional[str] = None
    categories: Optional[List[str]] = Field(default_factory=list)
    average_rating: Optional[float] = None
    author: Optional[AuthorResponse] = None  # Nested author

class BookCreate(BaseModel):
    title: str
    author_id: int
    language_id: int
    published_year: int
    pages: int
    isbn: str
    description: Optional[str] = None

class GenreResponse(BaseModel):
    id: int
    name: str

class BookItemResponse(BaseModel):
    id: int
    book_id: int
    status: str

class RentalResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    book_item_id: Optional[int] = None
    rented_at: Optional[datetime] = None  # Changed from str to datetime
    returned_at: Optional[datetime] = None  # Changed from str to datetime

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: Optional[str] = "user"
    # Don't return password_hash in responses!

class UserCreate(BaseModel):
    username: str
    email: str
    password_hash: str
    role: Optional[str] = "user"

class GenreCreate(BaseModel):
    name: str

class BookItemCreate(BaseModel):
    book_id: int
    status: str

class RentalCreate(BaseModel):
    user_id: Optional[int] = None
    book_item_id: Optional[int] = None
    rented_at: Optional[datetime] = None  # Changed from str to datetime
    returned_at: Optional[datetime] = None  # Changed from str to datetime

# Purchase schemas
class PurchaseBase(BaseModel):
    user_id: int
    book_id: int
    price: Decimal

class PurchaseCreate(PurchaseBase):
    pass

class PurchaseResponse(PurchaseBase):
    id: int
    purchase_date: datetime

    class Config:
        from_attributes = True

# Extended purchase response with book and user details
class PurchaseDetailResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    price: Decimal
    purchase_date: datetime
    # Book details
    book_title: str
    book_author: str
    # User details
    username: str

    class Config:
        from_attributes = True

# User's library response (books owned by user)
class UserLibraryResponse(BaseModel):
    book_id: int
    title: str
    author: str
    purchase_date: datetime
    price: Decimal

    class Config:
        from_attributes = True