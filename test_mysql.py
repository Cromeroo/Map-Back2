import pymysql
import os

try:
    print("🔍 Intentando conectar a MySQL en Clever Cloud usando `pymysql`...")

    connection = pymysql.connect(
        host="bomqaeinqjipko184nen-mysql.services.clever-cloud.com",
        user="u2x9tezyppdokhxy",
        password="poNbTno116tbCRLeoyRk",
        database="bomqaeinqjipko184nen",
        port=3306,
        connect_timeout=10
    )

    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print("✅ Conexión exitosa a MySQL en Clever Cloud")
        print("🔍 Resultado de la consulta:", result)

except pymysql.MySQLError as e:
    print(f"❌ ERROR en la conexión: {e}")

finally:
    if 'connection' in locals() and connection.open:
        connection.close()
        print("🔄 Conexión cerrada correctamente")
