import os
import shutil
import sqlite3
import random

from flask import Flask, request, session, g, redirect, url_for, abort, \
        render_template, flash

app = Flask(__name__)

app.config.from_object(__name__) # get config settings from this file

#######################  CONFIG STUFF   ##################################
'''DATABASE: This database stores the results of any person's left or
right swipes on various image pairs, along with any

DEEP_FASHION_IMAGES: assumes that any time we need to access a
particular image, we'll always just be looking in one of the many
subfolders is that directory. All image references can be passed in relative
to this particular path

DEMO_PAIRS: Quality controls for which pairs we view in what order for potentially
showing parts of this to a client.

MODEL_DESCRIPS: This is a dictionary keyed with the seven possible models in
all_pairs.txt. The values are themselves dictionaries containing three html
strings used to describe each of the models on our leaderboard.
 '''

with app.open_resource('secret_key.txt','r') as f:
        l337h4xx = f.readlines()[0]

new_config = {'DATABASE': os.path.join(app.root_path, 'dope_nope.db'),
              'DEEP_FASHION_IMAGES': 'static/to_dropbox/DeepFashion/',
              'SECRET_KEY': l337h4xx,
              'DEMO_PAIRS':[101,447,1445, 224, 922, 1296],
              'MODEL_DESCRIPS':{
                  'FC6BH':{
                      'layer':'''<b>FC6:</b> The sixth fully connected layer of the <a 
                      href='http://www.robots.ox.ac.uk/~vgg/research/very_deep/'>VGG16</a>  
                      network''',
                      'dsource':'''<b>B:</b> trained on basic <a 
                      href='http://image-net.org/challenges/LSVRC/2017/index#introduction'
                      >ImageNet</a> classes''',
                      'metric':'''<b>H:</b> measuring nearest neighbors with <a
                      href='https://en.wikipedia.org/wiki/Hamming_distance'
                      >Hamming Distance</a>'''
                      },
                  'FC6FL2':{
                      'layer':'''<b>FC6:</b> The sixth fully connected layer of the <a 
                      href='http://www.robots.ox.ac.uk/~vgg/research/very_deep/'>VGG16</a>  
                      network''',
                      'dsource':'''<b>F:</b> retrained on the full <a
                      href='http://mmlab.ie.cuhk.edu.hk/projects/DeepFashion.html'
                      >DeepFashion</a> data set''',
                      'metric':'''<b>L2:</b> measuring nearest neighbors with <a
                      href='https://en.wikipedia.org/wiki/Euclidean_distance'
                      >L2 Distance</a>'''
                      },
                  'FC6FH':{
                      'layer':'''<b>FC6:</b> The sixth fully connected layer of the <a 
                      href='http://www.robots.ox.ac.uk/~vgg/research/very_deep/'>VGG16</a>  
                      network''',
                      'dsource':'''<b>F:</b> retrained on the full <a
                      href='http://mmlab.ie.cuhk.edu.hk/projects/DeepFashion.html'
                      >DeepFashion</a> data set''',
                      'metric':'''<b>H:</b> measuring nearest neighbors with <a
                      href='https://en.wikipedia.org/wiki/Hamming_distance'
                      >Hamming Distance</a>'''
                      },
                  'FC6SL2':{
                      'layer':'''<b>FC6:</b> The sixth fully connected layer of the <a 
                      href='http://www.robots.ox.ac.uk/~vgg/research/very_deep/'>VGG16</a>  
                      network''',
                      'dsource':'''<b>S:</b> retrained on a subset of the <a
                      href='http://mmlab.ie.cuhk.edu.hk/projects/DeepFashion.html'
                      >DeepFashion</a> data set''',
                      'metric':'''<b>L2:</b> measuring nearest neighbors with <a
                      href='https://en.wikipedia.org/wiki/Euclidean_distance'
                      >L2 Distance</a>'''
                      },
                  'FC6FLSH':{
                      'layer':'''<b>FC6:</b> The sixth fully connected layer of the <a 
                      href='http://www.robots.ox.ac.uk/~vgg/research/very_deep/'>VGG16</a>  
                      network''',
                      'dsource':'''
                      <b>F:</b> retrained on the full <a
                      href='http://mmlab.ie.cuhk.edu.hk/projects/DeepFashion.html'
                      >DeepFashion</a> data set''',
                      'metric':'''<b>LSH:</b> searching for neighbors with <a
                      href='https://en.wikipedia.org/wiki/Locality-sensitive_hashing'
                      >Locality-Sensitive Hashing</a>, measuring neighbors with <a
                      href='https://en.wikipedia.org/wiki/Euclidean_distance'
                      >L2 Distance</a>'''
                      },
                  'FC7BH':{
                      'layer':'''<b>FC6:</b> The seventh fully connected layer of the <a 
                      href='http://www.robots.ox.ac.uk/~vgg/research/very_deep/'>VGG16</a>  
                      network''',
                      'dsource':'''
                      <b>B:</b> trained on basic <a 
                      href='http://image-net.org/challenges/LSVRC/2017/index#introduction'
                      >ImageNet</a> classes''',
                      'metric':'''
                      <b>H:</b> measuring nearest neighbors with <a
                      href='https://en.wikipedia.org/wiki/Hamming_distance'
                      >Hamming Distance</a>
                      '''
                      },
                  'FC6MIH':{
                      'layer':'''<b>FC6:</b> The sixth fully connected layer of the <a 
                      href='http://www.robots.ox.ac.uk/~vgg/research/very_deep/'>VGG16</a>  
                      network, retrained on the full <a
                      href='http://mmlab.ie.cuhk.edu.hk/projects/DeepFashion.html'
                      >DeepFashion</a> data set''',
                      'dsource':'',
                      'metric':'''
                      <b>MIH:</b> searching for neighbors with <a
                      href='https://www.cs.toronto.edu/~norouzi/research/papers/multi_index_hashing.pdf'
                      >Multi-Index Hashing</a>, measuring neighbors with <a
                      href='https://en.wikipedia.org/wiki/Hamming_distance'
                      >Hamming Distance</a>'''
                      }
                  }
              }
