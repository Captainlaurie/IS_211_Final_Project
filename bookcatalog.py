from flask import Flask
from flask import render_template
from flask import request
from flask import url_for
from flask import redirect
import sqlite3 as lite
import requests
import json

app = Flask(__name__)

USER = "admin"
PASSWORD = "password"
API_KEY = 'AIzaSyD2mVpczFpyzuaAbLDKQaAf3ZQHcy8Z0Pk'


def get_db_connection():
    """ Connect to SQLite database """
    conn = lite.connect('bookcatalog.db')
    conn.row_factory = lite.Row
    return conn


@app.route('/')
def root():
    return render_template("login.html", message=None)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form["user"]
        password = request.form["password"]
        
        if username == USER and password == PASSWORD:
            return redirect(url_for("catalog"))
        else:
            return render_template("login.html", message = "Incorrect username or password")
    else:
        return render_template("login.html", message=None)


@app.route('/catalog')
def catalog():
    books_qry = "select bookid, title, author, pgcount, avg_rating, isbn, image from books"
    
    conn = get_db_connection()

    books_dataset = conn.execute(books_qry).fetchall()
    
    return render_template("catalog.html", books=books_dataset)


@app.route('/booksearch', methods=['GET', 'POST'])
def book_search():
    if request.method == 'POST':
        isbn = request.form['isbn']
        # Make a request to the Google Books API using the ISBN and API key
        url = f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&key={API_KEY}'
        response = requests.get(url)
        print(response.text)

        if response.status_code == 200:
            data = response.json()

            if 'items' in data:
                for item in data['items']:
                    book_info = item['volumeInfo']
                    title = book_info['title']
                    authors = book_info.get('authors', [])
                    author_str = "" if len(authors) == 0 else ", ".join(authors)
                    page_count = book_info.get('pageCount', 'N/A')
                    rating = book_info.get('averageRating', 'N/A')

                    isbn_13 = book_info['industryIdentifiers'][0]['identifier'] if 'industryIdentifiers' in book_info else 'N/A'
                    image = book_info.get('imageLinks').get("thumbnail", "")
                    _insert_book(title, author_str, page_count, rating, isbn_13, image)

                return redirect(url_for("catalog"))
            else:
                return render_template('search_results.html', books=[])
        else:
            return render_template('search_results.html', books=[])
    else:
        return render_template('booksearch.html')


def _insert_book(title, author, pgcount, avg_rating, isbn, image):
    """
    Add a book to the database
    """
    conn = get_db_connection()
    conn.execute("INSERT INTO books(title, author, pgcount, avg_rating, isbn, image) VALUES(?, ?, ?, ?, ?, ?);",
                 (title, author, pgcount, avg_rating, isbn, image))
    conn.commit()


@app.route('/addbook', methods=['POST', 'GET'])
def add_book():
    if request.method == 'POST':
        title = request.form["title"]
        author = request.form["author"]
        pagecount = request.form["pgcount"]
        rating = request.form["avg_rating"]
        isbn = request.form["isbn"]
        image = request.form["image"]

        _insert_book(title, author, pagecount, rating, isbn, image)

        return redirect(url_for("catalog"))
    else:
        title = request.args.get('title')
        author = request.args.get('author')
        pagecount = request.args.get('pgcount')
        rating = request.args.get('avg_rating')
        isbn = request.args.get('isbn')
        image = request.args.get('image')
        return render_template("addbook.html", title=title, author=author, pagecount=pagecount, rating=rating, isbn=isbn, image=image)
    
    
@app.route('/deletebook/<bookid>', methods=['GET'])
def delete_book(bookid):
    conn = get_db_connection()
    conn.execute("DELETE from books where bookid = ?;", (bookid,))
    conn.commit()
    return redirect(url_for("catalog"))


if __name__ == '__main__':
    app.run(debug=True)
