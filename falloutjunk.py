import sqlite3
from decimal import Decimal
from flask import Flask, g, render_template, session, abort, request, \
    redirect,  url_for, flash
from contextlib import closing

# configuration
DATABASE = '/tmp/falloutjunk.db'
DEBUG = True
SECRET_KEY = 'marhmallows'
USERNAME = 'admin'
PASSWORD = 'buttslol'


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


app = Flask(__name__)
app.config.from_object(__name__)


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def after_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/')
def show_components():
    cursor = g.db.execute('select * from components order by id desc;')
    entries = []
    for row in cursor.fetchal():
        entry = {
            'slug': row[0], 'name': row[1], 'value': row[2], 'weight': row[3]}
        entries.append(entry)
    return render_template('show_components.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_component():
    if not session.get('logged_in'):
        abort(401)
    slug = request.form['name'].lower().replace(' ', '_')
    query = 'insert into components (slug, name, value, weight)' + \
        ' values (?, ?, ?, ?)'
    g.db.execute(
        query,
        [
            slug, request.form['name'], int(request.form['value']),
            Decimal(request.form['value'])]
        )
    g.db.commit()
    flash('Component was successfully created')
    return redirect(url_for('show_components'))

if __name__ == '__main__':
    app.run()
