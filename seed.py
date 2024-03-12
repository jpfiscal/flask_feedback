from app import app
from models import db, User, Feedback

with app.app_context():
    db.drop_all()
    db.create_all()