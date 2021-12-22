import mysql.connector
from mysql.connector import errorcode
import time
from .config import settings

# loop until connected to the database
class DataBase():
    while True:
        try:
            mydb = mysql.connector.connect(
                host=settings.database_host,
                user=settings.database_user,
                password=settings.database_password,
                database=settings.database_name
            )
            db_cursor = mydb.cursor(dictionary=True)
            print('Connected to the fastAPI database.')
            break
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
            time.sleep(5)
