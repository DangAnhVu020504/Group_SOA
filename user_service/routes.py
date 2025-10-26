from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from models.database import db
from models.user import User

# Thêm url_prefix để đồng bộ với gateway: /users/<path>
user_bp = Blueprint('user_bp', __name__, url_prefix='/users')

@user_bp.route('/')
def home():
    # Điều hướng về trang login cho rõ ràng luồng
    return redirect(url_for('user_bp.login'))

# Đăng ký
@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('Vui lòng nhập đủ thông tin.')
            return redirect(url_for('user_bp.register'))

        if User.query.filter_by(username=username).first():
            flash('Tên đăng nhập đã tồn tại.')
            return redirect(url_for('user_bp.register'))

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Đăng ký thành công. Vui lòng đăng nhập.')
        return redirect(url_for('user_bp.login'))

    return render_template('register.html')

# Đăng nhập
@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            flash('Sai tên đăng nhập hoặc mật khẩu.')
            return redirect(url_for('user_bp.login'))

        session['user_id'] = user.id
        session['username'] = user.username
        # Sau login chuyển về gateway để vào book service
        return redirect("http://127.0.0.1:8000/books/")

    return render_template('login.html')

# Đăng xuất
@user_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('user_bp.login'))

# Trang người dùng
@user_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('user_bp.login'))
    return render_template('dashboard.html')
