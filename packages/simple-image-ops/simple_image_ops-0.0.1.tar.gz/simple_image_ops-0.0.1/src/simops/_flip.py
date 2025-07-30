from typing import Any

from ._utils import opencv_available, pillow_available, raise_missing_image_library

FLIP_LEFT_RIGHT = "left-right"
FLIP_TOP_BOTTOM = "top-bottom"
FLIPS = [
    FLIP_LEFT_RIGHT,
    FLIP_TOP_BOTTOM,
]

PILLOW_USE_TRANSPOSE = None


def flip(img: Any, flip: str) -> Any:
    """
    For flipping the image.

    :param img: the image to rotate
    :param flip: left-right or top-bottom
    :type flip: str
    :return: the flipped image
    """
    if flip not in FLIPS:
        raise Exception("Unsupported flip: %s" % flip)

    if opencv_available():
        import cv2
        if flip == FLIP_LEFT_RIGHT:
            return cv2.flip(img, 1)
        elif flip == FLIP_TOP_BOTTOM:
            return cv2.flip(img, 0)

    if pillow_available():
        from PIL import Image
        global PILLOW_USE_TRANSPOSE
        if PILLOW_USE_TRANSPOSE is None:
            try:
                import PIL.Image.Transpose
                PILLOW_USE_TRANSPOSE = True
            except:
                PILLOW_USE_TRANSPOSE = False
        if PILLOW_USE_TRANSPOSE:
            if flip == FLIP_LEFT_RIGHT:
                return img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            elif flip == FLIP_TOP_BOTTOM:
                return img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        else:
            if flip == FLIP_LEFT_RIGHT:
                return img.transpose(Image.FLIP_LEFT_RIGHT)
            elif flip == FLIP_TOP_BOTTOM:
                return img.transpose(Image.FLIP_LEFT_RIGHT)

    raise_missing_image_library()
