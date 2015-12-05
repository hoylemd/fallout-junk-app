from collections import namedtuple
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

# define Field namedtuple
Field = namedtuple('Field', 'name type_func required')
Field.__new__.__defaults__ = (True,)
"""
type_func determines the expected type for that field
integer: int
float: float
string: str
boolean: flag
"""


def flag(value):
    """
    Use this as the type_func in a Field tuple for flag-type fields
    It doesn't actually get used for field parsing though
    """
    if value == 'on' or value is True or value == 1:
        return 1
    else:
        return None


# Helper functions
def parse_request_form(form, fields):
    """
    Parses a request form into a values dict according to a fields spec

    form(request form): the form from the flask request object
    fields(array of Fields): the fields specification.
    """
    values = {}
    try:
        for field in fields:
            if field.type_func == flag:
                if field.name in form:
                    values[field.name] = 1
            elif field.required or field.name in form:
                values[field.name] = field.type_func(form[field.name])
    except (ValueError, KeyError):
        abort(422)

    return values


def build_insert_cursor(table, fields):
    """
    sets up a db cursor to insert into the given table the give fields

    table(string): name of the table to insert into
    fields(dict): column name mapped to the value to insert
    """
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


def create_component(request):
    # define fields
    fields = [Field('name', str), Field('value', int), Field('weight', float)]

    # check for erroneous requests
    if not session.get('logged_in'):
        abort(401)

    values = parse_request_form(request.form, fields)

    if len(values['name']) > 64:
        abort(413)

    values['slug'] = values['name'].lower().replace(' ', '_')

    # update the database
    build_insert_cursor('components', values)
    g.db.commit()

    # feedback
    flash('Component "' + request.form['name'] + '" was successfully created')
    return redirect(url_for('components'))


def read_components(request):
    cursor = build_select_cursor('components', order_by='id desc')
    entries = []
    for row in cursor.fetchall():
        entry = {
            'slug': row[1], 'name': row[2], 'value': row[3], 'weight': row[4],
            'ratio': row[3] / row[4]}
        entries.append(entry)
    return render_template('show_components.html', entries=entries)


@app.route('/components', methods=['GET', 'POST'])
def components():
    if request.method == 'GET':
        return read_components(request)
    elif request.method == 'POST':
        return create_component(request)


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
    # define fields
    fields = [
        Field('name', str), Field('value', int), Field('weight', float),
        Field('components_value', int, False),
        Field('components_weight', float, False),
        Field('craftable', flag), Field('used_for_crafting', flag)]

    # check for erroneous requests
    if not session.get('logged_in'):
        abort(401)

    values = parse_request_form(request.form, fields)

    if len(values['name']) > 64:
        abort(413)

    values['slug'] = values['name'].lower().replace(' ', '_')

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
            return redirect(url_for('components'))

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('components'))

if __name__ == '__main__':
    app.run()
