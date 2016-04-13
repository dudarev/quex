from flask import render_template, request, redirect

from decorators import admin_required
from main import app
from models import Config


@app.route('/admin/config')
@admin_required
def config():
    c = Config.get()
    return render_template('admin/config/config.html', config=c)


@app.route('/admin/config/edit', methods=['GET', 'POST'])
@admin_required
def config_edit():
    c = Config.get()
    if request.method == 'POST':
        c.twitter_consumer_key = request.form.get('twitter_consumer_key', '')
        c.twitter_consumer_secret = request.form.get('twitter_consumer_secret', '')
        c.google_analytics_id = request.form.get('google_analytics_id', '')
        c.put()
        return redirect('/admin/config', code=303)
    return render_template('admin/config/edit.html', config=c)