app.config.update(new_config)

'''Silent will ignore this if FLASKR_SETTINGS is not present'''
app.config.from_envvar('FLASKR_SETTINGS', silent = True)

#######################  END CONFIG STUFF       #############################


#######################  DATABASE HELPER FUNCTIONS      ######################
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

#######################  END DATABASE HELPER FUNCTIONS  ################


#######################  FILES AND IMAGES HELPER FUNCTIONS      ############

def get_AB_testing_pairs():
        if not hasattr(g, 'AB_testing_pairs'):
                with app.open_resource('all_pairs.txt', mode = 'r') as f:
                        AB_pairs = f.readlines()
                        g.AB_testing_pairs = AB_pairs
        return g.AB_testing_pairs

#######################  END FILES AND IMAGES HELPER FUNCTIONS  ###########

'''The home page populates from all_pairs.txt. Before doing so, though,
it makes sure to choose randomly from text file rows that 

A) Have four unique images in them and
B) Were determined to fit "prettily" into the 224 X 224 image resolution

Only thing to consider in using random.randint: it selects from [a,b]
inclusive. So to use it as an index selector, you need to bound it
with len-1 instead of by len
'''
@app.route('/')
def home(n_jpgs = 4):
        AB_pairs = [v.split() for v in get_AB_testing_pairs()]
        four_img_lines = [v for v in AB_pairs if len(v) == 5]
        four_uniq_lines = [v for v in four_img_lines if len(set(v[1:])) == 4]
        pretty_pair_indices = [894,1103,779,725,1375,663,1836,264,\
                               890,564,1933,1068,1180]
        chosen_idx = random.randint(0,len(pretty_pair_indices) - 1)
        chosen_idx = pretty_pair_indices[chosen_idx]
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
@app.route('/models', defaults={'hash_str':None})
@app.route('/models/<string:hash_str>')
def models(hash_str):
        if not hash_str:
                hash_str = ''.join(random.choice('0123456789abcdef') for i in range(10))
                return redirect(url_for('models', hash_str = hash_str))
        AB_pairs = get_AB_testing_pairs()
        rand_idx = random.randint(0,len(AB_pairs)-1)
        served_pair = AB_pairs[rand_idx].split()
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
        data['total_votes'] = 0
        for rank, result in enumerate(ranked_models):
                rank_val = rank + 1
                rank_dict = {}
                rank_dict['model_name'] = result['model']
                rank_dict['tooltip_text'] = app.config['MODEL_DESCRIPS'][result['model']]
                rank_dict['model_votes'] = result['votes']
                rank_dict['model_matches'] = result['pos_votes']
                data['total_votes'] += rank_dict['model_votes']
                data[rank_val] = rank_dict


        result = get_top_pairs(data[1]['model_name'], 1).pop()
        data[1]['top_pair_1'] = result['pair_file_1']
        data[1]['top_pair_2'] = result['pair_file_2']
        data[1]['top_pair_approvals'] = result['pos_votes']

        return render_template('leaderboard.html', data = data)


def get_top_pairs(model_id, num_pairs):
        QUERY = '''
        SELECT model, pair_file_1, pair_file_2,
        SUM(user_vote) AS pos_votes, COUNT(1) AS votes
        FROM user_feedback
        WHERE model = ?
        GROUP BY model, pair_file_1, pair_file_2
        ORDER BY pos_votes DESC LIMIT ?
        '''
        PARAMS = [model_id, num_pairs]
        db = get_db()
        return db.execute(QUERY, PARAMS).fetchall()


@app.route('/pair_leaderboard/<model_id>')
def pair_leaderboard_for_a_model(model_id):
    N = 5
    return render_template('pair_leaderboard.html',
                           model_id = model_id,
                           top_pair_data = get_top_pairs(model_id, N))


if __name__ == '__main__':
        app.run(host='0.0.0.0')
