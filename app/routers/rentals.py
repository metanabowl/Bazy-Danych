# Updated rentals router with return/delete functionality
from fastapi import APIRouter, HTTPException
from app.db.connection import get_read_connection, get_write_connection
from app.models.schemas import RentalResponse, RentalCreate
from typing import List
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rentals", tags=["rentals"])


@router.get("/", response_model=List[RentalResponse])
def get_all_rentals():
    """Get all rentals"""
    conn = None
    cursor = None
    try:
        logger.info("Attempting to fetch all rentals")
        conn = get_read_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM rentals ORDER BY rented_at DESC")
        results = cursor.fetchall()

        logger.info(f"Found {len(results)} rentals")
        logger.info(f"Sample result: {results[0] if results else 'No results'}")

        return [RentalResponse(**row) for row in results]

    except Exception as e:
        logger.error(f"Error in get_all_rentals: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@router.get("/{rental_id}", response_model=RentalResponse)
def get_rental_by_id(rental_id: int):
    """Get a specific rental by ID"""
    conn = None
    cursor = None
    try:
        logger.info(f"Attempting to fetch rental with id: {rental_id}")
        conn = get_read_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM rentals WHERE id = %s", (rental_id,))
        result = cursor.fetchone()

        if not result:
            logger.warning(f"Rental with id {rental_id} not found")
            raise HTTPException(status_code=404, detail="Rental not found")

        logger.info(f"Found rental: {result}")
        return RentalResponse(**result)

    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Error in get_rental_by_id: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@router.get("/user/{user_id}", response_model=List[RentalResponse])
def get_rentals_by_user(user_id: int):
    """Get all rentals by a specific user"""
    conn = None
    cursor = None
    try:
        logger.info(f"Attempting to fetch rentals for user: {user_id}")
        conn = get_read_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM rentals WHERE user_id = %s ORDER BY rented_at DESC",
            (user_id,)
        )
        results = cursor.fetchall()

        logger.info(f"Found {len(results)} rentals for user {user_id}")
        return [RentalResponse(**row) for row in results]

    except Exception as e:
        logger.error(f"Error in get_rentals_by_user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@router.get("/user/{user_id}/active", response_model=List[RentalResponse])
def get_active_rentals_by_user(user_id: int):
    """Get all active (not returned) rentals by a specific user"""
    conn = None
    cursor = None
    try:
        logger.info(f"Attempting to fetch active rentals for user: {user_id}")
        conn = get_read_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM rentals WHERE user_id = %s AND returned_at IS NULL ORDER BY rented_at DESC",
            (user_id,)
        )
        results = cursor.fetchall()

        logger.info(f"Found {len(results)} active rentals for user {user_id}")
        return [RentalResponse(**row) for row in results]

    except Exception as e:
        logger.error(f"Error in get_active_rentals_by_user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@router.post("/", response_model=dict)
def rent_book(rental: RentalCreate):
    """Rent a book (create a new rental)"""
    conn = None
    cursor = None
    try:
        logger.info(f"Attempting to create rental: {rental}")
        conn = get_write_connection()
        cursor = conn.cursor()

        # Check if book_item exists
        cursor.execute("SELECT id FROM book_items WHERE id = %s", (rental.book_item_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Book item not found")

        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE id = %s", (rental.user_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="User not found")

        # Create the rental
        cursor.execute(
            "INSERT INTO rentals (user_id, book_item_id, rented_at, returned_at) VALUES (%s, %s, %s, %s)",
            (rental.user_id, rental.book_item_id, rental.rented_at, rental.returned_at)
        )

        rental_id = cursor.lastrowid
        conn.commit()

        logger.info(f"Rental created successfully with ID: {rental_id}")
        return {
            "message": "Book rented successfully",
            "rental_id": rental_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in rent_book: {str(e)}")
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@router.put("/{rental_id}/return", response_model=dict)
def return_rental(rental_id: int):
    """Return a rented book (update returned_at timestamp)"""
    conn = None
    cursor = None
    try:
        logger.info(f"Attempting to return rental with id: {rental_id}")
        conn = get_write_connection()
        cursor = conn.cursor(dictionary=True)

        # First check if rental exists and is not already returned
        cursor.execute("SELECT * FROM rentals WHERE id = %s", (rental_id,))
        rental = cursor.fetchone()

        if not rental:
            logger.warning(f"Rental with id {rental_id} not found")
            raise HTTPException(status_code=404, detail="Rental not found")

        if rental['returned_at'] is not None:
            logger.warning(f"Rental with id {rental_id} already returned")
            raise HTTPException(status_code=400, detail="Book already returned")

        # Update the rental with return timestamp
        current_time = datetime.now()
        cursor.execute(
            "UPDATE rentals SET returned_at = %s WHERE id = %s",
            (current_time, rental_id)
        )

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Rental not found")

        conn.commit()
        logger.info(f"Rental {rental_id} returned successfully")

        return {
            "message": "Book returned successfully",
            "rental_id": rental_id,
            "returned_at": current_time.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in return_rental: {str(e)}")
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@router.delete("/{rental_id}", response_model=dict)
def delete_rental(rental_id: int):
    """Delete a rental record completely"""
    conn = None
    cursor = None
    try:
        logger.info(f"Attempting to delete rental with id: {rental_id}")
        conn = get_write_connection()
        cursor = conn.cursor(dictionary=True)

        # First check if rental exists and get its details
        cursor.execute("SELECT * FROM rentals WHERE id = %s", (rental_id,))
        rental = cursor.fetchone()

        if not rental:
            logger.warning(f"Rental with id {rental_id} not found")
            raise HTTPException(status_code=404, detail="Rental not found")

        # Delete the rental
        cursor.execute("DELETE FROM rentals WHERE id = %s", (rental_id,))

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Rental not found")

        conn.commit()
        logger.info(f"Rental {rental_id} deleted successfully")

        return {
            "message": "Rental deleted successfully",
            "deleted_rental": {
                "id": rental["id"],
                "user_id": rental["user_id"],
                "book_item_id": rental["book_item_id"],
                "rented_at": rental["rented_at"].isoformat() if rental["rented_at"] else None,
                "returned_at": rental["returned_at"].isoformat() if rental["returned_at"] else None
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_rental: {str(e)}")
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()