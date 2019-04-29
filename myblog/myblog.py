import os
import sqlite3
from flask import Flask, request, session, g, url_for, redirect, abort, \
     render_template, flash
from functools import wraps
from datetime import datetime

app = Flask(__name__) #creating instances for app
app.config.from_object(__name__)
app.config.update(dict(
           DATABASE = os.path.join(app.root_path, 'myblog.db'),
           SECRET_KEY = ********,
           USERNAME = *******,
           PASSWORD = *******
))
app.config.from_envvar('MYBLOG_SETTINGS', silent=True)

# login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Please Login First')
            return redirect(url_for('login'))
    return wrap

def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    # initializes the database
    init_db()
    print('Initialized the database.')

# home page decorator
@app.route('/')
@app.route('/layout')
def layout():
    db = get_db()
    cur = db.execute('select title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('layout.html', entries=entries)

# show entries made in db
@app.route('/show')
@login_required
def show_entries():
    db = get_db()
    cur = db.execute('select title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)

# adding entry to db by logging in
@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values(?, ?)',
                 [request.form['title'], request.form['text']])
    db.commit()
    flash('new entry successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None # none is simplify empty or no value is here
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:   # != admin
            error = 'Invalid Username'
        elif request.form['password'] != app.config['PASSWORD']: # != default
            error = 'Invalid Password'
        else:
            session['logged_in'] = True
            flash('you have successfully logged in ')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('you have successfully logged out')
    # db = get_db()
    # cur = db.execute('select title, text from entries order by id desc')
    # entries = cur.fetchall()
    return redirect(url_for('layout'))
    #return render_template('logout.html')
