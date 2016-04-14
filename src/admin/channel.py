from flask import redirect, render_template, request

from decorators import admin_required
from main import app
from models import Channel


@app.route('/admin/channel')
@admin_required
def channels():
    cs = Channel.query().order(Channel.title).fetch()
    return render_template('admin/channel/index.html', channels=cs)


@app.route('/admin/channel/add', methods=['GET', 'POST'])
@admin_required
def add():
    if request.method == 'POST':
        c = Channel()
        c.title = request.form.get('title', '')
        c.link = request.form.get('link', '')
        c.type = request.form.get('type', 'in')
        c.put()
        return redirect('/admin/channel', code=303)
    return render_template('admin/channel/add.html')


@app.route('/admin/channel/<int:channel_id>')
@admin_required
def channel(channel_id):
    c = Channel.get_by_id(channel_id)
    return render_template('admin/channel/channel.html', channel=c)


@app.route('/admin/channel/<int:channel_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit(channel_id):
    c = Channel.get_by_id(channel_id)
    if request.method == 'POST':
        c.title = request.form.get('title', '')
        c.put()
        return redirect('/admin/channel', code=303)
    return render_template('admin/channel/edit.html', channel=c)


@app.route('/admin/channel/<int:channel_id>/delete', methods=['GET', 'POST'])
@admin_required
def delete(channel_id):
    c = Channel.get_by_id(channel_id)
    if request.method == 'POST':
        c.key.delete()
        return redirect('/admin/channel', code=303)
    return render_template('admin/channel/delete.html', channel=c)
