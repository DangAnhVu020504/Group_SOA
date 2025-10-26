from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from models.database import db
from models.borrow import Borrow

# Prefix /borrow để khớp với gateway: /borrows/<path> → forward to /borrow/<path>
borrow_bp = Blueprint('borrow_bp', __name__, url_prefix='/borrow')

# Trang chủ service
@borrow_bp.route('/')
def home():
    return render_template('index.html')

# Danh sách mượn (sửa đường dẫn tương đối, không lặp prefix)
@borrow_bp.route('/list')
def list_borrows():
    borrows = Borrow.query.order_by(Borrow.id.desc()).all()
    return render_template('list_borrows.html', borrows=borrows)

# Thêm lượt mượn (Mượn sách)
@borrow_bp.route('/add', methods=['GET', 'POST'])
def add_borrow():
    if request.method == 'POST':
        user_name = request.form.get('user_name', '').strip()
        book_title = request.form.get('book_title', '').strip()

        if not user_name or not book_title:
            return redirect(url_for('borrow_bp.add_borrow'))

        new_borrow = Borrow(user_name=user_name, book_title=book_title, status='borrowed')
        db.session.add(new_borrow)
        db.session.commit()
        return redirect(url_for('borrow_bp.list_borrows'))
    
    book_title = request.args.get("book_title", "")
    return render_template('add_borrow.html', book_title=book_title)

# Trả sách
@borrow_bp.route('/<int:borrow_id>/return', methods=['GET', 'PUT'])
def return_book(borrow_id):
    borrow = Borrow.query.get_or_404(borrow_id)
    borrow.status = 'returned'
    db.session.commit()

    if request.method == 'PUT':
        return jsonify(borrow.to_dict())
    return redirect(url_for('borrow_bp.list_borrows'))

# API: lấy tất cả lượt mượn (JSON)
@borrow_bp.route('/api/borrows', methods=['GET'])
def get_all_borrows():
    borrows = Borrow.query.order_by(Borrow.id.desc()).all()
    return jsonify([b.to_dict() for b in borrows])

# API: tạo lượt mượn (JSON)
@borrow_bp.route('/api/borrows', methods=['POST'])
def create_borrow_api():
    data = request.get_json(force=True) or {}
    user_name = data.get('user_name', '').strip()
    book_title = data.get('book_title', '').strip()

    if not user_name or not book_title:
        return jsonify({'error': 'Thiếu user_name hoặc book_title'}), 400

    new_borrow = Borrow(user_name=user_name, book_title=book_title, status='borrowed')
    db.session.add(new_borrow)
    db.session.commit()
    return jsonify(new_borrow.to_dict()), 201

# API: trả sách (JSON)
@borrow_bp.route('/api/borrows/<int:borrow_id>/return', methods=['PUT'])
def return_book_api(borrow_id):
    borrow = Borrow.query.get_or_404(borrow_id)
    borrow.status = 'returned'
    db.session.commit()
    return jsonify(borrow.to_dict())
