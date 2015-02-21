# coding: utf-8

__author__ = 'Junki Ishida'


class NotExistType:
    def __str__(self):
        return 'NotExist'

    def __repr__(self):
        return 'NotExist'


NotExist = NotExistType()
del NotExistType


class Entity(dict):
    def __setattr__(self, key, value):
        self[key] = value

    def __getattribute__(self, item):
        if item in self:
            return self[item]
        return dict.__getattribute__(self, item)

    def __delattr__(self, item):
        del self[item]

    def __repr__(self, *args, **kwargs):
        return 'Entity({0})'.format(dict.__repr__(self, *args, **kwargs))


__all__ = ['NotExist', 'Entity', ]