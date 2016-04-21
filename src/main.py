from flask import Flask, render_template, request
from google.appengine.api import memcache

from models import Question

app = Flask(__name__)


import admin
import cron
import questions
import tasks


TOTAL_COUNT_CACHE_TIME = 3600
QUESTIONS_PER_PAGE = 20


@app.route('/')
def main():
    start = int(request.args.get('start', 0))
    questions = Question.query().order(-Question.created_at).fetch(QUESTIONS_PER_PAGE, offset=start)
    total_questions_count = memcache.get('total_questions_count')
    if not total_questions_count:
        total_questions_count = Question.query().count()
        memcache.set('total_questions_count', total_questions_count, TOTAL_COUNT_CACHE_TIME)
    if total_questions_count > start + QUESTIONS_PER_PAGE:
        next_start = start + QUESTIONS_PER_PAGE
    else:
        next_start = 0
    previous_start = start - QUESTIONS_PER_PAGE
    context = {
        'next_start': next_start,
        'previous_start': previous_start,
        'questions': questions,
    }
    return render_template('index.html', **context)


if __name__ == '__main__':
    app.run()
