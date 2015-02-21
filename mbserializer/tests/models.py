__author__ = 'Junki Ishida'

from mbserializer import Model
from mbserializer.fields import attribute_fields as attrs, element_fields as elems, list_fields as lists, text_fields as texts

class NoElementChild(Model):
    __tag__ = 'nechild'
    __xmlns__ = 'http://mbserializer.com/nechild'

    str_text = texts.Str()
    str_attr = attrs.Str()
    int_attr = attrs.Int()
    float_attr = attrs.Float()
    decimal_attr = attrs.Decimal()
    bool_attr = attrs.Bool()
    datetime_attr = attrs.Datetime()

class Child(Model):
    __tag__ = 'child'
    __xmlns__ = 'http://mbserializer.com/child'

    int_text = texts.Int()
    str_elem = elems.Str()
    int_elem = elems.Int()
    float_elem = elems.Float()
    decimal_elem = elems.Decimal()
    bool_elem = elems.Bool()
    datetime_elem = elems.Datetime()

class NestedParent(Model):
    __tag__ = 'nested_parent'
    __xmlns__ = 'http://mbserializer.com/nested_parent'

    str_list = lists.Str('str', nested=True)
    int_list = lists.Int('int', nested=True)
    float_list = lists.Float('float', nested=True)

    child = elems.Delegate(Child)
    nechildren = lists.Delegate(NoElementChild, nested=True)

class Parent(Model):
    __tag__ = 'parent'
    __xmlns__ = 'http://mbserializer.com/parent'

    decimal_list = lists.Decimal('decimal', nested=False)
    bool_list = lists.Bool('bool', nested=False)
    datetime_list = lists.Datetime('datetime', nested=False)

    childen = lists.Delegate(Child)
    nechildren = lists.Delegate(NoElementChild)

class Person(Model):
    __xmlns__ = 'http://mbserializer.com/person'

    name = attrs.Str('Name')
    gender = attrs.Enum(('male', 'female',), 'Gender')
    birthday = elems.Date('Birthday')

