import numpy as np
import os
import shutil

IMG_FOLDER = 'Data/OpenImages/Couch'


def create_directories(dirs_to_create, base_dir):
	if not isinstance(dirs_to_create, list):
		dirs_to_create = [dirs_to_create]
	for direct in dirs_to_create:
		try:
			os.makedirs(os.path.join(base_dir, direct))
		except FileExistsError as e:
			continue

# Populating a directory with pictures we believe to represent pairs
# Right now these are random...we'll cross the bridge of actually populating
# the model stuff when we get there

if __name__ =='__main__':
	all_pair_dirs = []
	create_directories('models', 'static')
	model_dirs = [f'CNN{i}' for i in range(1,4)]
	create_directories(model_dirs, 'static/models')
	for mdl_dir in model_dirs:
		create_directories('pairs', f'static/models/{mdl_dir}')
		pair_dirs = [f'pair{i}' for i in range(1,11)]
		for pr_dir in pair_dirs:
			create_directories(pr_dir, f'static/models/{mdl_dir}/pairs')
			all_pair_dirs.append((mdl_dir, pr_dir))

	sampled_pics = np.random.choice(os.listdir(IMG_FOLDER), size = 60, replace = False)
	odd_pics = sampled_pics[1::2]
	even_pics = sampled_pics[::2]

	for i, pair_dir in enumerate(all_pair_dirs):
		dest_dir = f'static/models/{pair_dir[0]}/pairs/{pair_dir[1]}'
		odd_copy = os.path.join(IMG_FOLDER, odd_pics[i])
		even_copy = os.path.join(IMG_FOLDER, even_pics[i])
		for j,f_to_copy in enumerate([odd_copy, even_copy]):
			dest_file = os.path.join(dest_dir, f'img{j+1}.jpg')
			shutil.copyfile(f_to_copy, dest_file)

	
