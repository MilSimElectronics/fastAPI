from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
# import mysql.connector
# from mysql.connector import errorcode
from . import schemas
from .database import DataBase
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

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
#         print('Connected to the fastAPI database. OAUTH2')
#         break
#     except mysql.connector.Error as err:
#         if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
#             print("Something is wrong with your user name or password")
#         elif err.errno == errorcode.ER_BAD_DB_ERROR:
#             print("Database does not exist")
#         else:
#             print(err)
#         time.sleep(5)


# Path to openssl in windows 10: C:\Program Files\Git\usr\bin
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")

        if id is None:
            raise credentials_exception

        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exception

    return token_data


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.",
                                          headers={"WWW-Authenticate": "Bearer"})

    token = verify_access_token(token, credentials_exception)

    sql = "SELECT * FROM users WHERE id = %s"
    val = (token.id,)
    DataBase.db_cursor.execute(sql, val)
    last_record = DataBase.db_cursor.fetchone()

    if not last_record:
        raise credentials_exception

    return last_record
