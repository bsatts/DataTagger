import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')

WTF_CSRF_ENABLED = True
SECRET_KEY = 'this is weak security key'
RATINGSET = ["1", "2", "3", "4", "5"]
