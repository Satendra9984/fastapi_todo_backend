from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


class User(Base):
    __tablename__ = 'users'

    id = Column(type_=Integer, primary_key=True, autoincrement=True)
    username = Column(type_=String, unique=True)
    email = Column(type_=String, unique=True)
    first_name = Column(type_=String)
    last_name = Column(type_=String)
    hashed_password = Column(type_=String)
    is_active = Column(type_=Boolean, default=False)
    user_role= Column(type_=String)




class Todo(Base):
    __tablename__ = 'todos'

    id = Column(type_=Integer, primary_key=True, autoincrement=True)
    title = Column(type_=String)
    description = Column(type_=String)
    priority = Column(type_=String)
    complete = Column(type_=Boolean, default=False)
    user_id = Column(ForeignKey("users.id"),type_=Integer)

