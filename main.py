from flask import (
    Flask, 
    render_template, 
    request, 
    redirect, 
    url_for,
    abort
)
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import relationship


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookservice.db'
app.app_context().push()

db = SQLAlchemy(app)

ma = Marshmallow(app)

# ---------------------------------------------------------------------------------------Таблицы в БД
genre_book = db.Table(
    "genre_book",
    db.Column("genre_id", db.Integer, db.ForeignKey("genres.id")),
    db.Column("book_id", db.Integer, db.ForeignKey("books.id"))
)

author_book = db.Table(
    "author_book",
    db.Column("author_id", db.Integer, db.ForeignKey("authors.id")),
    db.Column("book_id", db.Integer, db.ForeignKey("books.id")),
)

class Genre(db.Model):
    __tablename__ = "genres"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    
    def __repr__(self):
        return f'<Genre "{self.name}">' 

class Author(db.Model):
    __tablename__ = "authors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    bio = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Author "{self.name}">' 


class Book(db.Model):
    __tablename__ = "books"
    __table_args__ = (db.UniqueConstraint('title'), ) # Ограничение на уникальность названия книги
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    publ_year = db.Column(db.Integer)
    author = relationship("Author", secondary=author_book, backref="authors")
    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"))
    genre_id = db.Column(db.Integer, db.ForeignKey("genres.id"))
    genre = relationship("Genre", secondary=genre_book, backref="genres")


    def __repr__(self):
        return f'<Book "{self.title}">'


# -----------------------------------------------------------------------------------Валидация данных
class AuthorSchema(ma.SQLAlchemySchema):

    class Meta:
        model = Author
    
    id = ma.auto_field()
    name = ma.auto_field()
    bio = ma.auto_field()
    # books = ma.auto_field()

class GenreSchema(ma.SQLAlchemySchema):

    class Meta:
        model = Genre
    
    id = ma.auto_field()
    name = ma.auto_field()
    # books = ma.auto_field()

class BookSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = Book
        include_fk = True


# ------------------------------------------------------------------------------------------------API

@app.route('/')  
def index():  
    books = Book.query.all()
    return render_template('index.html', books=books)

@app.route('/get/<title>/', methods=['GET'])  
def book(title):  
    book = Book.query.filter_by(title=title).first()
    if not book:
        abort(404)
    return render_template('book.html', book=book)   
 
@app.route('/add', methods=['GET', 'POST'])  
def create():  
    if request.method == 'POST':

        title = request.form['title']
        genre_title = request.form['genre_title'].split(',')
        author_name = request.form['author_name'].split(',')
        publ_year = int(request.form['publ_year'])
        description = request.form['description']

        genre_data = []
        for genre in genre_title:
            existing_genre = db.session.query(Genre).filter_by(name=genre.strip()).first()
            if existing_genre:
                genre_data.append(existing_genre)
            else:
                new_genre = Genre(name=genre.strip())
                db.session.add(new_genre)
                genre_data.append(new_genre)

        # Создаем список объектов Author на основе переданных имен авторов
        author_data = []
        for author in author_name:
            existing_author = db.session.query(Author).filter_by(name=author.strip()).first()
            if existing_author:
                author_data.append(existing_author)
            else:
                new_author = Author(name=author.strip())
                db.session.add(new_author)
                author_data.append(new_author)

        # Создаем объект Book и связываем его с жанрами и авторами
        book_data = Book(title=title, publ_year=publ_year, description=description,
                         author=author_data, genre=genre_data)

        db.session.add(book_data)
        db.session.commit()
        # print(f"{genre_title}\n{author_data}\n{book_data}")

        return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/instruction/')  
def instruction():
    return render_template('instruction.html')

@app.route('/author/')  
def author():
    authors = Author.query.all()
    return render_template('author.html', authors=authors)

'''@app.route('/author/<name>/',endpoint='func1', methods=['GET'])  
def authors(name):  
    author = Author.query.filter_by(name=name).first()
    if not author:
        abort(404)
    return render_template('author2.html', author=author)'''