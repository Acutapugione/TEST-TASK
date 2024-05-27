from flask import Flask, request, render_template, Response, redirect, url_for
from base64 import b64encode
from sqlalchemy import create_engine, LargeBinary, Column
from sqlalchemy.dialects.sqlite import BLOB
from werkzeug.utils import secure_filename
from sqlalchemy.orm import (
    sessionmaker,
    Mapped,
    mapped_column,
    DeclarativeBase
    
)


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)

class Book(Base):
    __tablename__ = 'books'

    title: Mapped[str]
    description: Mapped[str]
    author: Mapped[str]
    price: Mapped[int]
    isbn: Mapped[str]
    photo = Column(BLOB)

app = Flask(__name__)

engine = create_engine('sqlite:///books.db', echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for('book_list'), code=301)


def up():
    Base.metadata.create_all(engine)


def down():
    Base.metadata.drop_all(engine)


@app.get('/book_list')
def book_list():
    session = Session()
    content = []
    books = session.query(Book).all()
    for book in books:
        content.append({
            "id": book.id,
            "title": book.title,
            "description": book.description,
            "author": book.author,
            "price": book.price,
            "isbn": book.isbn,
            "photo": b64encode(book.photo).decode("utf-8"),
        })
        
    session.close()
    return render_template('book/list.html', books=content)

@app.post('/create_book')
def create_book():
    title = request.form['title']
    description = request.form['description']
    author = request.form['author']
    price = request.form['price']
    isbn = request.form['isbn']
    
    file = request.files.get('photo')

    filename = secure_filename(file.filename)
    
    file.save(filename)

    with open(filename, "rb") as filename:
        photo = filename.read()

    with Session.begin() as session:
        session.add(
            Book(
                title=title, 
                description=description, 
                author=author, 
                price=price, 
                isbn=isbn, 
                photo=photo,
            )
        )

    return redirect(url_for("book_list"))

@app.get('/create_book')
def create_book_form():
    return render_template('book/create.html')

@app.get('/get_book/<int:id>')
def get_book(id):
    with Session.begin() as session:
        book = session.query(Book).get(id)
        context = {
            "book": {
                "id": book.id,
                "title": book.title,
                "description": book.description,
                "author": book.author,
                "price": book.price,
                "isbn": book.isbn,
                "photo": b64encode(book.photo).decode("utf-8"),
            }
        }
    return render_template('book/index.html', **context)


if __name__ == '__main__':
    # down()
    up()
    app.run(debug=True)
