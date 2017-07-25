# Potential Blog Post Outline
### (or, Ross Takes A Stab at Main Points We May Want to Hit)

## Motivation

* Out at lunch one day, Chris sees a light fixture that speaks to him. He likes it so much that he takes a photo of it

* "I wish there were an app that allowed me to find this thing that I saw."  This is an example of a user story that motivates the need for "visual search," a subset of the burgeoning field of computer vision.

* Turns out we aren't the only ones to have this idea. 
	* Back in March of this year, [Pinterest released a beta version of a visual search application called Lens](https://blog.pinterest.com/en/and-you-get-lens-and-you-get-lens-and-you-get-lens).
	* A few days after Chris found the light fixture of his dreams, Amazon announced a "product social discovery network" that's basically [Instagram with links directly from photos to Prime pages](https://arstechnica.com/business/2017/07/amazon-spark-is-a-product-discovery-social-network-that-looks-like-instagram/) 

* While this effectively crushed our desires of moving to the Bay Area and tracking down angel investors to make Chris's application a reality, it didn't stop us from seeing how much progress we could make in building a visual search engine using publicly available data and open source code

## So, What is this Visual Search Thing Anyway?

* At its highest level, image processing involves taking photos and converting them into very long arrays where each value represents the colors present in a particular pixel.  So a 100 X 100 pixel image encoded in the RGB colorway can be represented as a vector that has a dimension of 1 X 30,000.

* A particular type of neural network that tends to excel at working with and learning from these images is the Convolutional Neural Network, because it is good at encoding local relationships between pixel values in nearby areas of the image. We could potentially go into more detail on this, or we could refer people to a [much more detailed description like this one](https://ujjwalkarn.me/2016/08/11/intuitive-explanation-convnets/) 

* We could very easily just take a photo of the drawing on the board by the internet cabinet, and explain that at its outset, we're working with the very end layers, after the convolution has already happened. What our "image search" really is is just a comparison across multiple images that have been transformed into these long vectors

* We've just scratched the surface of something that veritable armies of researchers have dedicated their blood, sweat, and tears to over the years. These CNNs are highly complex systems that
	* Require massive amounts of data to yield viable results,
	* Require massive computing power to push through said data, and
	* Are controlled by _a lot_ of input parameters (think knobs on a big dashboard) that can be calibrated in myriad ways

* This complexity partially explains why image recognition is still an active area of research.  Reference ImageNet, annual competition in which research teams from academia and industry alike compete on a shared data set to try and make progress in various computer vision subchallenges.

* Luckily, one of the beauties of the open-source ethos is that it allows us to stand on the shoulders of giants. Introduce VGG16 architecture, something that has done very well in the object detection portion of ImageNet in the past.  Now mention that this "state of the art" model comes preloaded in the excellent keras deep learning library.

* This significantly lowers the barriers to entry for anyone hoping to work with and learn about image recognition. To get started with them, we don't need to have GPU machines churn through millions of images. Instead, we can take networks that are already calibrated, use that configuration as a starting point, and tweak or customize them as your own situation dictates.

* Optional: If we wanted to link people to another very good example of what "tweaking and customizing" looks like, we could potentially show them the [NotHotdog Medium post](https://hackernoon.com/how-hbos-silicon-valley-built-not-hotdog-with-mobile-tensorflow-keras-react-native-ef03260747f3)...but that might be counterproductive at this point. Possibly we could chuck this in toward the end as "further reading"


## Adventures in Data

* Now that we have a model to use, the next thing we needed was a bunch of images to feed into our network and make comparisons across. Just as there are state-of-the-art models out there in the public domain, there are a number of open (or quasi-open) data sets released by the computer vision community. 

* The first place we looked was [OpenImages](https://research.googleblog.com/2016/09/introducing-open-images-dataset.html), a data set curated by Google that includes 9 million images across 6,000 categories. We thought this would give us a good number of lights to learn from  

* Perhaps show one pair of lights that VGG16 found to be similar; after we passed these lights part of the way through the VGG16 net to convert them into vectors, these vectors were found to be nearest neighbors. 

* Then, show what happens if you took all of these light-photos-turned-vectors, collapsed them into two dimensions, and plotted them on the same graph. You would get a map that looks something like ![this T-SNE plot](output/light_tsne.png) 

* There are definitely instances where similar lights end up in similar regions, but you may also notice that the nighttime images got placed with the nighttime images and the daytime images got placed with daytime ones.  The network is doing a good job at grouping similar images together, but there's a difference between **similar images** and **similar lights in those images.**

* The inability to control for a high degree of variability in things like lighting, quality, focus, and content (there may be a light in this image, but there are also trees, clouds, etc) is one of the biggest challenges to overcome in dealing with "images in the wild"

* Two main reasons (feel free to edit/amend these) why we moved from looking at photos of lights to photos from the [Deep Fashion data set](http://mmlab.ie.cuhk.edu.hk/projects/DeepFashion.html)
	1. Fashion photos are often taken in studios against neutral backgrounds with minimal other details to distract from the clothing at hand. Our hope is that if there are generally fewer of those "background factors" in the images we're dealing with, then the similarities our network is measuring will have more to do with the object of interest (i.e. clothes)
	2. The curators of this data included bounding box information with every photo. What this allows us to do is identify particular sub-regions of an image that we might want to focus on and exclude everything else. That way, we can be reasonably sure that when we pass in two images of, say, scarves, the network will learn to recognize visual features of the scarves and not about other pieces of clothing the models may be wearing
	3.(Optionally, show one of the deep fashion photos with and without bounding boxes to make it clear how these things help)


## NAT WORKS JEDI MAGIC AND SOLVES FASHION ONCE AND FOR ALL, THERE, DONE!

* Leaving this section blank-ish, because I don't want to pretend to be familiar enough with the steps that occurred. At the same time, my *vague sense of what went on is...* 
	1. Started by just looking at how the fc6, fc7, and fc8 features of the standard VGG16 network did with the fashion data. Could this network apply ImageNet labels to the DeepFashion Data
	2. Began to retrain the network to the predict the categories actually in the DeepFashion Data.  This is where an attempt is made to move beyond the exact settings calibrated by the VGG16 and see if we can customize the network at all to this specific application
	3. Which models do the best?  How are we measuring "best?" (precision in labeling a certain number of categories?) 

## What does success look like?

* Having deep neural networks do a bunch of math and spit out distance metrics or make classifications is all well and good for machine learning contests.

* There isn't a direct relationship between these quantitative measures of how well a neural network is doing its job and how well it actually *meets a human need.* In this case, does our visual search actually put images together in ways that people enjoy?

* In order to get a better sense at how our visual search is working from a human-centered perspective, we built a little website called [INSERT BETTER WEB APPLICATION NAME HERE] to put these different models head to head and asked several esteemed Datascope colleagues to vote on these in a blind AB testing fashion

* TKTK let anywhere between 3 and 5 datascopers vote on these and summarize the results on the leaderboard

* You can go to this website and play with it too!

## A nice pretty conclusion that ties everything together

* It's relatively easy to get started with state of the art image recognition technologies

* We were lucky enough to be able to work with highly curated data sets with a high degree of metadata. Any one starting to build an application from scratch may not be so lucky and would need _to spend a significant amount of time preprocessing the data (perhaps even involving an entirely separate neural network to do so)._

* How easy is it to retrain neural networks from a general case to a more specific one?