NUMPY_AVAILABLE = None
OPENCV_AVAILABLE = None
PILLOW_AVAILABLE = None


def numpy_available() -> bool:
    """
    Returns whether the numpy library is available.

    :return: True if available
    :rtype: bool
    """

    global NUMPY_AVAILABLE
    if NUMPY_AVAILABLE is None:
        try:
            import numpy
            NUMPY_AVAILABLE = True
        except:
            NUMPY_AVAILABLE = False
    return NUMPY_AVAILABLE


def opencv_available() -> bool:
    """
    Returns whether the OpenCV library is available.

    :return: True if available
    :rtype: bool
    """

    global OPENCV_AVAILABLE
    if OPENCV_AVAILABLE is None:
        try:
            import cv2
            OPENCV_AVAILABLE = True
        except:
            OPENCV_AVAILABLE = False
    return OPENCV_AVAILABLE


def pillow_available() -> bool:
    """
    Returns whether the Pillow library is available.

    :return: True if available
    :rtype: bool
    """

    global PILLOW_AVAILABLE
    if PILLOW_AVAILABLE is None:
        try:
            from PIL import Image
            PILLOW_AVAILABLE = True
        except:
            PILLOW_AVAILABLE = False
    return PILLOW_AVAILABLE


def raise_missing_image_library():
    """
    Raises an exception if neither opencv nor pillow is available.
    """
    if not opencv_available() and not pillow_available():
        raise Exception("Neither OpenCV nor Pillow installed!")


def raise_missing_numpy_library():
    """
    Raises an exception if numpy is not is available.
    """
    if not numpy_available():
        raise Exception("Numpy is not installed!")


def raise_not_pillow_image(img):
    """
    Raises an exception that a Pillow Image was expected but got something else instead.

    :param img: the unsupported image object
    """
    raise Exception("Expected Pillow Image, but got: %s" % str(type(img)))
