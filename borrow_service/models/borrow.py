from models.database import db

class Borrow(db.Model):
    __tablename__ = 'borrows'

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    book_title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='borrowed')  # borrowed | returned

    def to_dict(self):
        return {
            'id': self.id,
            'user_name': self.user_name,
            'book_title': self.book_title,
            'status': self.status
        }
