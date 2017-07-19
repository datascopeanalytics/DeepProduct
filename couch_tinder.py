import os
import shutil
import sqlite3
import numpy as np

from flask import Flask, request, session, g, redirect, url_for, abort, \
	render_template, send_from_directory, flash

app = Flask(__name__)

app.config.from_object(__name__) # get config settings from this file

############	QUESTIONABLY USEFUL DATABASE FUNCTIONS 	 ##########################
'''Allows app to recognize a sqlite database couch_tinder.db, should we need it.
Working idea is that this might be updated every time someone "swipes right" on
 a couch pair one of our models suggests.

UPLOAD FOLDER is what allows for random loading of couches on the index
 '''
new_config = {'DATABASE': os.path.join(app.root_path, 'couch_tinder.db'),
			  'INDEX_UPLOAD_FOLDER': 'Data/OpenImages/Couch',
			  'SECRET_KEY': 'blue; no, yellow!'
			  }
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
	with app.open_resource('couch_tinder_schema.sql', mode = 'r') as f:
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
def home(n_jpgs = 4):
	src_dir = app.config['INDEX_UPLOAD_FOLDER']
	dest_dir = 'static/img'
	sampled = np.random.choice(os.listdir(src_dir), size = n_jpgs, replace = False)
	data = {}
	for i, jpg in enumerate(sampled):
		jpg_path = os.path.join(src_dir, jpg)
		dest_path = os.path.join(dest_dir, f'index_{i}')
		shutil.copyfile(jpg_path, dest_path)
		data[i] = '/'.join(dest_path.split('/')[1:])
	return render_template('index.html', data = data)

@app.route('/models/<model_name>/<pair_name>/')
def models(model_name, pair_name):

	# model_name = request.args.get('model_name')
	# pair_name = request.args.get('pair_name')

	# # if not model_name and not request.args.get('model_name'):
	# # 	model_name = 'CNN1'
	# # if not pair_name and not request.args.get('pair_name'):
	# # 	pair_name = 'pair1'

	data = {'model_name':model_name,
	        'pair_name':pair_name,
	        'image_1_path':f'models/{model_name}/pairs/{pair_name}/img1.jpg',
	        'image_2_path':f'models/{model_name}/pairs/{pair_name}/img2.jpg'
	        }

	return render_template('models.html', data = data)

@app.route('/judgement', methods=['POST'])
def judgement():
	if request.method == 'POST':
		print(request.form)
		print(request.form['match'])
		if 'flag' in request.form and request.form['flag']:
			flash('You flagged this one, yo')
		if request.form['match'] == 'Match!':
			flash('You totally judged that couch matched')
		else:
			flash("You said those didn't match")
	return redirect(url_for('models'))
