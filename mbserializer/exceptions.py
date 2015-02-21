# coding:utf-8

__author__ = 'Junki Ishida'


class FormatError(ValueError):
    def __init__(self, *args, **kwargs):
        super(FormatError, self).__init__(*args, **kwargs)
        self.inner = kwargs.get('inner')


class ParseError(ValueError):
    def __init__(self, *args, **kwargs):
        super(FormatError, self).__init__(*args, **kwargs)
        self.inner = kwargs.get('inner')
