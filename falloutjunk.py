import sqlite3
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
    for row in cursor.fetchall():
        entry = {
            'slug': row[1], 'name': row[2], 'value': row[3], 'weight': row[4],
            'ratio': row[3] / row[4]}
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
            float(request.form['weight'])]
        )
    g.db.commit()
    flash('Component was successfully created')
    return redirect(url_for('show_components'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Incorrect username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Incorrect password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_components'))

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_components'))

if __name__ == '__main__':
    app.run()
