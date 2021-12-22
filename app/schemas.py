from pydantic import BaseModel, EmailStr
from pydantic.types import conint
from datetime import datetime
from typing import Optional


# Schema to handle post creation
class PostBase(BaseModel):
    title: str
    content: str
    published: str = 'Y'


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    # title: str
    # content: str
    # published: str
    addedon: datetime
    user_id: int
    user_email: str
    votes_total: int

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    addedon: datetime

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class Vote(BaseModel):
    post_id: int
    vote_type: bool = True


class VoteUpdate(BaseModel):
    vote_type: bool
