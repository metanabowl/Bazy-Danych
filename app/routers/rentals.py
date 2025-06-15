# Updated rentals router with improved error handling and logging
from fastapi import APIRouter, HTTPException
from app.db.connection import get_read_connection, get_write_connection
from app.models.schemas import RentalResponse, RentalCreate
from typing import List
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rentals", tags=["rentals"])


@router.get("/", response_model=List[RentalResponse])
def get_all():
    conn = None
    cursor = None
    try:
        logger.info("Attempting to fetch all rentals")
        conn = get_read_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM rentals")
        results = cursor.fetchall()

        logger.info(f"Found {len(results)} rentals")
        logger.info(f"Sample result: {results[0] if results else 'No results'}")

        return [RentalResponse(**row) for row in results]

    except Exception as e:
        logger.error(f"Error in get_all: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@router.get("/{id}", response_model=RentalResponse)
def get_by_id(id: int):
    conn = None
    cursor = None
    try:
        logger.info(f"Attempting to fetch rental with id: {id}")
        conn = get_read_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM rentals WHERE id = %s", (id,))
        result = cursor.fetchone()

        if not result:
            logger.warning(f"Rental with id {id} not found")
            raise HTTPException(status_code=404, detail="Rental not found")

        logger.info(f"Found rental: {result}")
        return RentalResponse(**result)

    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Error in get_by_id: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@router.post("/", response_model=dict)
def create(item: RentalCreate):
    conn = None
    cursor = None
    try:
        logger.info(f"Attempting to create rental: {item}")
        conn = get_write_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO rentals (user_id, book_item_id, rented_at, returned_at) VALUES (%s, %s, %s, %s)",
            (item.user_id, item.book_item_id, item.rented_at, item.returned_at)
        )
        conn.commit()
        logger.info("Rental created successfully")
        return {"message": "Rental created successfully"}

    except Exception as e:
        logger.error(f"Error in create: {str(e)}")
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()