from fastapi import FastAPI
from app.routers import books, users, authors, genres, rentals

app = FastAPI(title="Biblioteka API")

# Remove the prefix parameters since your routers already have prefixes
app.include_router(books.router, tags=["Books"])
app.include_router(users.router, tags=["Users"])
app.include_router(authors.router, tags=["Authors"])
app.include_router(genres.router, tags=["Genres"])
app.include_router(rentals.router, tags=["Rentals"])
