from fastapi import Response, status, HTTPException, APIRouter, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
# import mysql.connector
# from mysql.connector import errorcode
from .. import schemas, utils, oauth2
from ..database import DataBase

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
#         print('Connected to the fastAPI database. AUTH')
#         break
#     except mysql.connector.Error as err:
#         if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
#             print("Something is wrong with your user name or password")
#         elif err.errno == errorcode.ER_BAD_DB_ERROR:
#             print("Database does not exist")
#         else:
#             print(err)
#         time.sleep(5)

router = APIRouter(
    tags=['Authentication']
)


@router.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends()):
    sql = "SELECT * FROM users WHERE email = %s"
    val = (user_credentials.username,)
    DataBase.db_cursor.execute(sql, val)
    last_record = DataBase.db_cursor.fetchone()

    if not last_record:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid credentials.")

    if not utils.verify_credentials(user_credentials.password, last_record['password']):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid credentials.")

    access_token = oauth2.create_access_token(data={"user_id": last_record['id']})
    return {"access_token": access_token, "token_type": "bearer"}
