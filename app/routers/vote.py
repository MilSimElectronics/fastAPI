from fastapi import FastAPI, Response, status, HTTPException, APIRouter, Depends
from .. import schemas, oauth2
from typing import List, Optional
from ..database import DataBase

router = APIRouter(
    prefix="/vote",
    tags=['Vote']
)


# Create a vote
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_vote(vote: schemas.Vote, current_user: int = Depends(oauth2.get_current_user)):
    # First check if the user has voted on the post already
    sql = "SELECT * FROM votes WHERE post_id = %s AND user_id = %s"
    val = (vote.post_id, int(current_user['id']))
    DataBase.db_cursor.execute(sql, val)
    last_record = DataBase.db_cursor.fetchone()

    if last_record:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"User {current_user['id']} has already voted on post {vote.post_id}.")

    if vote.vote_type:
        vote_type = 1
    else:
        vote_type = 0

    sql = "INSERT INTO votes (user_id, post_id, vote_type, active) VALUES (%s, %s, %s, %s)"
    val = (current_user['id'], vote.post_id, vote_type, 'Y')
    DataBase.db_cursor.execute(sql, val)
    DataBase.mydb.commit()
    last_id = DataBase.db_cursor.lastrowid
    return {"message": "Vote added successfully."}


# Update a vote
@router.put("/{id}")
def update_vote(id: int, vote: schemas.VoteUpdate, current_user: int = Depends(oauth2.get_current_user)):
    sql = "SELECT * FROM votes WHERE id = %s"
    val = (id,)
    DataBase.db_cursor.execute(sql, val)
    last_record = DataBase.db_cursor.fetchone()

    if not last_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vote with id {id} not found.")

    if current_user['id'] != last_record['user_id']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action.")

    if vote.vote_type:
        vote_type = 1
    else:
        vote_type = 0

    sql = "UPDATE votes SET vote_type = %s WHERE id = %s"
    val = (vote_type, id)

    try:
        DataBase.db_cursor.execute(sql, val)
        DataBase.mydb.commit()
        return {"message": f"Vote {id} updated successfully."}
    except mysql.connector.Error as err:
        print(err)


# Delete a vote based on id
@router.delete("/{id}")
def delete_vote(id: int, current_user: int = Depends(oauth2.get_current_user)):
    sql = "SELECT * FROM votes WHERE id = %s"
    val = (id,)
    DataBase.db_cursor.execute(sql, val)
    last_record = DataBase.db_cursor.fetchone()

    if not last_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vote with id {id} not found.")

    if current_user['id'] != last_record['user_id']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action.")

    sql = "UPDATE votes SET active = 'N' WHERE id = %s"
    val = (id,)

    try:
        DataBase.db_cursor.execute(sql, val)
        DataBase.mydb.commit()
        return {"message": f"Vote {id} deleted successfully."}
    except mysql.connector.Error as err:
        print(err)

