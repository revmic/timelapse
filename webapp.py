import os
import sqlite3
from flask import Flask, request, session, g, redirect, \
    url_for, abort, render_template, flash

''' CONFIGURATION '''
# Create application
app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environ var
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'timelapse.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='pass'
))
app.config.from_envvar('TIMELAPSE_SETTINGS', silent=True)

''' MODEL '''
def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('bin/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def get_db():
    """
    Opens a new db connection if there is none yet for
    the current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

''' VIEW '''
@app.route('/')
def show_videos():
    db = get_db()
    cur = db.execute('select title, filename from tl_videos order by id desc')
    videos = cur.fetchall()
    return render_template('show_videos.html', videos=videos)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
