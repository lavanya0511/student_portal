from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column,String,Integer
Base = declarative_base()

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key=True,autoincrement=True)
    name = Column(String(80),nullable=False)
    email = Column(String(100),unique=True,nullable=False)
    password_hash = Column(String,nullable=False)
    role = Column(String(25),default="student")