# Create this as app/routers/purchases.py

from fastapi import APIRouter, HTTPException
from app.db.connection import get_read_connection, get_write_connection
from app.models.schemas import (
    PurchaseResponse,
    PurchaseCreate,
    PurchaseDetailResponse,
    UserLibraryResponse
)
from typing import List
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/purchases", tags=["Purchases"])


@router.get("/", response_model=List[PurchaseDetailResponse])
def get_all_purchases():
    """Get all purchases with book and user details"""
    conn = None
    cursor = None
    try:
        logger.info("Attempting to fetch all purchases")
        conn = get_read_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT 
            p.id, p.user_id, p.book_id, p.price, p.purchase_date,
            b.title as book_title,
            CONCAT(a.first_name, ' ', a.last_name) as book_author,
            u.username
        FROM purchases p
        JOIN books b ON p.book_id = b.id
        JOIN authors a ON b.author_id = a.id
        JOIN users u ON p.user_id = u.id
        ORDER BY p.purchase_date DESC
        """

        cursor.execute(query)
        results = cursor.fetchall()

        logger.info(f"Found {len(results)} purchases")
        return [PurchaseDetailResponse(**row) for row in results]

    except Exception as e:
        logger.error(f"Error in get_all_purchases: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@router.get("/{purchase_id}", response_model=PurchaseDetailResponse)
def get_purchase_by_id(purchase_id: int):
    """Get a specific purchase by ID"""
    conn = None
    cursor = None
    try:
        logger.info(f"Attempting to fetch purchase with id: {purchase_id}")
        conn = get_read_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT 
            p.id, p.user_id, p.book_id, p.price, p.purchase_date,
            b.title as book_title,
            CONCAT(a.first_name, ' ', a.last_name) as book_author,
            u.username
        FROM purchases p
        JOIN books b ON p.book_id = b.id
        JOIN authors a ON b.author_id = a.id
        JOIN users u ON p.user_id = u.id
        WHERE p.id = %s
        """

        cursor.execute(query, (purchase_id,))
        result = cursor.fetchone()

        if not result:
            logger.warning(f"Purchase with id {purchase_id} not found")
            raise HTTPException(status_code=404, detail="Purchase not found")

        logger.info(f"Found purchase: {result}")
        return PurchaseDetailResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_purchase_by_id: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@router.get("/user/{user_id}/library", response_model=List[UserLibraryResponse])
def get_user_library(user_id: int):
    """Get all books purchased by a specific user"""
    conn = None
    cursor = None
    try:
        logger.info(f"Attempting to fetch library for user: {user_id}")
        conn = get_read_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT 
            b.id as book_id,
            b.title,
            CONCAT(a.first_name, ' ', a.last_name) as author,
            p.purchase_date,
            p.price
        FROM purchases p
        JOIN books b ON p.book_id = b.id
        JOIN authors a ON b.author_id = a.id
        WHERE p.user_id = %s
        ORDER BY p.purchase_date DESC
        """

        cursor.execute(query, (user_id,))
        results = cursor.fetchall()

        logger.info(f"Found {len(results)} books in user {user_id}'s library")
        return [UserLibraryResponse(**row) for row in results]

    except Exception as e:
        logger.error(f"Error in get_user_library: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@router.post("/", response_model=dict)
def create_purchase(purchase: PurchaseCreate):
    """Create a new purchase"""
    conn = None
    cursor = None
    try:
        logger.info(f"Attempting to create purchase: {purchase}")
        conn = get_write_connection()
        cursor = conn.cursor()

        # First check if book exists
        cursor.execute("SELECT id FROM books WHERE id = %s", (purchase.book_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Book not found")

        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE id = %s", (purchase.user_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="User not found")

        # Create the purchase
        cursor.execute(
            "INSERT INTO purchases (user_id, book_id, price) VALUES (%s, %s, %s)",
            (purchase.user_id, purchase.book_id, purchase.price)
        )

        purchase_id = cursor.lastrowid
        conn.commit()

        logger.info(f"Purchase created successfully with ID: {purchase_id}")
        return {
            "message": "Purchase created successfully",
            "purchase_id": purchase_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in create_purchase: {str(e)}")
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@router.get("/user/{user_id}", response_model=List[PurchaseDetailResponse])
def get_purchases_by_user(user_id: int):
    """Get all purchases made by a specific user"""
    conn = None
    cursor = None
    try:
        logger.info(f"Attempting to fetch purchases for user: {user_id}")
        conn = get_read_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT 
            p.id, p.user_id, p.book_id, p.price, p.purchase_date,
            b.title as book_title,
            CONCAT(a.first_name, ' ', a.last_name) as book_author,
            u.username
        FROM purchases p
        JOIN books b ON p.book_id = b.id
        JOIN authors a ON b.author_id = a.id
        JOIN users u ON p.user_id = u.id
        WHERE p.user_id = %s
        ORDER BY p.purchase_date DESC
        """

        cursor.execute(query, (user_id,))
        results = cursor.fetchall()

        logger.info(f"Found {len(results)} purchases for user {user_id}")
        return [PurchaseDetailResponse(**row) for row in results]

    except Exception as e:
        logger.error(f"Error in get_purchases_by_user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()