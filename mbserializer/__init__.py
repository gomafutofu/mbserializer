__author__ = 'Junki Ishida'

from .declarations import NotExist, Entity
from .models import Model, ListModel
from .serializer import Serializer
from ._xml import xmlnsmap, register_xmlnsmap, unregister_xmlns, unregister_prefix


def __loaded():
    from .models import ModelTypeBase

    ModelTypeBase._ModelTypeBase__modules_loaded = True


__loaded()