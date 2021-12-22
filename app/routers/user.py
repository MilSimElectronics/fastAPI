from fastapi import FastAPI, Response, status, HTTPException, APIRouter
# import mysql.connector
# from mysql.connector import errorcode
from .. import schemas, utils
# import time
from ..database import DataBase


router = APIRouter(
    prefix="/users",
    tags=['Users']
)



# loop until connected to the database
# while True:
#     try:
#         mydb = mysql.connector.connect(
#             host="localhost",
#             user="root",
#             password="DevUser14!",
#             database="fastapi"
#         )
#         db_cursor = mydb.cursor(dictionary=True)
#         print('Connected to the fastAPI database. USER')
#         break
#     except mysql.connector.Error as err:
#         if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
#             print("Something is wrong with your user name or password")
#         elif err.errno == errorcode.ER_BAD_DB_ERROR:
#             print("Database does not exist")
#         else:
#             print(err)
#         time.sleep(5)


# Creates a new user
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate):
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    sql = "INSERT INTO users (email, password, active) VALUES (%s, %s, %s)"
    val = (user.email, user.password, 'Y')
    DataBase.db_cursor.execute(sql, val)
    DataBase.mydb.commit()
    last_id = DataBase.db_cursor.lastrowid
    DataBase.db_cursor.execute(f"SELECT * FROM users WHERE id = {last_id}")
    last_record = DataBase.db_cursor.fetchone()
    return last_record

# Returns user info base don id
@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int):
    sql = "SELECT * FROM users WHERE id = %s"
    val = (str(id), )
    DataBase.db_cursor.execute(sql, val)
    last_record = DataBase.db_cursor.fetchone()
    if not last_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} not found.")
    return last_record
