import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from config import RATINGSET

app = Flask(__name__)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import *

@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    entry = None
    context = []
    start = True
    if request.method == "POST":
        try:
            start = False
            #Get the current database entry
            untagged_post = Post.query.filter(Post.rating == None).\
                order_by(Post.id).first()
            if (untagged_post is None):
                #There are no more untagged entries
                raise ValueError("No more untagged posts")
            #Get the previous 5 replies
            cur_id = untagged_post.id
            for i in range(1, 11):
                prior_post = Post.query.get(cur_id-i)
                if prior_post is None:
                    break
                else:
                    context.append(prior_post.text)

            #Reverse it to get in sequential order
            context.reverse()

            #Check if it's the start button
            f = request.form
            if "rating" not in f:
                #Display entry is still the same
                entry = untagged_post.text
            else:
                rating = f["rating"]
                if rating not in RATINGSET:
                    entry = untagged_post.text
                    er = "Rating should lie between {} and {}".\
                        format(min(RATINGSET), max(RATINGSET))
                    raise ValueError(er)
                else:
                    #Update the post
                    untagged_post.rating = int(rating)
                    db.session.commit()
                    #Get the next entry for Display
                    next_post = Post.query.filter(Post.rating == None).\
                        order_by(Post.id).first()
                    if (next_post is None):
                        raise ValueError("No more untagged posts")
                    entry = next_post.text
        except ValueError as e:
            errors.append(e)
    return render_template('index.html', errors=errors, entry=entry,
            start=start, context = context)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
