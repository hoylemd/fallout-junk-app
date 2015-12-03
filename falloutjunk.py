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
def index():
    return redirect(url_for('show_junk'))


@app.route('/components')
def show_components():
    cursor = g.db.execute('select * from components order by id desc;')
    entries = []
    for row in cursor.fetchall():
        entry = {
            'slug': row[1], 'name': row[2], 'value': row[3], 'weight': row[4],
            'ratio': row[3] / row[4]}
        entries.append(entry)
    return render_template('show_components.html', entries=entries)


@app.route('/add_component', methods=['POST'])
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
    flash('Component "' + request.form['name'] + '" was successfully created')
    return redirect(url_for('show_components'))


@app.route('/junk')
def show_junk():
    cursor = g.db.execute('select * from junk order by id desc;')
    entries = []
    for row in cursor.fetchall():
        entry = {
            'slug': row[1], 'name': row[2], 'value': row[3], 'weight': row[4],
            'ratio': row[3] / row[4], 'components_value': row[5],
            'components_weight': row[6], 'components_ratio': row[5] / row[6],
            'craftable': 'yes' if row[7] else 'no',
            'used_for_crafting': 'yes' if row[8] else 'no'}
        entries.append(entry)
    return render_template('show_junk.html', entries=entries)


def get_flag_from_form(form, key):
    return 1 if (key in form) and (form[key] == 'on') else 0


def build_insert_cursor(table, fields, values):
    query = 'insert into (' + ', '.join(fields) + ') ' + \
            'values (' + ', '.join(['?' for i in fields]) + ')'

    return g.db.execute(query, values)


@app.route('/add_junk', methods=['POST'])
def add_junk():
    if not session.get('logged_in'):
        abort(401)
    fields = ['slug', 'name', 'value', 'weight', 'components_value',
              'components_weight', 'craftable', 'used_for_crafting']

    slug = request.form['name'].lower().replace(' ', '_')
    craftable = get_flag_from_form(request.form, 'craftable')
    used_for_crafting = get_flag_from_form(request.form, 'used_for_crafting')
    values = [
        slug, request.form['name'], int(request.form['value']),
        float(request.form['weight']), int(request.form['components_value']),
        float(request.form['components_weight']), craftable, used_for_crafting]

    build_insert_cursor('junk', fields, values)

    g.db.commit()
    flash('Junk "' + request.form['name'] + '" was successfully created')
    return redirect(url_for('show_junk'))


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
