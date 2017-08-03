# Building a Visual Search Algorithm

This story, like all great stories, begins with a light fixture. In particular, this light fixture:

[Chris's Light](image location)

Datascope intern, Chris, spotted this light fixture while out at lunch one day and was immediately transfixed by it's glowing, orthogonal, orbiness. In an attempt to find where he could buy his own wonderful light fixture, he took a picture with his camera and used [Google Reverse Image Search](https://images.google.com/) to find places that might have the product online. However, while Google was able to show him lots of pictures of light fixtures, it wasn't able to show him the exact product he was looking for. This is partially because Google Reverse Image Search is designed to find similar **pictures** and not similar **items**.

This lead us to start to consider what a visual **item** search might look like and how we might build one. Leveraging some articles on [style transfer](link) and [auto-encoders](link) we sort-of remembered skimming, we started to think about ways that we might leverage machine learning to build a visual product search.

Some quick googling revealed that we weren't the first people to have this idea/. Back in March of this year, [Pinterest released a beta version of a visual search application called Lens](https://blog.pinterest.com/en/and-you-get-lens-and-you-get-lens-and-you-get-lens). In June, [Wayfair introduced a visual search feature to their app and website](http://engineering.wayfair.com/2017/06/visual-search-with-deep-learning/). A few days after Chris found the light fixture of his dreams, Amazon announced a "product social discovery network" that's basically [Instagram with links directly from photos to Prime pages](https://ar

While this effectively crushed our dreams of becoming Silicon Valley billinaires, it gave us confidence that this idea was interesting and achievable using existing technologies. Because we were so excited about this idea, we decided to see how much progress we could make in building a visual search engine using publicly available data and open source code.

## So, What is this Visual Search Thing Anyway?

One of the challenges in dealing with images is that they are very high-dimensional, even a relatively low-resolution 640x480 photograph contains nearly one milion data points. This large size makes it difficult to use images as a direct input to machine learning classifiers. Fortunately, A particular type of neural network that tends to excel at working with and learning from these images is the Convolutional Neural Network, because it is good at encoding local relationships between pixel values in nearby areas of the image. I'll leave [a more detailed explanation](https://ujjwalkarn.me/2016/08/11/intuitive-explanation-convnets/) of Convolutional Neural Networks to someone [smarter than me](http://cs231n.github.io/convolutional-networks/). But, to briefly summarize, Convolutional Neural Networks use a collection of convolutional filters and pooling layers to drastically reduce the dimensionality of images while still retaining the salient features. In fact, the most successful CNNs use several convolution and pooling layers to create so-called Deep Networks, that are extremely successful at visual recognition tasks.

These Deep Convolutional Networks have a large number of hyperparameters and typically require large datasets and a lot of training in order to reach very high accuracy in visual classification. Fortunately for us, many programmers and computer vision researchers have decided to open-source not only deep-learning software libraries but also the results of pre-trained models. This allows us to leverage the results of state-of-the-art models created by dedicated research teams and then slightly modify them to to fit our own particular problem

## Building the Search Engine

While our interest in product search started with a light fixture, we ended up training our model on images of clothing from the [Deep Fashion data set](http://mmlab.ie.cuhk.edu.hk/projects/DeepFashion.html). The reason that we chose this data set is because it contains a large number of images that are annotated with category and attribute labels and provides bounding box information for the labels. This bounding box information is very helpful in creating a training set, because it allows us to separate the product from the rest of the image, which is a necessary pre-processing step. (We could probably automatically create bounding boxes using a network trained in [Object Localization](link), but that's a topic for another blog post.) The Deep Fashion data set has the advantage of providing us with examples of products in a wide variety of shape, size, color, pattern, texture, etc. Learning to train a model on the Deep Fashion data set will give us insight on how to extend this method to other items.

With the data set selected, we need to figure out how to build our visual product search algorithm. Lucky for us, the engineering team behind Pinterest's visual search product have published [a research paper outlining their approach](https://arxiv.org/pdf/1702.04680.pdf). We can use the results of their work as a blue print for creating our own visual search.

The core concept behind this method of visual search relies on using the intermediate results of a pre-trained Deep Convolutional Neural Network as a feature vector and finding products with features that are nearby to the input vector. The logic behind this is that a CNN trained at visual classification typically has two sections: a series of convolutional layers trained at extracting meaningful visual information from the input image and a series of dense layers trained at performing the classification task. Using the output of the convolutional layers as the image feature allows us to perform comparisons in a vector-space that corresponds to visual attributes as opposed to semantic attributes (i.e. the output of the classification layers). 

For this task, we decided to use the [VGG-16](http://www.robots.ox.ac.uk/~vgg/research/very_deep/) network because of its strong performance at visual classification without having to use networks with more complicated structures such as [Inception](https://github.com/google/inception) or [ResNet](https://github.com/KaimingHe/deep-residual-networks)

![Sketch of layers with notes]()

Getting started with this task is almost comically easy thanks to the high-level neural network library [Keras](https://keras.io/). We can directly import the VGG-16 architecture and download the weights from a pre-trained model in one simple step.

```python
from keras.applications import VGG16

model = VGG16(weights='imagenet')
```

Then, we can create a model that gives us just the output of the first fully connected layer and start producing feature vectors

```python
from keras.applications import imagenet_utils
from keras.preprocessing.image import img_to_array
from keras.preprocessing.image import load_img
from keras.models import Model


feature_model = Model(inputs=model.input,outputs=model.get_layer('fc1').output)

inputShape = (224, 224)
preprocess = imagenet_utils.preprocess_input

file = 'path/to/image/file.jpg'
image = load_img(file,target_size=inputShape)
image = img_to_array(image)
image = np.expand_dims(image,axis=0)
image = preprocess(image)
    
feature = feature_model.predict(image)
```

Using the pre-trained weights from VGG-16 gives us pretty good results, but we can improve our results by re-training the model on the DeepFashion dataset. The pre-trained model we started with is trained on the [ImageNet challenge](http://www.image-net.org/challenges/LSVRC/), which tasks the network with classifying images into 1,000 categories ranging from firetruck to airplane to one of 120 different breeds of dog. ([seriously](https://arxiv.org/pdf/1409.0575.pdf)) However, for our task, we want to look at small differences between items that fall into the same category. To VGG-16, all 80,000 images of a dress might look the same since they fall in the same category, so we need to train our network to learn the differences.

Fortunately, we can re-train our network on our new data set while still leveraging the power of pre-trained networks through a technique known as [transfer learning](http://cs231n.github.io/transfer-learning/). This means that we take a pre-trained network like VGG-16 and re-use the weights in the convolutional layers, but learn completely new weights (and architectures) for the dense classification layers at the end.