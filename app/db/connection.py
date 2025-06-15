from contextlib import contextmanager

import mysql.connector
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Master
MASTER_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "SilneHaslo123$",
    "database": "biblioteka",
    "ssl_ca": "/usr/local/mysql/client-certs/ca-cert.pem",
    "ssl_cert": "/usr/local/mysql/client-certs/client-cert.pem",
    "ssl_key": "/usr/local/mysql/client-certs/client-key.pem",
    "charset": "utf8mb4"
}

# Slave
SLAVE_CONFIG = {
    "host": "127.0.0.1",
    "port": 3307,
    "user": "root",
    "password": "SilneHaslo123$", 
    "database": "biblioteka",
    "ssl_ca": "/usr/local/mysql/client-certs/ca-cert.pem",
    "ssl_cert": "/usr/local/mysql/client-certs/client-cert.pem",
    "ssl_key": "/usr/local/mysql/client-certs/client-key.pem",
    "charset": "utf8mb4"
}


def get_write_connection():
    """Get connection to MASTER database for write operations"""
    try:
        connection = mysql.connector.connect(**MASTER_CONFIG)
        logger.info("Connected to MASTER database")
        return connection
    except mysql.connector.Error as err:
        logger.error(f"Error connecting to MASTER database: {err}")
        raise


def get_read_connection():
    """Get connection to SLAVE database for read operations"""
    try:
        connection = mysql.connector.connect(**SLAVE_CONFIG)
        logger.info("Connected to SLAVE database")
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
    except Exception as e:
        if connection:
            connection.rollback()
        logger.error(f"Error in write operation: {e}")
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
            cursor.execute("SELECT 'Master Connection OK' as status, @@hostname as host")
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
            cursor.execute("SELECT 'Slave Connection OK' as status, @@hostname as host")
            result = cursor.fetchone()
            print(f"✓ Slave: {result}")

            # Check slave status
            cursor.execute("SHOW SLAVE STATUS")
            slave_status = cursor.fetchone()
            if slave_status:
                print(
                    f"✓ Slave Status: IO_Running={slave_status.get('Slave_IO_Running')}, SQL_Running={slave_status.get('Slave_SQL_Running')}")
                print(
                    f"✓ Master Info: Host={slave_status.get('Master_Host')}, Log_File={slave_status.get('Master_Log_File')}")
            else:
                print("⚠ Warning: This server is not configured as a Slave")
    except Exception as e:
        print(f"✗ Slave connection failed: {e}")


def check_ssl_status():
    """Check SSL status for both connections"""
    print("\nChecking SSL Status:")

    # Check Master SSL
    try:
        with get_write_cursor() as cursor:
            cursor.execute("SHOW SESSION STATUS LIKE 'Ssl_version'")
            ssl_version = cursor.fetchone()
            print(f"Master SSL Version: {ssl_version}")
    except Exception as e:
        print(f"Error checking Master SSL: {e}")

    # Check Slave SSL
    try:
        with get_read_cursor() as cursor:
            cursor.execute("SHOW SESSION STATUS LIKE 'Ssl_version'")
            ssl_version = cursor.fetchone()
            print(f"Slave SSL Version: {ssl_version}")
    except Exception as e:
        print(f"Error checking Slave SSL: {e}")


if __name__ == "main":
    test_connections()
    check_ssl_status()
# import mysql.connector
#
# # Połączenie do MASTER (zapis)
# def get_write_connection():
#     return mysql.connector.connect(
#         host="127.0.0.1",
#         port=3306,
#         user="root",
#         password="SilneHaslo123$",
#         database="biblioteka",
#         ssl_ca="/usr/local/mysql/client-certs/ca-cert.pem",
#         ssl_cert="/usr/local/mysql/client-certs/client-cert.pem",
#         ssl_key="/usr/local/mysql/client-certs/client-key.pem"
#     )
#
# # Połączenie do SLAVE (odczyt)
# def get_read_connection():
#     return mysql.connector.connect(
#         host="127.0.0.1",
#         port=3306,
#         user="root",
#         password="SilneHaslo123$",
#         database="biblioteka",
#         ssl_ca="/usr/local/mysql/client-certs/ca-cert.pem",
#         ssl_cert="/usr/local/mysql/client-certs/client-cert.pem",
#         ssl_key="/usr/local/mysql/client-certs/client-key.pem"
#     )
#
# conn = get_read_connection()
# cursor = conn.cursor()
# cursor.execute("SHOW SESSION STATUS LIKE 'Ssl_version'")
# ssl_version = cursor.fetchone()
# print("SSL Version:", ssl_version)
# conn.close()
#
# # Sprawdzenie SSL:
# ### mysql -u root -p
# ### SHOW VARIABLES LIKE 'ssl%';
# ### SHOW SESSION STATUS LIKE 'Ssl_version';
