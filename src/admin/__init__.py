from channel import *
from config import *

from flask import render_template

from decorators import admin_required
from main import app


@app.route('/admin')
@admin_required
def admin():
    return render_template('admin/index.html')
