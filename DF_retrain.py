import pandas as pd
import numpy as np
import PIL

from keras.applications import VGG16,imagenet_utils
from keras.preprocessing.image import img_to_array
from keras.preprocessing.image import load_img
from keras.models import Model
from keras.layers import Dense
from keras import callbacks
from keras import metrics

import pickle
import time
import argparse

inputShape = (224, 224)
preprocess = imagenet_utils.preprocess_input

def preprocess_DF(bbox):
    image = crop_resize_DF(bbox)
    image = img_to_array(image)
    image = np.expand_dims(image,axis=0)
    
    return preprocess(image)

def crop_resize_DF(bbox):
    img = PIL.Image.open('./Data/DeepFashion/'+bbox['image_name'])
    lx = bbox['x_1']
    ly = bbox['y_1']
    ux = bbox['x_2']
    uy = bbox['y_2']
    
    img = img.crop((lx,ly,ux,uy))
    img = img.resize(inputShape, PIL.Image.ANTIALIAS)
    return img

def generator(df, batch_size):
    while True:
        subset = np.random.randint(df.shape[0],size=batch_size)
        proc_imgs = []
        for i in range(batch_size):
            proc_imgs.append(np.squeeze(preprocess_DF(df.iloc[i])))
    
        attr = (df.iloc[subset,6:].values>0)
        yield np.array(proc_imgs), attr


def main(batch_size=64,steps_per_epoch=10,epochs=1,save_file=None):
	df = pd.read_table('Data/DeepFashion/list_attr_img.txt',skiprows=1,sep='\s+',header=None)
	bbox = pd.read_table('Data/DeepFashion/list_bbox.txt',sep='\s+')
	joined = bbox.join(df,lsuffix='image_name',rsuffix='0')

	attr = (joined.iloc[:,6:].values>0)
	class_weights = 1/(np.mean(attr,axis=0)*1000+1e-8)

	base_model = VGG16(weights='imagenet')
	x = base_model.get_layer('predictions').input
	predictions = Dense(1000, activation='sigmoid',name='predictions')(x)

	new_model = Model(inputs=base_model.input, outputs=predictions)
	new_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=[metrics.top_k_categorical_accuracy])

	tbCB = callbacks.TensorBoard(log_dir="logs/{}".format(time.time()), histogram_freq=0, write_graph=False, write_images=False)
	checkpointCB = callbacks.ModelCheckpoint("checkpoints/{}".format(time.time()))

	new_model.fit_generator(generator(joined,batch_size),steps_per_epoch=steps_per_epoch,epochs=epochs
							,verbose=1,callbacks=[tbCB,checkpointCB])
	if save_file:
		new_model.save_weights(save_file)


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--batch_size', action="store", dest='batch_size',default=64)
	parser.add_argument('--steps_per_epoch', action="store", dest="steps_per_epoch",type=int,default=100)
	parser.add_argument('--epochs', action="store", dest="epochs", type=int,default=1)
	parser.add_argument('--save_file', action="store", dest="save_file", default=None)
	print(vars(parser.parse_args()))
	main(**vars(parser.parse_args())) 