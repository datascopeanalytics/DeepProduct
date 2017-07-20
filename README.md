# DeepProduct
![i love lamp](http://24.media.tumblr.com/04454579e797f43f3e563d6b828b8a08/tumblr_mnmm11IeVO1rmyah0o1_250.gif )



To get started, make sure you're using Python 3 and then create an environment using something like

```
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```

this will install Tensorflow and Keras (amongst other things), so it may take slightly longer than usual.

Link to the image data in the dropbox:
```
ln -s ~/Dropbox\ \(Datascope\ Analytics\)/DeepProduct/Data/ Data
```

With the environment active, view the notebook by launching the jupyter server

```jupyter notebook```

The code will need to download several files of order ~100MB when being first run, but will cache them for future execution.

**For those working on developing the tentatively named couch_tinder application**, you should also create a symlink within the `static` directory. Please call it `to_dropbox`, otherwise your web app will be Brokeymon.

```
cd static
ln -s ~/Dropbox\ \(Datascope\ Analytics\)/DeepProduct/Data/ to_dropbox
```
