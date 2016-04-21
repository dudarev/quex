from main import app
from models import Question


@app.route('/cron/fetch_new_questions_answers')
def fetch_new_questions_answers():
    res = Question.fetch_new_questions_answers()
    return "Questions updated: {}".format(res)


@app.route('/cron/fetch_old_questions_answers')
def fetch_old_questions_answers():
    res = Question.fetch_old_questions_answers()
    return "Questions updated: {}".format(res)
