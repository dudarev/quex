from google.appengine.ext import ndb
from flask import render_template

from main import app
from models import Question


@app.route('/q/<key>')
def question(key):
    q = ndb.Key(urlsafe=key).get()
    c = q.channel.get()
    context = {
        'question': q,
        'channel': c,
    }
    return render_template('question/index.html', **context)
