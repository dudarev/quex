from main import app
from models import Channel


@app.route('/cron/fetch_new_questions')
def fetch_new_questions():
    res = ''
    channels = Channel.query().fetch(Channel.MAXIMUM_CHANNELS_NUMBER)
    for c in channels:
        c.fetch_new_questions()
        res += u'Channel: {}<br/>{}<br/>'.format(c.title, c.data)
    return res


@app.route('/cron/fetch_old_questions')
def fetch_old_questions():
    res = ''
    channels = Channel.query().fetch(Channel.MAXIMUM_CHANNELS_NUMBER)
    for c in channels:
        c.fetch_old_questions()
        res += u'Channel: {}<br/>{}<br/>'.format(c.title, c.data)
    return res
