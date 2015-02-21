# coding: utf-8

__author__ = 'Junki Ishida'

import unittest, pytz

from decimal import Decimal
from datetime import datetime
from mbserializer.tests import models
from mbserializer import Serializer, register_xmlnsmap


class Object(object):
    pass


class ConvertTestCase(unittest.TestCase):
    def setUp(self):
        child = Object()
        child.int_text = -50000
        child.str_elem = 'test_str!"#$$%&\'()=~~|`{+*}<>?_-^\\@[;:],./'
        child.int_elem = 50
        child.float_elem = 1.1
        child.decimal_elem = Decimal('53.53')
        child.bool_elem = True
        child.datetime_elem = datetime(2015, 1, 5, 8, 30, tzinfo=pytz.timezone('Asia/Tokyo'))

        nechild = Object()
        nechild.str_text = '-50000'
        nechild.str_attr = 'test_str'
        nechild.int_attr = 50
        nechild.float_attr = 1.1
        nechild.decimal_attr = Decimal('53.53')
        nechild.bool_attr = False
        nechild.datetime_attr = datetime(2015, 1, 5, 8, 30, tzinfo=pytz.utc)

        nested_parent = Object()
        nested_parent.str_list = (
            'hoge',
            'fuga',
            '!"#$$%&\'()=~~|`{+*}<>?_-^\\@[;:],./',
        )
        nested_parent.int_list = (
            153,
            55987651,
            -89465662
        )
        nested_parent.float_list = (
            165464.26544,
            15,
            -597.56
        )
        nested_parent.child = child
        nested_parent.nechildren = (
            nechild,
            nechild,
        )

        parent = Object()
        parent.decimal_list = (
            Decimal('3.5'),
            Decimal('444444.5555555555'),
            Decimal('5'),
        )
        parent.bool_list = (
            True,
            False,
            True,
        )
        parent.datetime_list = (
            datetime(1900, 1, 1, tzinfo=pytz.utc),
            datetime(1935, 2, 5, 17, 49, 50, 999, tzinfo=pytz.timezone('Asia/Tokyo')),
            datetime(9999, 12, 31, 23, 59, 59, 999, tzinfo=pytz.utc),
        )
        parent.childen = (
            child,
            child,
        )
        parent.nechildren = (
            nechild,
            nechild,
        )

        self.parent = parent
        self.nested_parent = nested_parent

        xmlnsmap = {
            models.Child.__xmlns__: 'c',
            models.NoElementChild.__xmlns__: 'nec',
            models.Parent.__xmlns__: 'p',
            models.NestedParent.__xmlns__: 'np',
        }
        register_xmlnsmap(xmlnsmap)

    def test_001_parent_xml(self):
        serializer = Serializer(models.Parent)
        text = serializer.dumps(self.parent, data_type='xml', pretty_print=True)
        print(text)
        obj = serializer.loads(text, data_type='xml')

    def test_002_nested_parent_xml(self):
        serializer = Serializer(models.NestedParent)
        text = serializer.dumps(self.nested_parent, data_type='xml', pretty_print=True)
        print(text)
        obj = serializer.loads(text, data_type='xml')

    def test_003_parent_json(self):
        serializer = Serializer(models.Parent)
        text = serializer.dumps(self.parent, data_type='json', indent=2)
        print(text)
        obj = serializer.loads(text, data_type='json')

    def test_004_nested_parent_json(self):
        serializer = Serializer(models.NestedParent)
        text = serializer.dumps(self.nested_parent, data_type='json', indent=2)
        print(text)
        obj = serializer.loads(text, data_type='json')

    def test_005_parent_yaml(self):
        serializer = Serializer(models.Parent)
        text = serializer.dumps(self.parent, data_type='yaml', indent=2)
        print(text)
        obj = serializer.loads(text, data_type='yaml')

    def test_006_nested_parent_yaml(self):
        serializer = Serializer(models.NestedParent)
        text = serializer.dumps(self.nested_parent, data_type='yaml', indent=2)
        print(text)
        obj = serializer.loads(text, data_type='yaml')