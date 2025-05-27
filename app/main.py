from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routerów z podmodułów
from app.routers import books, users, authors, genres, rentals

app = FastAPI(title="Biblioteka API")

# Middleware CORS – dla frontendu mobilnego
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rejestracja routerów (endpointów)
app.include_router(books.router, prefix="/books", tags=["Books"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(authors.router, prefix="/authors", tags=["Authors"])
app.include_router(genres.router, prefix="/genres", tags=["Genres"])
app.include_router(rentals.router, prefix="/rentals", tags=["Rentals"])
