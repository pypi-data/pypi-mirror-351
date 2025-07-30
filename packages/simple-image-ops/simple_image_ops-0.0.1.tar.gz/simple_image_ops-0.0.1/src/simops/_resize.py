from typing import Union, Any, Tuple

from ._utils import opencv_available, pillow_available, raise_missing_image_library

KEEP_ASPECT_RATIO = "keep-aspect-ratio"

INTERPOLATION_NEAREST = "nearest"
INTERPOLATION_CUBIC = "cubic"
INTERPOLATION_LINEAR = "linear"
INTERPOLATION_LANCZOS = "lanczos"
INTERPOLATIONS = [
    INTERPOLATION_NEAREST,
    INTERPOLATION_CUBIC,
    INTERPOLATION_LINEAR,
    INTERPOLATION_LANCZOS,
]


PILLOW_USE_RESAMPLING = None


def _determine_dims(img_width: int, img_height: int, width: Union[int, str], height: Union[int, str]) -> Tuple[int, int]:
    """
    Determines the actual dimensions to use from the specified width/height.

    :param img_width: the current image width
    :type img_width: int
    :param img_height: the current image height
    :type img_height: int
    :param width: the requested width, can be KEEP_ASPECT_RATIO
    :type width: str or int
    :param height: the requested height, can be KEEP_ASPECT_RATIO
    :type height: str or int
    :return: the calculated dimensions (width, height)
    :rtype: tuple
    """
    if width == KEEP_ASPECT_RATIO:
        ratio = img_width / img_height
        return int(height * ratio), height
    elif height == KEEP_ASPECT_RATIO:
        ratio = img_height / img_width
        return width, int(width * ratio)
    else:
        return width, height


def resize(img: Any, width: Union[int, str] = KEEP_ASPECT_RATIO, height: Union[int, str] = KEEP_ASPECT_RATIO,
           interpolation: str = INTERPOLATION_CUBIC) -> Any:
    """
    Resizes the image object and returns the new image.

    :param img: the image object to resize
    :param width: the width to use, or KEEP_ASPECT_RATIO to determine from new height
    :type width: int or str
    :param height: the width to use, or KEEP_ASPECT_RATIO to determine from new height
    :type height: int or str
    :param interpolation: the type of interpolation to use
    :type interpolation: str
    :return: the resize image
    """
    # nothing to do?
    if (width == KEEP_ASPECT_RATIO) and (height == KEEP_ASPECT_RATIO):
        return img

    if opencv_available():
        import cv2
        if interpolation == INTERPOLATION_LINEAR:
            _interpolation = cv2.INTER_LINEAR
        elif interpolation == INTERPOLATION_NEAREST:
            _interpolation = cv2.INTER_NEAREST
        elif interpolation == INTERPOLATION_CUBIC:
            _interpolation = cv2.INTER_CUBIC
        elif interpolation == INTERPOLATION_LANCZOS:
            _interpolation = cv2.INTER_LANCZOS4
        else:
            raise Exception("Unhandled interpolation: %s" % interpolation)
        img_height, img_width = img.shape[:2]
        new_width, new_height = _determine_dims(img_width, img_height, width, height)
        return cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)

    if pillow_available():
        from PIL import Image
        global PILLOW_USE_RESAMPLING
        if PILLOW_USE_RESAMPLING is None:
            try:
                import PIL.Image.Resampling
                PILLOW_USE_RESAMPLING = True
            except:
                PILLOW_USE_RESAMPLING = False
        if PILLOW_USE_RESAMPLING:
            if interpolation == INTERPOLATION_LINEAR:
                _interpolation = Image.Resampling.BILINEAR
            elif interpolation == INTERPOLATION_NEAREST:
                _interpolation = Image.Resampling.NEAREST
            elif interpolation == INTERPOLATION_CUBIC:
                _interpolation = Image.Resampling.BICUBIC
            elif interpolation == INTERPOLATION_LANCZOS:
                _interpolation = Image.Resampling.LANCZOS
            else:
                raise Exception("Unhandled interpolation: %s" % interpolation)
        else:
            if interpolation == INTERPOLATION_LINEAR:
                _interpolation = Image.BILINEAR
            elif interpolation == INTERPOLATION_NEAREST:
                _interpolation = Image.NEAREST
            elif interpolation == INTERPOLATION_CUBIC:
                _interpolation = Image.BICUBIC
            elif interpolation == INTERPOLATION_LANCZOS:
                _interpolation = Image.LANCZOS
            else:
                raise Exception("Unhandled interpolation: %s" % interpolation)
        img_width, img_height = img.size
        new_width, new_height = _determine_dims(img_width, img_height, width, height)
        return img.resize((new_width, new_height), _interpolation)

    raise_missing_image_library()
