from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from catalogue_models import Author, Book, AuthorCreate, AuthorModel, get_db, BookModel, BookCreate, UpdateBook

app = FastAPI()


@app.post("/authors/", response_model=Author)
async def create_author(author: AuthorCreate, db: Session = Depends(get_db)):
    db_author = AuthorModel(**author.model_dump())
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author


@app.get("/authors/", response_model=list[Author])
async def get_authors(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    authors = db.query(AuthorModel).offset(skip).limit(limit).all()
    return authors


@app.get("/authors/{author_id}", response_model=Author)
async def get_author(author_id: int, db: Session = Depends(get_db)):
    author = db.query(AuthorModel).filter(AuthorModel.id == author_id).first()
    if author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    return author


@app.patch("/authors/{author_id}", response_model=Author)
async def update_author(
        author_id: int, author: AuthorCreate, db: Session = Depends(get_db)
):
    db_author = db.query(AuthorModel).filter(AuthorModel.id == author_id).first()
    if db_author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    for key, value in author.model_dump().items():
        setattr(db_author, key, value)
    db.commit()
    db.refresh(db_author)
    return db_author


@app.delete("/authors/{author_id}", response_model=dict)
async def delete_author(author_id: int, db: Session = Depends(get_db)):
    db_author = db.query(AuthorModel).filter(AuthorModel.id == author_id).first()
    if db_author is None:
        raise HTTPException(status_code=404, detail="Author not found")
    db.delete(db_author)
    db.commit()
    return {"message": "Author deleted successfully"}


@app.post("/books/", response_model=Book)
async def create_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = BookModel(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


@app.get("/books/", response_model=list[Book])
async def get_books(author_id: int = None, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    query = db.query(BookModel)
    if author_id is not None:
        query = query.filter(BookModel.author_id == author_id)
    books = query.offset(skip).limit(limit).all()
    return books


@app.get("/books/{book_id}", response_model=Book)
async def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.patch("/books/{book_id}", response_model=Book)
async def update_book(book_id: int, book_update: UpdateBook, db: Session = Depends(get_db)):
    db_book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    if book_update.name is not None:
        db_book.name = book_update.name

    if book_update.author_id is not None:
        db_book.author_id = book_update.author_id

    db.commit()
    db.refresh(db_book)
    return db_book

@app.delete("/books/{book_id}", response_model=dict)
async def delete_book(book_id: int, db: Session = Depends(get_db)):
    db_book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(db_book)
    db.commit()
    return {"message": "Book deleted successfully"}
