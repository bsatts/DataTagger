import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from config import RATINGSET
import traceback

app = Flask(__name__)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import Post, Line, Chunk

#Using global variables to keep track of state
isComplete = False

@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    entry = None
    context = []
    chunks = []
    full_post = ""
    start = True
    if request.method == "POST":
        try:
            global isComplete
            global hasRating
            start = False

            #Get the current database entry
            untagged_post = Post.query.filter(Post.rating == None).\
                order_by(Post.id).first()
            if (untagged_post is None):
                #There are no more untagged entries
                raise ValueError("No more untagged posts")

            full_post = untagged_post.text

            #Check if the post has untagged lines
            untagged_line = Line.query.filter_by(post_id=untagged_post.id).\
                filter(Line.rating == None).order_by(Line.id).first()
            if untagged_line is None:
                isComplete = True
            else:
                isComplete = False

            #Get the context of the post if it exists
            parent_post_name = untagged_post.parent_id
            while (parent_post_name is not None):
                parent_post = Post.query.filter_by(name=parent_post_name).first()
                if parent_post is None:
                    break
                else:
                    parent_post_name = parent_post.parent_id
                    context.append(parent_post.text)

            #Reverse it to get in sequential order
            if context: context.reverse()


            if not isComplete:
                untagged_line = Line.query.filter_by(post_id=untagged_post.id).\
                    filter(Line.rating == None).order_by(Line.id).first()
                if untagged_line is None:
                    isComplete = True
                else:
                    entry = untagged_line.text

            #Check if it is the start button
            f = request.form
            if ("l_rating" not in f) and ("p_rating" not in f):
                #Display entry is the same
                if (not isComplete):
                    #Get the chunks for the line
                    untagged_chunks = Chunk.query.filter_by(line_id=untagged_line.id).\
                        order_by(Chunk.id).all()

                    if untagged_chunks:
                        for u_chunk in untagged_chunks:
                            chunks.append(u_chunk.text)
            else:
                if (isComplete):
                    #Get the post rating
                    p_rating = f['p_rating']
                    #Update the post rating
                    untagged_post.rating = int(p_rating)
                    db.session.commit()

                    #Get the next post and it's lines and chunks
                    untagged_post = Post.query.filter(Post.rating == None).\
                    order_by(Post.id).first()
                    if (untagged_post is None):
                        #There are no more untagged entries
                        raise ValueError("No more untagged posts")

                    full_post = untagged_post.text

                    #Get the context of the post if it exists
                    context = []

                    parent_post_name = untagged_post.parent_id

                    while (parent_post_name is not None):
                        parent_post = Post.query.filter_by(name = parent_post_name).\
                            first()
                        if parent_post is None:
                            break
                        else:
                            parent_post_name = parent_post.parent_id
                            context.append(parent_post.text)

                    #Reverse it to get in sequential order
                    if context: context.reverse()

                    untagged_line = Line.query.filter_by(post_id=untagged_post.id).\
                        filter(Line.rating == None).order_by(Line.id).first()
                    entry = untagged_line.text

                    untagged_chunks = Chunk.query.filter_by(line_id = untagged_line.id).\
                        order_by(Chunk.id).all()

                    if untagged_chunks:
                        for u_chunk in untagged_chunks:
                            chunks.append(u_chunk.text)
                else:
                    l_rating = f['l_rating']
                    untagged_chunks = Chunk.query.filter_by(line_id = untagged_line.id).\
                        order_by(Chunk.id).all()
                    #Update the line rating
                    untagged_line.rating = int(l_rating)

                    #Update chunk ratings if they exist
                    if untagged_chunks:
                        for i, ut_chunk in enumerate(untagged_chunks):
                            if ('c_rating' + str(i)) in f:
                                chunk_rating = f['c_rating' + str(i)]
                                ut_chunk.rating = int(chunk_rating)

                    db.session.commit()

                    #Get the next line for display
                    try:
                        next_line = Line.query.filter_by(post_id=untagged_post.id).\
                            filter(Line.rating == None).order_by(Line.id).first()

                        if next_line is None:
                            isComplete = True
                            entry = None
                        else:
                            entry = next_line.text
                            #Fill the chunks
                            next_chunks = Chunk.query.filter_by(line_id=next_line.id).\
                                order_by(Chunk.id).all()
                            if next_chunks:
                                for n_chunk in next_chunks:
                                    chunks.append(n_chunk.text)
                    except Exception as e:
                        raise ValueError("Ooops")
        except ValueError as e:
            errors.append(e)
    return render_template('index.html', errors=errors, entry=entry,
            start=start, context = context, chunks = chunks,
             full_post = full_post)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
