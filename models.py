from app import db

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.String, index=True)
    rating = db.Column(db.Integer, index=True)
