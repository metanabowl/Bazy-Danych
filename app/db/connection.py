from contextlib import contextmanager
import mysql.connector
from mysql.connector import pooling
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connection pool configuration
POOL_CONFIG = {
    "pool_size": 5,
    "pool_reset_session": True,
    "charset": "utf8mb4",
    "autocommit": False,
    "connect_timeout": 10,
    "sql_mode": "STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO"
}

# Master configuration
MASTER_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "SilneHaslo123$",
    "database": "biblioteka",
    "ssl_ca": "/usr/local/mysql/client-certs/ca-cert.pem",
    "ssl_cert": "/usr/local/mysql/client-certs/client-cert.pem",
    "ssl_key": "/usr/local/mysql/client-certs/client-key.pem",
    **POOL_CONFIG
}

# Slave configuration
SLAVE_CONFIG = {
    "host": "127.0.0.1",
    "port": 3307,
    "user": "root",
    "password": "SilneHaslo123$",
    "database": "biblioteka",
    "ssl_ca": "/usr/local/mysql/client-certs/ca-cert.pem",
    "ssl_cert": "/usr/local/mysql/client-certs/client-cert.pem",
    "ssl_key": "/usr/local/mysql/client-certs/client-key.pem",
    **POOL_CONFIG
}

# Create connection pools
try:
    master_pool = pooling.MySQLConnectionPool(
        pool_name="master_pool",
        **MASTER_CONFIG
    )
    logger.info("Master connection pool created successfully")
except mysql.connector.Error as err:
    logger.error(f"Error creating master pool: {err}")
    master_pool = None

try:
    slave_pool = pooling.MySQLConnectionPool(
        pool_name="slave_pool",
        **SLAVE_CONFIG
    )
    logger.info("Slave connection pool created successfully")
except mysql.connector.Error as err:
    logger.error(f"Error creating slave pool: {err}")
    slave_pool = None

def get_write_connection():
    """Get connection to MASTER database for write operations"""
    try:
        if master_pool:
            connection = master_pool.get_connection()
            logger.debug("Got connection from master pool")
            return connection
        else:
            # Fallback to direct connection
            connection = mysql.connector.connect(**MASTER_CONFIG)
            logger.info("Connected to MASTER database (direct)")
            return connection
    except mysql.connector.Error as err:
        logger.error(f"Error connecting to MASTER database: {err}")
        raise

def get_read_connection():
    """Get connection to SLAVE database for read operations"""
    try:
        if slave_pool:
            connection = slave_pool.get_connection()
            logger.debug("Got connection from slave pool")
            return connection
        else:
            # Try direct slave connection
            connection = mysql.connector.connect(**SLAVE_CONFIG)
            logger.info("Connected to SLAVE database (direct)")
            return connection
    except mysql.connector.Error as err:
        logger.error(f"Error connecting to SLAVE database: {err}")
        # Fallback to master if slave is unavailable
        logger.warning("Falling back to MASTER for read operations")
        return get_write_connection()

@contextmanager
def get_write_cursor():
    """Context manager for write operations"""
    connection = None
    cursor = None
    try:
        connection = get_write_connection()
        cursor = connection.cursor(dictionary=True)
        yield cursor
        connection.commit()
        logger.debug("Write operation committed successfully")
    except Exception as e:
        if connection:
            connection.rollback()
            logger.error(f"Write operation rolled back due to error: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@contextmanager
def get_read_cursor():
    """Context manager for read operations"""
    connection = None
    cursor = None
    try:
        connection = get_read_connection()
        cursor = connection.cursor(dictionary=True)
        yield cursor
        logger.debug("Read operation completed successfully")
    except Exception as e:
        logger.error(f"Error in read operation: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def test_connections():
    """Test both master and slave connections"""
    print("Testing Master (Write) Connection:")
    try:
        with get_write_cursor() as cursor:
            cursor.execute("SELECT 'Master Connection OK' as status, @@hostname as host, NOW() as timestamp")
            result = cursor.fetchone()
            print(f"✓ Master: {result}")

            # Check if this is actually the master
            cursor.execute("SHOW MASTER STATUS")
            master_status = cursor.fetchone()
            if master_status:
                print(f"✓ Master Status: File={master_status.get('File')}, Position={master_status.get('Position')}")
            else:
                print("⚠ Warning: This server is not configured as a Master")
    except Exception as e:
        print(f"✗ Master connection failed: {e}")

    print("\nTesting Slave (Read) Connection:")
    try:
        with get_read_cursor() as cursor:
            cursor.execute("SELECT 'Slave Connection OK' as status, @@hostname as host, NOW() as timestamp")
            result = cursor.fetchone()
            print(f"✓ Slave: {result}")

            # Check slave status
            cursor.execute("SHOW SLAVE STATUS")
            slave_status = cursor.fetchone()
            if slave_status:
                print(f"✓ Slave Status: IO_Running={slave_status.get('Slave_IO_Running')}, SQL_Running={slave_status.get('Slave_SQL_Running')}")
                print(f"✓ Master Info: Host={slave_status.get('Master_Host')}, Log_File={slave_status.get('Master_Log_File')}")
            else:
                print("⚠ Warning: This server is not configured as a Slave")
    except Exception as e:
        print(f"✗ Slave connection failed: {e}")

if __name__ == "__main__":
    test_connections()