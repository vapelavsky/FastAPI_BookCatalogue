from pydantic import BaseModel
from databases import Database
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./test.db"
database = Database(DATABASE_URL)

# SQLAlchemy configuration
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class AuthorBase(BaseModel):
    name: str


class AuthorCreate(AuthorBase):
    pass


class Author(AuthorBase):
    id: int

    class Config:
        from_attributes = True


class BookBase(BaseModel):
    name: str
    author_id: int


class BookCreate(BookBase):
    pass


class Book(BookBase):
    id: int

    class Config:
        from_attributes = True


class AuthorDB(AuthorBase):
    id: int

    class Config:
        from_attributes = True


class BookDB(BookBase):
    id: int

    class Config:
        from_attributes = True


class UpdateBook(BaseModel):
    name: str = None
    author_id: int = None

    class Config:
        populate_by_name = True


# SQLAlchemy Models
class AuthorModel(Base):
    __tablename__ = "author"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)


class BookModel(Base):
    __tablename__ = "book"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    author_id = Column(Integer, ForeignKey("author.id"))


Base.metadata.create_all(bind=engine)


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
