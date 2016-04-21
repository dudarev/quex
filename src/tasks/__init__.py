from google.appengine.ext import ndb

from main import app


@app.route('/tasks/q/<key>/fetch_answers')
def fetch_question_answers(key):
    q = ndb.Key(urlsafe=key).get()
    q.fetch_answers()
    return 'Answers updated'
