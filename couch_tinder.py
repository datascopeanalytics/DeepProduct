import os
import shutil
import sqlite3
import numpy as np

from flask import Flask, request, session, g, redirect, url_for, abort, \
	render_template, send_from_directory, flash, current_app

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

'''Assuming we have information to the effect of "this model
recommended that these images go together" in some source 
text file, this makes sure that the current application
context has a representation of those pairs
'''
def access_model_pairs():
	if not hasattr(g, 'model_pairs'):
		with app.open_resource('web_app_AB_pairs.txt', mode = 'r') as f:
			g.model_pairs = f.readlines()
	return g.model_pairs


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


@app.route('/models', defaults = {'served_pair':None})
# If we're always going to be choosing randomly, not sure
# if this defaults option is even necessary
def models(served_pair = None):

	if not served_pair:
		all_pairs = access_model_pairs()
		served_pair = np.random.choice(all_pairs, 1).item()
		# FIX THIS STUFF.....
		pair_model = served_pair.split()[0]
		pair_img_1 = os.path.join(app.config['DEEP_FASHION_IMAGES'], served_pair.split()[1])
		pair_img_2 = os.path.join(app.config['DEEP_FASHION_IMAGES'], served_pair.split()[2])
		#return redirect(url_for('models', model_name = model_name, pair_name = pair_name))

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

# if __name__ == '__main__':
# 	with app.open_resource('web_app_AB_pairs.txt', mode = 'r') as f:
# 		model_pairs = f.readlines()
# 		import pdb
# 		pdb.set_trace()
