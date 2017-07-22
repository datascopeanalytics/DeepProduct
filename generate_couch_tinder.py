import numpy as np
import os
import shutil
import pandas as pd
import time

import PIL
from PIL import Image, ImageDraw

def create_directories(dirs_to_create, base_dir):
	'''
	Was originally created predicated on the idea
	that we would actually port over the images
	produced by the models into static

	Since we're symlinking to dropbox to get images now,
	this shouldn't be necessary 
	'''
	if not isinstance(dirs_to_create, list):
		dirs_to_create = [dirs_to_create]
	for direct in dirs_to_create:
		try:
			os.makedirs(os.path.join(base_dir, direct))
		except FileExistsError as e:
			continue

def random_number_of_images(base_dir, n_images):
	'''
	Selects n images from a random subdirectory and returns
	a list of n paths.  These paths are assumed to be
	appended onto 'DeepFashion/img' and are going to be
	in the form of SUBDIR_NAME/IMG_NAME.jpg

	Used to create "web_app_AB_pairs.txt", something that
	will likely be supplanted by a file that Nat provides
	'''
	random_subdir = np.random.choice(os.listdir(base_dir),1).item()
	path_to_subdir = os.path.join(base_dir, random_subdir)
	img_paths = []
	for v in np.random.choice(os.listdir(path_to_subdir), n_images, replace = False):
		full_path = os.path.join(random_subdir,v)
		img_paths.append(full_path)
	return img_paths

def gget_bbox_coords(input_image, bbox_file, method = 'pandas'):
	'''
	For now, assumes that you input an image path
	from within the img directory.  This function
	goes ahead and gets the bounding box coordinates

	Returns a list of integers corresponding to
	x_1, y_1, x_2, y_2

	The method = pandas argument is just me messing around
	to see if using pandas gives particular speedups
	'''
	input_image = os.path.join('img', input_image)

	if method == 'pandas':
		img_row = bbox_file[bbox_file.image_name == input_image]
		if len(img_row) == 0:
			return None
		return [img_row['x_1'], img_row['y_1'], img_row['x_2'], img_row['y_2']]

	else:
		img_row = [v for v in bbox_file if v[0] == input_image]
		if not img_row:
			return None
		coords = img_row[0][1:]
		return [int(v) for v in coords]


def make_bbox_image(input_image, bbox_coords):
	'''
	Once you have the coordinates from above, saves a modified form
	of the image with the box drawn on it
	'''
	input_image = os.path.join('Data', 'DeepFashion', 'img', input_image)
	base = PIL.Image.open(input_image).convert('RGBA')
	rect = PIL.Image.new('RGBA', base.size, (255,255,255,0))
	d = ImageDraw.Draw(base)
	lower_corner = tuple(bbox_coords[:2])
	upper_corner = tuple(bbox_coords[2:])
	d.rectangle((lower_corner, upper_corner), outline = 'red')
	return PIL.Image.alpha_composite(base, rect)



if __name__ =='__main__':
	
	IMG_FOLDER = 'Data/DeepFashion/img'
	method = 'kitten'	


	# Loading this once as a data frame will prevent us from having to
	# open and scan that text file many times within the application
	# I just hope that we can dump whatever we use into the app.config
	# (see no reason why not?)
	step = 'Opening File'
	t1 = time.time()
	print(step)
	
	if method == 'pandas':
		BOUNDING_BOX_FILE = pd.read_table('Data/DeepFashion/list_bbox.txt', sep = '\s+')
	else:
		with open('Data/DeepFashion/list_bbox.txt', 'r') as f:
			raw_lines = f.readlines()
			BOUNDING_BOX_FILE = [v.split() for v in raw_lines]
	t2 = time.time()
	print('{} took {:2f} seconds'.format(step, t2-t1))


	step = 'Drawing Bounding Boxes'
	t1 = time.time()
	print(step)
	some_random_images = random_number_of_images(IMG_FOLDER, 5)
	for idx, img in enumerate(some_random_images):
		print(img)
		boxy_box = gget_bbox_coords(img, BOUNDING_BOX_FILE, method)
		mod_img = make_bbox_image(img, boxy_box)
		# We can't save these files as JPEGs because of the alpha
		# channel required to draw the bounding box
		# If pngs look bad on the website..maybe try svg?
		mod_img.save(f'foo_box_{idx+1}.png')
	t2 = time.time()
	print('{} took {:2f} seconds'.format(step, t2-t1))






	'''
	Just creates "web_app_AB_pairs.txt"
	to help us scaffold out the application
	'''
	# with open('web_app_AB_pairs.txt','w') as f:
	# 	for mdl in MODELS:
	# 		for pr in range(N_PAIRS):
	# 			images = random_image_pair(IMG_FOLDER,2)
	# 			file_line = f'{mdl}\t{images[0]}\t{images[1]}\n'
	# 			f.write(file_line)



	# Populating a directory with random pictures meant to represent pairs
	# DEPRECATED

	# all_pair_dirs = []
	# create_directories('models', 'static')
	# model_dirs = [f'CNN{i}' for i in range(1,4)]
	# create_directories(model_dirs, 'static/models')
	# for mdl_dir in model_dirs:
	# 	create_directories('pairs', f'static/models/{mdl_dir}')
	# 	pair_dirs = [f'pair{i}' for i in range(1,11)]
	# 	for pr_dir in pair_dirs:
	# 		create_directories(pr_dir, f'static/models/{mdl_dir}/pairs')
	# 		all_pair_dirs.append((mdl_dir, pr_dir))

	# sampled_pics = np.random.choice(os.listdir(IMG_FOLDER), size = 60, replace = False)
	# odd_pics = sampled_pics[1::2]
	# even_pics = sampled_pics[::2]

	# for i, pair_dir in enumerate(all_pair_dirs):
	# 	dest_dir = f'static/models/{pair_dir[0]}/pairs/{pair_dir[1]}'
	# 	odd_copy = os.path.join(IMG_FOLDER, odd_pics[i])
	# 	even_copy = os.path.join(IMG_FOLDER, even_pics[i])
	# 	for j,f_to_copy in enumerate([odd_copy, even_copy]):
	# 		dest_file = os.path.join(dest_dir, f'img{j+1}.jpg')
	# 		shutil.copyfile(f_to_copy, dest_file)

	
