from main import app
from models import Channel


@app.route('/cron/fetch_questions')
def fetch_questions():
    c = Channel.get_oldest_fetched()
    c.fetch_questions()
    return u'Channel: {}<br/>{}'.format(c.title, c.data)
