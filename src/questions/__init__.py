from google.appengine.ext import ndb
from flask import render_template

from main import app
from models import Answer, Question


@app.route('/q/<key>')
def question(key):
    q = ndb.Key(urlsafe=key).get()
    channel = q.channel.get()
    answers = Answer.query(Answer.question == q.key).fetch(Question.MAX_ANSWERS_NUMBER)
    context = {
        'question': q,
        'channel': channel,
        'answers': answers,
    }
    return render_template('question/index.html', **context)
