from flask import request, render_template
from google.appengine.api import search

from helpers import stem_and_lower
from main import app
from models import Question


@app.route('/search')
def search_view():
    index = search.Index(name=Question.SEARCH_INDEX_NAME)
    query = request.args.get('q', '')
    results = index.search(stem_and_lower(query))
    questions = []
    for doc in results.results:
        res = {'key': doc.doc_id}
        for field in doc.fields:
            if field.name == 'title':
                res['title'] = field.value
            if field == 'created_at':
                res['created_at'] = field.value
        questions.append(res)
    return render_template('search.html', **{'questions': questions})
