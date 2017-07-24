import os
import shutil
import sqlite3
import numpy as np

import PIL
from PIL import Image, ImageDraw

from flask import Flask, request, session, g, redirect, url_for, abort, \
	render_template, flash, make_response
from functools import wraps, update_wrapper
from datetime import datetime

app = Flask(__name__)

app.config.from_object(__name__) # get config settings from this file

#######################	 CONFIG STUFF 	##################################
'''DATABASE: This database stores the results of any person's left or 
right swipes on various image pairs, along with any 

DEEP_FASHION_IMAGES: assumes that any time we need to access a 
particular image, we'll always just be looking in one of the many 
subfolders is that directory. All image references can be passed in relative 
to this particular path

BBOX_FILE: This is consulted any time we get a path to an image from
the AB pairs file and need to find the bounding boxes to draw over it
 '''
with app.open_resource('static/to_dropbox/DeepFashion/list_bbox.txt', 'r') as f:
	raw_bbox_lines = f.readlines()
	bbox_information = [v.split() for v in raw_bbox_lines]

new_config = {'DATABASE': os.path.join(app.root_path, 'couch_tinder.db'),
			  'DEEP_FASHION_IMAGES': 'static/to_dropbox/DeepFashion/img/',
			  'SECRET_KEY': 'blue; no, yellow!'
			  }
app.config.update(new_config)

'''Silent will ignore this if FLASKR_SETTINGS is not present'''
app.config.from_envvar('FLASKR_SETTINGS', silent = True)

#######################	 END CONFIG STUFF 	#############################


#######################	 DATABASE HELPER FUNCTIONS	######################
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


#######################	 FILES AND IMAGES HELPER FUNCTIONS	############

def get_AB_testing_pairs():
	if not hasattr(g, 'AB_testing_pairs'):
		with app.open_resource('web_app_AB_pairs.txt', mode = 'r') as f:
			AB_pairs = f.readlines()
			g.AB_testing_pairs = AB_pairs
	return g.AB_testing_pairs

def get_bbox_coords(txt_file_path):
	'''
	For now, assumes that you input an image path
	from within the DEEP_FASHION_IMAGES directory of config.

	This goes ahead and gets the bounding box coordinates
	of said image as a list of integers corresponding to
	x_1, y_1, x_2, y_2
	'''
	bbox_img_path = os.path.join('img', txt_file_path)
	img_row = [v for v in app.config['BBOX_FILE'] if v[0] == bbox_img_path]
	if not img_row:
		return None
	coords = img_row[0][1:]
	return [int(v) for v in coords]

def make_bbox_image(txt_file_path, bbox_coords):
	'''
	Once you have the coordinates from above, this function
	takes the same path from above and returns a version with
	the bounding box lines drawn over it.

	The output of this function can be saved into static to be
	served on the models template.  Only quirk there is that RGBA
	images can't be saved as JPEGS
	'''
	in_img = os.path.join(app.config['DEEP_FASHION_IMAGES'], txt_file_path)
	base = PIL.Image.open(in_img).convert('RGBA')
	rect = PIL.Image.new('RGBA', base.size, (255,255,255,0))
	d = ImageDraw.Draw(base)
	lower_corner = tuple(bbox_coords[:2])
	upper_corner = tuple(bbox_coords[2:])
	d.rectangle((lower_corner, upper_corner), outline = 'red')
	return PIL.Image.alpha_composite(base, rect)


#######################	 END FILES AND IMAGES HELPER FUNCTIONS	###########

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

		if request.form['match'] == 'Match!':
			flash('You totally judged that couch matched')
			matching = 1
		else:
			flash("You said those didn't match")
			matching = 0
			
		db = get_db()
		INSERT_QUERY = '''
		INSERT INTO user_feedback
		(pair_file_1, pair_file_2, model, user_vote, comment)
		VALUES (?,?,?,?,?)
		'''
		INSERT_DATA = [request.form['image_1'], 
			 		   request.form['image_2'], 
			 		   request.form['model'], 
			 		   matching, 
			 		   request.form['comment']]
		db.execute(INSERT_QUERY,INSERT_DATA)
		db.commit()
	return redirect(url_for('models'))

