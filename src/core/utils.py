import os
from uuid import uuid4

from django.utils.deconstruct import deconstructible


@deconstructible
class PathAndRename(object):

    def __init__(self, sub_path=None, randomize=False):
        if not sub_path:
            raise ValueError('PathAndRename needs sub_path')

        self.path = sub_path
        self.randomize = randomize

    def __call__(self, instance, filename):
        if self.randomize:
            ext = filename.split('.')[-1]
            # set filename as random string
            filename = '{}.{}'.format(uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join(self.path, filename)
