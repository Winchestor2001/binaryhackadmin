from flask_sqlalchemy import SQLAlchemy
from app import app


db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(200), nullable=False)
    user_status = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Users {self.id}>'

