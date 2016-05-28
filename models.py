from app import db

#Modified to suit reddit's data model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, index = True)
    text = db.Column(db.String, index=True)
    parent_id = db.Column(db.String, index=True)
    rating = db.Column(db.Integer, index=True)
    lines = db.relationship('Line')

class Line(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.String, index  = True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    chunks = db.relationship('Chunk')
    rating = db.Column(db.Integer, index=True)

class Chunk(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.String, index = True)
    line_id = db.Column(db.Integer, db.ForeignKey('line.id'))
    rating = db.Column(db.Integer, index = True)
