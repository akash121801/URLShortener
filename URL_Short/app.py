from flask import Flask,render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import string
import random

from sqlalchemy.engine import url


app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db=SQLAlchemy(app)

class URL(db.Model):
    id_=db.Column("id_", db.Integer, primary_key=True)
    long=db.Column("long", db.String())
    short=db.Column("short", db.String(3))
    
    def _init_(self, long, short):
        self.long=long
        self.short=short

@app.before_first_request
def create_tables():
    db.create_all()

def shorten_url():
    letters=string.ascii_letters + string.ascii_uppercase
    while True:
        rand_letters=random.choices(letters, k=3)
        rand_letters="".join(rand_letters)
        short_url=URL.query.filter_by(short=rand_letters).first()
        if not short_url:
            return rand_letters

@app.route('/', methods=['POST', 'GET'])
def hello():
    if request.method=="POST":
        url_received=request.form["original_url"]
        #Check if URL is already in DB
        found_url=URL.query.filter_by(long=url_received).first()
        if found_url:
            return redirect(url_for("display_short_url", url=found_url.short))
        else:
            short_url=shorten_url()
            new_url=URL(long=url_received, short=short_url)
            db.session.add(new_url)
            db.session.commit()
            return redirect(url_for("display_short_url", url=short_url))
    else:
        return render_template('index.html')

@app.route('/display/<url>')
def display_short_url(url):
    return render_template('shorturl.html', short_url_display=url)

@app.route('/<short_url>')
def redirection(short_url):
    url_exists=URL.query.filter_by(short=short_url).first()
    if url_exists:
        return redirect(url_exists.long)
    else:
        return f'<h1> URL Does Not Exist</h1>'

if __name__ == 'main':
    app.run(port=5000, debug=True)