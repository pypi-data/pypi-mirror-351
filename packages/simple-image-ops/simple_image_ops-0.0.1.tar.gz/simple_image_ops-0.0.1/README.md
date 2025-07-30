# simple-image-ops
Python3 library for simple image operations either using OpenCV or Pillow.


## Installation

### PyPI

```bash
pip install simple_image_ops
```

### Github

```bash
pip install git+https://github.com/waikato-datamining/simple-image-ops.git
```

## API

The following I/O operations are available:

* `simops.load_file` - loads an image from disk
* `simops.load_bytes` - loads an image from a bytes structure
* `simops.save_file` - saves an image to disk
* `simops.save_bytes` - saves an images into a bytes structure

**NB:** the `save_` methods allow specifying the JPEG quality via the 
`jpeg_quality` parameter.

The following image operations are available:

* `simops.flip` - flips the image left/right or top/bottom
* `simops.resize` - resizes the image
* `simops.rotate` - rotates the image by 90/180/270 degrees counter-clockwise

These helper methods are available:

* `simops.numpy_available` - whether Numpy is available
* `simops.opencv_available` - whether OpenCV is available
* `simops.pillow_available` - whether Pillow is available


## Examples

### Resize file

The following loads the images from disk, resizes it using explicit width/height, 
and saves it back to disk:

```python
from simops import load_file, resize, save_file

img = load_file("input.jpg")
img_res = resize(img, width=800, height=600)
save_file(img_res, "output.jpg")
```

### Resize bytes

Here we load the image from bytes, resize it specifying only the width 
(therefore keeping the aspect ratio) and then turn it back into bytes
(using JPEG format):

```python
from simops import load_bytes, resize, save_bytes

data_in = ...  # obtained from somewhere
img = load_bytes(data_in)
img_res = resize(img, width=1024)
data_out = save_bytes(img_res, "JPEG")
```
