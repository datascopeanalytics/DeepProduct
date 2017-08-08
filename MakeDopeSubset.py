import os
import shutil

target_path = 'Data/DopeOrNopeImages/'

def make_target_dirs(file):
    dirname = os.path.split(file)[0]
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

def copy_sub(file):
    shutil.copy2('Data/DeepFashion/'+file,target_path+file)



with open('all_pairs.txt') as f:
    lines = f.readlines()

i = 0
for line in lines:
    imgs = line.split()[1:]
    for img in imgs:
    	i += 1
    	make_target_dirs(target_path+img)
    	copy_sub(img)
print('copied {} images to {}'.format(i,target_path))