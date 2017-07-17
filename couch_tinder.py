import os
import sqlite3

from flask import Flask, request, session, g, redirect, url_for, abort, \
	render_template


app = Flask(__name__)

app.config.from_object(__name__) # get config settings from this file

############	QUESTIONABLY USEFUL DATABASE FUNCTIONS 	 ##########################
'''Allows app to recognize a sqlite database couch_tinder.db, should we need it.  
Working idea is that this might be updated every time someone "swipes right" on
 a couch pair one of our models suggests.  Could also be used to load pairs
 to populate the pages'''
new_config = {'DATABASE': os.path.join(app.root_path, 'couch_tinder.db')}
app.config.update(new_config)

'''Silent will ignore this if FLASKR_SETTINGS is not present'''
app.config.from_envvar('FLASKR_SETTINGS', silent = True)

def connect_db():
	'''Not sure if returning the db with a dictionary for each row will
	be useful'''
	rv = sqlite3.connect(app.config['DATABASE'])
	rv.row_factory = sqlite3.Row # Treats rows as dictionaries instead of tuples
	return rv

def get_db():
	''' Opens a new database connection if there isn't one in the
	current application context
	'''
	if not hasattr(g, 'sqlite_db'):
		g.sqlite_db = connect_db()
	return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
	'''Closes the database again at the end of a request'''
	if hasattr(g, 'sqlite_db'):
		g.sqlite_db.close()

def init_db():
	db = get_db()
	with app.open_resource('schema.sql', mode = 'r') as f:
		db.cursor().executescript(f.read())
	db.commit()

'''The command line decorator creates a new command with 
the flask script.  Running flask initdb will wipe whatever
exists in 'couch_tinder.db' and redefine it according to
schema.sql
'''
@app.cli.command('initdb')
def initdb_command():
	'''Initializes the database'''
	init_db()
	print('Initialized the database')

############	END QUESTIONABLY USEFUL DATABASE FUNCTIONS 	 ##################

@app.route('/')
def home():
	return render_template('base.html')