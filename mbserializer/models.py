# coding: utf-8

__author__ = 'Junki Ishida'

from . import utils
from ._compat import with_metaclass, OrderedDict


class ModelTypeBase(type):
    __modules_loaded = False

    def __new__(cls, name, bases, attrs):
        __model_class = super(ModelTypeBase, cls).__new__(cls, name, bases, attrs)
        __model_class._islist = False
        if __model_class.__tag__ is None:
            __model_class.__tag__ = name
        if cls.__modules_loaded:
            from . import Serializer

            __model_class._serializer = Serializer(__model_class)
        return __model_class


class ModelType(ModelTypeBase):
    def __new__(cls, name, bases, attrs):
        def _getxmlnsset(cls):
            if not hasattr(cls, '_MLModelType__xmlnsset'):
                xmlnsset = set()
                if cls.__xmlns__ is not None:
                    xmlnsset.add(cls.__xmlns__)
                for f in cls._fields.values():
                    if f._ismember:
                        if f.xmlns is not None:
                            xmlnsset.add(f.xmlns)
                        if f._islist and f.nested_xmlns is not None:
                            xmlnsset.add(f.nested_xmlns)
                        if f._isdelegate or f._islistdelegate:
                            xmlnsset.update(f.model_class._getxmlnsset())
                        if f._nullable:
                            xmlnsset.add('http://www.w3.org/2001/XMLSchema-instance')
                cls.__xmlnsset = xmlnsset
            return cls.__xmlnsset

        __fields = OrderedDict()
        for base in bases:
            if isinstance(base, ModelType):
                __fields.update(base._fields)
        utils._setfields(__fields, attrs)
        attrs['_fields'] = __fields
        attrs['_getxmlnsset'] = classmethod(_getxmlnsset)
        return super(ModelType, cls).__new__(cls, name, bases, attrs)


class ListModelType(ModelTypeBase):
    def __new__(cls, name, bases, attrs):
        __model_class = super(ListModelType, cls).__new__(cls, name, bases, attrs)
        if cls._ModelTypeBase__modules_loaded and __model_class.__model__ is None:
            raise ValueError()
        __model_class._islist = True
        return __model_class


class Model(with_metaclass(ModelType)):
    __xmlns__ = None
    __tag__ = None


class ListModel(with_metaclass(ListModelType)):
    __model__ = None

    __xmlns__ = None
    __tag__ = None


__all__ = ['Model', 'ListModel']