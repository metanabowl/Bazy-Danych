import mysql.connector

# Połączenie do MASTER (zapis)
def get_write_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="SilneHaslo123$",
        database="biblioteka",
        ssl_ca="app/certs/ca-cert.pem",
        #ssl_cert="app/certs/server-cert.pem",
        #ssl_key="app/certs/server-key.pem"
    )

# Połączenie do SLAVE (odczyt)
def get_read_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3307,
        user="root",
        password="SilneHaslo123$",
        database="biblioteka",
        ssl_ca="app/certs/ca-cert.pem",
        #ssl_cert="app/certs/server-cert.pem",
        #ssl_key="app/certs/server-key.pem"
    )

conn = get_read_connection()
cursor = conn.cursor()
cursor.execute("SHOW SESSION STATUS LIKE 'Ssl_version'")
ssl_version = cursor.fetchone()
print("SSL Version:", ssl_version)
conn.close()
