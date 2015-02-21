# coding: utf-8

__author__ = 'Junki Ishida'

from . import utils
from .declarations import NotExist, Entity
from .exceptions import FormatError, ParseError
from ._compat import iteritems, str_types, raise_with_inner, PY2, PY3

import re

try:
    from lxml import etree

    lxml_loaded = True
except ImportError:
    lxml_loaded = False

try:
    import defusedxml.ElementTree as ElementTree
    from xml.etree.ElementTree import ParseError as XMLParseError

    defusedxml_loaded = True
except ImportError as e:
    defusedxml_loaded = False

if PY2:
    RE_XML_DECLARATION = re.compile("""
^<\?xml
[ \\t\\r\\n]version[ \\t\\r\\n]?=[ \\t\\r\\n]?("1\.[0-9]+"|'1\.[0-9]+')
[ \\t\\r\\n]encoding[ \\t\\r\\n]?=[ \\t\\r\\n]?("([a-zA-Z][a-zA-Z0-9._\-]*)"|'([a-zA-Z][a-zA-Z0-9._\-]*)')
([ \\t\\r\\n]standalone[ \\t\\r\\n]?=[ \\t\\r\\n]?("(yes|no)"|'(yes|no)'))?
[ \\t\\r\\n]?\?>""", re.VERBOSE)

__default_xmlnsmap = {
    'http://www.w3.org/XML/1998/namespace': 'xml',
    'http://www.w3.org/1999/xhtml': 'html',
    'http://www.w3.org/1999/02/22-rdf-syntax-ns#': 'rdf',
    'http://schemas.xmlsoap.org/wsdl/': 'wsdl',
    'http://www.w3.org/2001/XMLSchema': 'xs',
    'http://www.w3.org/2001/XMLSchema-instance': 'xsi',
    'http://purl.org/dc/elements/1.1/': 'dc',
}

_xmlnsmap = __default_xmlnsmap.copy()


def register_xmlnsmap(xmlnsmap):
    _xmlnsmap.clear()
    _xmlnsmap.update(__default_xmlnsmap)
    _xmlnsmap.update(xmlnsmap)


def _build_element(model_class, data_type, data, root, xmlns):
    isdict = isinstance(data, dict)
    for k, f in iteritems(model_class._fields):
        if not utils.haskey(data, k, isdict):
            if f._ignorable:
                continue
            raise FormatError()
        src = utils.getvalue(data, k, isdict)
        if f._ignorable and src is NotExist:
            continue
        if f._istext:
            root.text = f._dump(src, data_type)
        elif f._ismember:
            key = f.get_key(k)
            if f._isattr:
                if f.xmlns:
                    key = utils.gettag(key, f.xmlns)
                root.attrib[key] = f._dump(src, data_type)
            else:
                hasniltag = f._nullable and src is None
                if f._islist:
                    if f.nested:
                        fxmlns = utils.getxmlns(f.nested_xmlns, xmlns)
                        tag = utils.gettag(key, fxmlns)
                        listtoot = etree.SubElement(root, tag)
                        if hasniltag:
                            utils.setnil(listtoot)
                            continue
                    else:
                        listtoot = root
                    exmlns = utils.getxmlns(f.xmlns, xmlns)
                    for v in src or ():
                        tag = utils.gettag(f.tag, exmlns)
                        element = etree.SubElement(listtoot, tag)
                        if f._islistdelegate:
                            _build_element(f.model_class, data_type, v, element, exmlns)
                        else:
                            element.text = f._dump(v, data_type)
                else:
                    fxmlns = utils.getxmlns(f.xmlns, xmlns)
                    tag = utils.gettag(key, fxmlns)
                    element = etree.SubElement(root, tag)
                    if hasniltag:
                        utils.setnil(element)
                    else:
                        if f._isdelegate:
                            _build_element(f.model_class, data_type, src, element, fxmlns)
                        else:
                            element.text = f._dump(src, data_type)


