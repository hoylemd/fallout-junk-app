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


# Helper functions
def parse_optional(form, key, dictionary, force_value=None):
    if key in form:
        dictionary[key] = form[key] if force_value is None else force_value
    return dictionary


def build_insert_cursor(table, fields):
    columns = []
    values = []
    for key, value in fields.iteritems():
        columns.append(key)
        values.append(value)

    query = 'insert into ' + table + ' (' + ', '.join(columns) + ') '
    query += 'values (' + ', '.join(['?' for i in values]) + ')'
    query += ';'

    return g.db.execute(query, values)


def build_select_cursor(table, fields=None, where=None, order_by=None):
    query = 'select ' + (', '.join(fields) if fields is not None else '*')
    query += ' from ' + table
    if where is not None:
        query += ' where ' + where
    if order_by is not None:
        query += ' order by ' + order_by
    query += ';'

    return g.db.execute(query)


# validation functions
def missing_required_fields(form, fields):
    for field in fields:
        if field not in form:
            return True
    return False


# app setup functions
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
    cursor = build_select_cursor('components', order_by='id desc')
    entries = []
    for row in cursor.fetchall():
        entry = {
            'slug': row[1], 'name': row[2], 'value': row[3], 'weight': row[4],
            'ratio': row[3] / row[4]}
        entries.append(entry)
    return render_template('show_components.html', entries=entries)


@app.route('/add_component', methods=['POST'])
def add_component():
    # set ecceptable and required fields
    required_fields = ['name', 'value', 'weight']

    # check for erroneous requests
    if not session.get('logged_in'):
        abort(401)
    if missing_required_fields(request.form, required_fields):
        abort(422)

    # build the values dictionary
    values = {}
    values['slug'] = request.form['name'].lower().replace(' ', '_')
    values['name'] = str(request.form['name'])
    values['value'] = int(request.form['value'])
    values['weight'] = float(request.form['value'])

    # update the database
    build_insert_cursor('components', values)
    g.db.commit()

    # feedback
    flash('Component "' + request.form['name'] + '" was successfully created')
    return redirect(url_for('show_components'))


@app.route('/junk')
def show_junk():
    cursor = build_select_cursor('junk', order_by='id desc')
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


@app.route('/add_junk', methods=['POST'])
def add_junk():
    # set ecceptable and required fields
    required_fields = ['name', 'value', 'weight']
    optional_fields = ['components_value', 'components_weight']
    flags = ['craftable', 'used_for_crafting']

    # check for erroneous requests
    if not session.get('logged_in'):
        abort(401)
    if missing_required_fields(request.form, required_fields):
        abort(422)

    # build the values dictionary
    values = {}
    values['slug'] = request.form['name'].lower().replace(' ', '_')
    values['name'] = str(request.form['name'])
    values['value'] = int(request.form['value'])
    values['weight'] = float(request.form['value'])
    for field in optional_fields:
        values = parse_optional(request.form, field, values)
    for field in flags:
        values = parse_optional(request.form, field, values, force_value=1)

    # update the database
    build_insert_cursor('junk', values)
    g.db.commit()

    # feedback
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
