from fastapi import FastAPI, Response, status, HTTPException, APIRouter, Depends
# import mysql.connector
# from mysql.connector import errorcode
from .. import schemas, oauth2
from typing import List, Optional
# import time
from ..database import DataBase

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
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
#         print('Connected to the fastAPI database. POST')
#         break
#     except mysql.connector.Error as err:
#         if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
#             print("Something is wrong with your user name or password")
#         elif err.errno == errorcode.ER_BAD_DB_ERROR:
#             print("Database does not exist")
#         else:
#             print(err)
#         time.sleep(5)


# Return all post
@router.get("/", response_model=List[schemas.Post])
def get_posts(limit: int = 10, skip: int = 0, search: Optional[str] = "",
              current_user: int = Depends(oauth2.get_current_user)):
    """Currently returns records from all users"""
    # db_cursor.execute("SELECT * FROM posts")
    sql = "SELECT users.email AS user_email, posts.*, COUNT(votes.id) AS votes_total FROM posts \
    LEFT JOIN users ON posts.user_id = users.id \
    LEFT JOIN votes ON posts.id = votes.post_id \
    WHERE title LIKE CONCAT('%', %s, '%') \
    GROUP BY posts.id, users.id \
    ORDER BY posts.addedon DESC \
    LIMIT %s, %s"
    val = (search, skip, limit,)
    DataBase.db_cursor.execute(sql, val)
    the_data = DataBase.db_cursor.fetchall()
    return the_data


# Return a single post based on id
@router.get("/{id}", response_model=schemas.Post)
def get_post(id: int, response: Response, current_user: int = Depends(oauth2.get_current_user)):
    """Currently returns records from all users"""
    # sql = "SELECT * FROM posts WHERE id = %s"
    sql = "SELECT users.email AS user_email, posts.*, COUNT(votes.id) AS votes_total FROM posts \
    LEFT JOIN users ON posts.user_id = users.id \
    LEFT JOIN votes ON posts.id = votes.post_id \
    WHERE posts.id = %s \
    GROUP BY posts.id, users.id"
    val = (str(id),)
    DataBase.db_cursor.execute(sql, val)
    last_record = DataBase.db_cursor.fetchone()
    if not last_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found.")
    return last_record


# Create a new post
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostCreate)
def create_post(post: schemas.PostCreate, current_user: int = Depends(oauth2.get_current_user)):
    sql = "INSERT INTO posts (title, content, published, user_id) VALUES (%s, %s, %s, %s)"
    val = (post.title, post.content, post.published, int(current_user['id']))
    DataBase.db_cursor.execute(sql, val)
    DataBase.mydb.commit()
    last_id = DataBase.db_cursor.lastrowid
    DataBase.db_cursor.execute(f"SELECT * FROM posts WHERE id = {last_id}")
    last_record = DataBase.db_cursor.fetchone()
    return last_record


# Update a post based on id
@router.put("/{id}", response_model=schemas.PostCreate)
def update_post(id: int, post: schemas.PostCreate, current_user: int = Depends(oauth2.get_current_user)):
    sql = "SELECT * FROM posts WHERE id = %s"
    val = (str(id),)
    DataBase.db_cursor.execute(sql, val)
    last_record = DataBase.db_cursor.fetchone()

    if not last_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found.")

    if current_user['id'] != last_record['user_id']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action.")

    sql = "UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s"
    val = (post.title, post.content, post.published, str(id),)

    try:
        DataBase.db_cursor.execute(sql, val)
        DataBase.mydb.commit()

        sql = "SELECT * FROM posts WHERE id = %s"
        val = (str(id),)
        DataBase.db_cursor.execute(sql, val)
        last_record = DataBase.db_cursor.fetchone()
    except mysql.connector.Error as err:
        print(err)

    if last_record == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post {id} does not exist.")

    return last_record


# Delete a post based on id
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, current_user: int = Depends(oauth2.get_current_user)):
    sql = "SELECT * FROM posts WHERE id = %s"
    val = (str(id),)
    DataBase.db_cursor.execute(sql, val)
    last_record = DataBase.db_cursor.fetchone()

    if not last_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found.")

    if current_user['id'] != last_record['user_id']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action.")

    sql = "DELETE FROM posts WHERE id = %s"
    val = (str(id),)

    try:
        DataBase.db_cursor.execute(sql, val)
        DataBase.mydb.commit()
    except mysql.connector.Error as err:
        print(err)

    if DataBase.db_cursor.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post {id} does not exist.")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