def dump_xml_bytes(model_class, data_type, data, **options):
    xmlns = model_class.__xmlns__
    tag = utils.gettag(model_class.__tag__, xmlns)
    nsmap = utils.getnsmap((model_class.__model__ if model_class._islist else model_class)
                           ._getxmlnsset(), _xmlnsmap, xmlns)
    root = etree.Element(tag, nsmap=nsmap)
    if model_class._islist:
        elem_xmlns = model_class.__model__.__xmlns__
        tag = utils.gettag(model_class.__model__.__tag__, elem_xmlns)
        for d in data:
            subroot = etree.SubElement(root, tag)
            _build_element(model_class, data_type, d, subroot, elem_xmlns)
    else:
        _build_element(model_class, data_type, data, root, xmlns)
    xml_declaration = options.get('xml_declaration', True)
    encoding = options.get('encoding', 'utf-8')
    pretty_print = options.get('pretty_print', False)
    return etree.tostring(root, xml_declaration=xml_declaration, encoding=encoding, pretty_print=pretty_print)


def dump_xml_str(model_class, data_type, data, **options):
    result = dump_xml_bytes(model_class, data_type, data, **options)
    if PY3:
        encoding = options.get('encoding', 'utf-8')
        return result.decode(encoding)
    return result


def _parse_xml(model_class, data_type, data, xmlns):
    entity = Entity()
    if isinstance(data, str_types):
        data = ElementTree.fromstring(data)
    tag = utils.gettag(model_class.__tag__, xmlns)
    if data.tag != tag:
        raise FormatError()
    for k, f in iteritems(model_class._fields):
        key = f.get_key(k)
        if f._istext:
            value = data.text
        elif f._ismember:
            if f._isattr:
                key = utils.gettag(key, f.xmlns)
                if not key in data.keys():
                    raise FormatError()
                value = data.attrib[key]
            else:
                if f._islist and not f.nested:
                    fxmlns = utils.getxmlns(f.xmlns, xmlns)
                    tag = utils.gettag(f.tag, fxmlns)
                    value = []
                    for e in data:
                        if e.tag == tag:
                            v = _parse_xml(f.model_class, data_type, e, fxmlns) \
                                if f._islistdelegate else f._parse(e.text, data_type)
                            value.append(v)
                else:
                    fxmlns = utils.getxmlns(f.nested_xmlns if f._islist else f.xmlns, xmlns)
                    tag = utils.gettag(key, fxmlns)
                    element = None
                    for e in data:
                        if e.tag == tag:
                            element = e
                            break
                    if element is None:
                        if f._ignorable:
                            entity[k] = NotExist
                            continue
                        raise FormatError()
                    if f._nullable and utils.isnil(element):
                        value = None
                    else:
                        if f._islist:
                            value = []
                            exmlns = utils.getxmlns(f.xmlns, xmlns)
                            tag = utils.gettag(f.tag, exmlns)
                            for e in element:
                                if e.tag == tag:
                                    v = _parse_xml(f.model_class, data_type, e, exmlns) \
                                        if f._islistdelegate else f._parse(e.text, data_type)
                                    value.append(v)
                                else:
                                    raise FormatError()
                        else:
                            value = _parse_xml(f.model_class, data_type, element, fxmlns) \
                                if f._isdelegate else f._parse(element.text, data_type)
        entity[k] = value
    return entity


def load_xml(model_class, data_type, data, **options):
    try:
        if isinstance(data, str_types):
            if PY2 and isinstance(data, unicode):
                encoding = 'utf-8'
                match = RE_XML_DECLARATION.match(data)
                if match:
                    g3 = match.group(3)
                    g4 = match.group(4)
                    encoding = match.group(3) or match.group(4)
                data = data.encode(encoding)
            data = ElementTree.fromstring(data)
        else:
            data = ElementTree.parse(data).getroot()
    except XMLParseError as e:
        raise_with_inner(ParseError, e)
    xmlns = model_class.__xmlns__
    if model_class._islist:
        tag = utils.gettag(model_class.__tag__, xmlns)
        elem_xmlns = model_class.__model__.__xmlns__
        if data.tag != tag:
            raise FormatError()
        result = []
        for e in data:
            entity = _parse_xml(model_class, data_type, e, elem_xmlns)
            result.append(entity)
        return result
    else:
        return _parse_xml(model_class, data_type, data, xmlns)