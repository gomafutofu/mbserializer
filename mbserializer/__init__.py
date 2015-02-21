__author__ = 'Junki Ishida'

from .declarations import NotExist, Entity
from .models import Model, ListModel
from .serializer import Serializer
from ._xml import register_xmlnsmap


def __loaded():
    from .models import ModelTypeBase

    ModelTypeBase._ModelTypeBase__modules_loaded = True


__loaded()