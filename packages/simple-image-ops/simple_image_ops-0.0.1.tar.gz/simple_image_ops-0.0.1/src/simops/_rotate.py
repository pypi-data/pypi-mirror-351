from typing import Any

from ._utils import opencv_available, pillow_available, raise_missing_image_library

PILLOW_USE_TRANSPOSE = None


def rotate(img: Any, degrees: int) -> Any:
    """
    For rotating the image counter-clockwise.

    :param img: the image to rotate
    :param degrees: 0/90/180/270 degrees
    :type degrees: int
    :return: the rotated image
    """
    # nothing to do?
    if degrees == 0:
        return img
    # valid degrees?
    if degrees not in [90, 180, 270]:
        raise Exception("Degrees can only be: 90, 180 or 270!")

    if opencv_available():
        import cv2
        if degrees == 90:
            return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif degrees == 180:
            return cv2.rotate(img, cv2.ROTATE_180)
        else:
            return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

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
            if degrees == 90:
                return img.transpose(Image.Transpose.ROTATE_90)
            elif degrees == 180:
                return img.transpose(Image.Transpose.ROTATE_180)
            else:
                return img.transpose(Image.Transpose.ROTATE_270)
        else:
            if degrees == 90:
                return img.transpose(Image.ROTATE_90)
            elif degrees == 180:
                return img.transpose(Image.ROTATE_180)
            else:
                return img.transpose(Image.ROTATE_270)

    raise_missing_image_library()
