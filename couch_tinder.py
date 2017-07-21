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
			  'DEEP_FASHION_IMAGES': 'static/to_dropbox/DeepFashion/img/',
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

def get_AB_testing_pairs():
	if not hasattr(g, 'AB_testing_pairs'):
		with app.open_resource('web_app_AB_pairs.txt', mode = 'r') as f:
			AB_pairs = f.readlines()
			g.AB_testing_pairs = AB_pairs
	return g.AB_testing_pairs


############	END QUESTIONABLY USEFUL DATABASE FUNCTIONS 	 ##################

@app.route('/')
def home(n_jpgs = 4):
	src_dir = app.config['DEEP_FASHION_IMAGES']
	random_subdir = os.path.join(src_dir, np.random.choice(os.listdir(src_dir),1).item())
	sampled = np.random.choice(os.listdir(random_subdir), size = n_jpgs, replace = False)
	data = {}
	for i, jpg in enumerate(sampled):
		jpg_path = os.path.join(random_subdir, jpg)
		data[i] = '/'.join(jpg_path.split('/')[1:])
	return render_template('index.html', data = data)

'''Assuming that we always want to route back to a random page in our A/B
testing, this should work. Every time a request is made, we open up our
reference text file, choose a random row, split it into its constituent parts 
(first element = model, second element = first_image, third_element = second_image)
and serve those on the very same couch tinder layout we had before.
'''
@app.route('/models')
def models():
	AB_pairs = get_AB_testing_pairs()
	served_pair = np.random.choice(AB_pairs,1).item().split()
	pair_model = served_pair[0]
	pair_img_1 = os.path.join(app.config['DEEP_FASHION_IMAGES'], served_pair[1])
	pair_img_2 = os.path.join(app.config['DEEP_FASHION_IMAGES'], served_pair[2])

	data = {'model_served':pair_model,
	        'image_1_path':'/'.join(pair_img_1.split('/')[1:]),
	        'image_2_path':'/'.join(pair_img_2.split('/')[1:])
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

