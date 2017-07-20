import codecs


def b(x):
    """ convert a py-string to-bytes
    """
    return codecs.latin_1_encode(x)[0]
