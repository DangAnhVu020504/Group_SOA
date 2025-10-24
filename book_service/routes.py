from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from models.database import db
from models.book import Book

# Prefix /books để khớp với gateway: /books/<path>
book_bp = Blueprint('book_bp', __name__, url_prefix='/books')

# Danh sách sách (đặt ở '/' trong blueprint để endpoint là /books/)
@book_bp.route('/')
def list_books():
    books = Book.query.order_by(Book.id.desc()).all()
    return render_template('list_books.html', books=books)

# Thêm sách
@book_bp.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        year = request.form.get('year')

        new_book = Book(title=title, author=author, year=year)
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('book_bp.list_books'))

    return render_template('add_book.html')

# Sửa sách
@book_bp.route('/<int:book_id>/edit', methods=['GET', 'POST'])
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    if request.method == 'POST':
        book.title = request.form.get('title')
        book.author = request.form.get('author')
        book.year = request.form.get('year')
        db.session.commit()
        return redirect(url_for('book_bp.list_books'))

    return render_template('edit_book.html', book=book)

# Xóa sách
@book_bp.route('/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('book_bp.list_books'))

# API JSON: lấy tất cả sách
@book_bp.route('/api/books', methods=['GET'])
def api_get_books():
    books = Book.query.all()
    return jsonify([b.to_dict() for b in books])

# API JSON: thêm sách
@book_bp.route('/api/books', methods=['POST'])
def api_add_book():
    data = request.get_json(force=True)
    new_book = Book(title=data['title'], author=data['author'], year=data.get('year'))
    db.session.add(new_book)
    db.session.commit()
    return jsonify(new_book.to_dict()), 201
