from main import app
from models import Question


@app.route('/cron/add_to_search_index')
def add_to_search_index():
    res = Question.add_batch_to_search_index()
    return "Questions added to search index: {}".format(res)
