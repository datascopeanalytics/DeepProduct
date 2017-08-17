import pandas as pd
import numpy as np
import pickle
import PIL
from PIL import ImageDraw
from keras.preprocessing.image import load_img, img_to_array, array_to_img
from keras.applications import imagenet_utils
import time

class DFModel(object):

    def __init__(self,
                 full_matrix_fn='Data/feature_matrix/fc6_full_set.p',
                 full_trained_fn='Data/Trained Models/DF-Category-FULL-retrain.h5',
                 bboxes_fn='Data/DeepFashion/list_bbox.txt',
                 cats_fn='Data/DeepFashion/list_category_img.txt'):

        with open(full_matrix_fn,'rb') as f:
            feat = pickle.load(MacOSFile(f))
        self.feature_matrix = feat > 0
        from keras.models import load_model,Model

        start = time.time()
        self.full_trained = load_model(full_trained_fn)
        self.full_fc6 = Model(inputs=self.full_trained.input,outputs=self.full_trained.get_layer('fc1').output)
        print('{:.2f} s'.format(time.time()-start))

        bbox = pd.read_table(bboxes_fn,sep='\s+')
        cat = pd.read_table(cats_fn,sep='\s+')

        self.image_df = bbox.join(cat,lsuffix='_',rsuffix='')



    def preprocess_DF(self, image, bbox):
        image = crop_resize_DF(bbox)
        image = img_to_array(image)
        image = np.expand_dims(image,axis=0)

        return imagenet_utils.preprocess_input(image)

    def preprocess_file(self, file, inputShape=(224,224)):
        image = PIL.Image.open(file).convert('RGB')
        image = image.resize(inputShape, PIL.Image.ANTIALIAS)
        image = img_to_array(image)
        image = np.expand_dims(image,axis=0)

        return imagenet_utils.preprocess_input(image)

    def crop_resize_DF(self, bbox, inputShape=(224,224)):
        img = PIL.Image.open('Data/DeepFashion/'+bbox['image_name'])
        lx = bbox['x_1']
        ly = bbox['y_1']
        ux = bbox['x_2']
        uy = bbox['y_2']

        img = img.crop((lx,ly,ux,uy))
        img = img.resize(inputShape, PIL.Image.ANTIALIAS)
        return img

    def draw_k(self, image_file, k):
        img = self.preprocess_file(image_file)
        img_feature = self.full_fc6.predict(img)>0

        print("Source Image")
        image = PIL.Image.open(image_file)
        image.thumbnail((300,300), PIL.Image.ANTIALIAS)
        print(image_file)

        dist = np.sum(np.logical_xor(img_feature,self.feature_matrix),axis=1)
        j=0
        match = np.argsort(dist)
        while dist[match[j]]<=0:
                j += 1


        print("Top Matches")
        tops = []
        for m in match[j:(j+k)]:
            print(self.image_df.iloc[m])
            tops.append(self.image_df.iloc[m].loc['image_name'])

        return tops

    def select_k(self, N,k,image_df,feature_matrix):
        img_index = np.random.randint(image_df.shape[0],size=N)

        for i in img_index:

            dist = np.sum(np.logical_xor(feature_matrix[i,:],feature_matrix),axis=1)
            j=0
            match = np.argsort(dist)
            while dist[match[j]]<=0:
                    j += 1

            print(image_df.iloc[i])

            for m in match[j:(j+k)]:
                print("distance: {}".format(dist[m]))
                print(image_df.iloc[m])


class MacOSFile(object):
    def __init__(self, f):
        self.f = f

    def __getattr__(self, item):
        return getattr(self.f, item)

    def read(self, n):
        if n >= (1 << 31):
            buffer = bytearray(n)
            pos = 0
            while pos < n:
                size = min(n - pos, 1 << 31 - 1)
                chunk = self.f.read(size)
                buffer[pos:pos + size] = chunk
                pos += size
            return buffer
        return self.f.read(n)

if __name__ == '__main__':
    print('nope')
