import imghdr


def is_image(file_path: str) -> bool:
    return imghdr.what(file_path) is not None
