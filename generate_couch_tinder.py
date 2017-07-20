import numpy as np
import os
import shutil

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

def random_image_pair(base_dir):
	'''
	Selects two images from a random subdirectory and returns
	a list of two paths.  These paths are assumed to be
	appended onto 'DeepFashion/img' and are going to be
	in the form of SUBDIR_NAME/IMG_NAME.jpg

	Used to create "web_app_AB_pairs.txt", something that
	will likely be supplanted by a file that Nat provides
	'''
	random_subdir = np.random.choice(os.listdir(base_dir),1).item()
	path_to_subdir = os.path.join(base_dir, random_subdir)
	img_paths = []
	for v in np.random.choice(os.listdir(path_to_subdir), 2, replace = False):
		full_path = os.path.join(random_subdir,v)
		img_paths.append(full_path)
	return img_paths


if __name__ =='__main__':
	
	IMG_FOLDER = 'Data/DeepFashion/img'
	MODELS = ['MD1', 'MD2', 'MD3']
	N_PAIRS = 50

	'''
	Just creates "web_app_AB_pairs.txt"
	to help us scaffold out the application
	'''
	with open('web_app_AB_pairs.txt','w') as f:
		for mdl in MODELS:
			for pr in range(N_PAIRS):
				images = random_image_pair(IMG_FOLDER)
				file_line = f'{mdl}\t{images[0]}\t{images[1]}\n'
				f.write(file_line)



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

	
