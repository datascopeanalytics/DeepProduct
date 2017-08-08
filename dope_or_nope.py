import os
import shutil
import sqlite3
import numpy as np

from flask import Flask, request, session, g, redirect, url_for, abort, \
	render_template, flash, make_response

app = Flask(__name__)

app.config.from_object(__name__) # get config settings from this file

#######################	 CONFIG STUFF 	##################################
'''DATABASE: This database stores the results of any person's left or 
right swipes on various image pairs, along with any 

DEEP_FASHION_IMAGES: assumes that any time we need to access a 
particular image, we'll always just be looking in one of the many 
subfolders is that directory. All image references can be passed in relative 
to this particular path

DEMO_PAIRS: Quality controls for which pairs we view in what order for potentially
showing parts of this to a client.  
 '''

with app.open_resource('secret_key.txt','r') as f:
	l337h4xx = f.readlines()[0]

new_config = {'DATABASE': os.path.join(app.root_path, 'dope_nope.db'),
			  'DEEP_FASHION_IMAGES': 'static/to_dropbox/DeepFashion/',
			  'SECRET_KEY': l337h4xx,
			  'DEMO_PAIRS':[101,447,1445, 224, 922, 1296]
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
	with app.open_resource('dope_nope_schema.sql', mode = 'r') as f:
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

#######################	 END DATABASE HELPER FUNCTIONS	################


#######################	 FILES AND IMAGES HELPER FUNCTIONS	############

def get_AB_testing_pairs():
	if not hasattr(g, 'AB_testing_pairs'):
		with app.open_resource('all_pairs.txt', mode = 'r') as f:
			AB_pairs = f.readlines()
			g.AB_testing_pairs = AB_pairs
	return g.AB_testing_pairs

#######################	 END FILES AND IMAGES HELPER FUNCTIONS	###########

'''The home page populates from all_pairs.txt. Before doing so, though,
it makes sure to choose randomly from text file rows that have four
unique images in them
'''
@app.route('/')
def home(n_jpgs = 4):
	AB_pairs = [v.split() for v in get_AB_testing_pairs()]
	four_img_lines = [v for v in AB_pairs if len(v) == 5]
	four_uniq_lines = [v for v in four_img_lines if len(set(v[1:])) == 4]
	chosen_idx = np.random.choice(np.arange(len(four_uniq_lines)),1).item()
	chosen_imgs = four_uniq_lines[chosen_idx][1:]
	data = {}
	for i, jpg in enumerate(chosen_imgs):
		jpg_path = os.path.join(app.config['DEEP_FASHION_IMAGES'], jpg)
		data[i] = '/'.join(jpg_path.split('/')[1:])
	return render_template('index.html', data = data)

'''Assuming that we always want to route back to a random page in our A/B
testing, this should work. Every time a request is made, we open up our
reference text file, choose a random row, split it into its constituent parts 
(first element = model, second element = first_image, third_element = second_image).

We then retrieve those images (and their bounding-box-drawn copies), put them in
the data template, and pass the template on to be rendered
'''
@app.route('/models')
def models():
	AB_pairs = get_AB_testing_pairs()
	served_pair = np.random.choice(AB_pairs,1).item().split()
	pair_model = served_pair[0]
	pair_img_1 = os.path.join(app.config['DEEP_FASHION_IMAGES'], served_pair[1])
	fname, fext = os.path.splitext(pair_img_1)
	pair_bbox_1 = '{}_bbox.png'.format(fname) 
	
	pair_img_2 = os.path.join(app.config['DEEP_FASHION_IMAGES'], served_pair[2])
	fname, fext = os.path.splitext(pair_img_2)
	pair_bbox_2 = '{}_bbox.png'.format(fname)
	

	data = {'model_served':pair_model,
	        'image_1_path':'/'.join(pair_img_1.split('/')[1:]),
	        'image_2_path':'/'.join(pair_img_2.split('/')[1:]),
		'image_1_bbox':'/'.join(pair_bbox_1.split('/')[1:]),
		'image_2_bbox':'/'.join(pair_bbox_2.split('/')[1:])
	        }
	return render_template('models.html', data = data)


@app.route('/demo', defaults={'pair_idx':None})
@app.route('/demo/<int:pair_idx>')
def demo(pair_idx):
	AB_pairs = get_AB_testing_pairs()
	if not pair_idx:
		pair_idx = app.config['DEMO_PAIRS'][0]
		return redirect(url_for('demo', pair_idx = pair_idx))

	served_pair = AB_pairs[pair_idx].split()
	pair_model = served_pair[0]
	pair_img_1 = os.path.join(app.config['DEEP_FASHION_IMAGES'], served_pair[1])
	fname, fext = os.path.splitext(pair_img_1)
	pair_bbox_1 = '{}_bbox.png'.format(fname) 
	
	pair_img_2 = os.path.join(app.config['DEEP_FASHION_IMAGES'], served_pair[2])
	fname, fext = os.path.splitext(pair_img_2)
	pair_bbox_2 = '{}_bbox.png'.format(fname)

	# Figure out which of the listed DEMO_PAIRS you are on, and set the
	# next pair.  If there is no next pair, set the next_idx attribute as none.
	loc_in_sequence = app.config['DEMO_PAIRS'].index(pair_idx)
	try:
		next_idx = app.config['DEMO_PAIRS'][loc_in_sequence + 1]
	except IndexError as e:
		next_idx = ''

	data = {'current_pair':pair_idx,
			'next_pair':next_idx,
			'model_served':pair_model,
	        'image_1_path':'/'.join(pair_img_1.split('/')[1:]),
	        'image_2_path':'/'.join(pair_img_2.split('/')[1:]),
		'image_1_bbox':'/'.join(pair_bbox_1.split('/')[1:]),
		'image_2_bbox':'/'.join(pair_bbox_2.split('/')[1:])
	        }
	return render_template('demo.html', data = data)


@app.route('/judgement', methods=['POST'])
def judgement():
	if request.method == 'POST':
		print(request.form)
		print(request.form['match'])

		if request.form['match'] == 'Match!':
			flash('You said that pair was dope!')
			matching = 1
		else:
			flash("To that pair, you said nope!")
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
	# If you're in the demo view of stuff, redirect to the demo page.
	# Otherwise, go to the models page
	if request.form['pair_idx'] and request.form['next_idx']:
		return redirect(url_for('demo', pair_idx=request.form['next_idx']))
	elif request.form['pair_idx']:
		return redirect(url_for('home'))
	return redirect(url_for('models'))

@app.route('/leaderboard')
def leaderboard():
	db = get_db()
	LEAD_QUERY = '''
	SELECT model, SUM(user_vote) AS pos_votes, COUNT(1) AS votes
	FROM user_feedback 
	GROUP BY model 
	ORDER BY pos_votes DESC
	'''

	ranked_models = [row for row in db.execute(LEAD_QUERY).fetchall()]
	data = {}
	data['model_indices'] = [i+1 for i in range(len(ranked_models))]
	for rank, result in enumerate(ranked_models):
		rank_val = rank + 1
		rank_dict = {}
		name_key = 'model_name'
		rank_dict[name_key] = result['model']
		vote_key = 'model_votes'
		rank_dict[vote_key] = result['votes']
		match_key = 'model_matches'
		rank_dict[match_key] = result['pos_votes']
		data[rank_val] = rank_dict

	BEST_PAIR_QUERY = '''
	SELECT model, pair_file_1, pair_file_2,
	SUM(user_vote) AS pos_votes, COUNT(1) AS votes
	FROM user_feedback
	WHERE model = '{}'
	GROUP BY model, pair_file_1, pair_file_2
	ORDER BY pos_votes DESC LIMIT 1
	'''.format(data[1]['model_name'])

	best_pair = [row for row in db.execute(BEST_PAIR_QUERY).fetchall()]
	for result in best_pair:
		data[1]['top_pair_1'] = result['pair_file_1']
		data[1]['top_pair_2'] = result['pair_file_2']
		data[1]['top_pair_approvals'] = result['pos_votes']

	return render_template('leaderboard.html', data = data)


if __name__ == '__main__':
	app.run(host='0.0.0.0')
