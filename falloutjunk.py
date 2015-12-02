import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash

# configuration
DATABASE = '/tmp/falloutjunk.db'
DEBUG = True
SECRET_KEY = 'marhmallows'
USERNAME = 'admin'
PASSWORD = 'buttslol'


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

app = Flask(__name__)
app.config.from_object(__name__)

if __name__ == '__main__':
    app.run()
