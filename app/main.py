from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import books, users, authors, genres, rentals, purchases
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Biblioteka API",
    description="Library Management API",
    version="1.0.0"
)

# Add CORS middleware to allow Android app access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Android app's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "API is running"}

# Include routers
app.include_router(books.router, tags=["Books"])
app.include_router(users.router, tags=["Users"])
app.include_router(authors.router, tags=["Authors"])
app.include_router(genres.router, tags=["Genres"])
app.include_router(rentals.router, tags=["Rentals"])
app.include_router(purchases.router, tags=["Purchases"])


# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Biblioteka API"}