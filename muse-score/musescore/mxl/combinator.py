# encoding: UTF-8

"""
Parser combinator
"""

from lxml.etree import _Element as Element
from typing import Optional, List
from dataclasses import _PARAMS as DATACLASS_PARAMS_KEY
from dataclasses import dataclass
from datetime import date as pydate

COMBINATOR_CTOR = '__combinator_ctor__'
ENTITY_CTOR = '__entity_ctor__'
TAG_TRANS = {ord(c): '' for c in '-_'}


def tag_eq(lhs: str, rhs: str):
    return lhs.lower().translate(TAG_TRANS) == rhs.lower().translate(TAG_TRANS)


class XMLElement:
    @classmethod
    def match_tag(cls, tag) -> bool:
        if isinstance(tag, Element):
            tag = tag.tag
        return tag_eq(cls.__name__, tag)

    def __init__(self, doc: Element):
        children = doc.getchildren()
        for key, value in self.__annotations__.items():
            if is_combinator(value):
                setattr(self, key, value(children))
            else:
                if key in doc.attrib:
                    setattr(self, key, value(doc.attrib[key]))
                elif is_entity(value):
                    dummy = DummyXMLElement(key)
                    for child in filter(dummy.match_tag, children):
                        setattr(self, key, value(child.text.strip()))
                        break
                    else:
                        setattr(self, key, None)
                elif key in self.__dict__:
                    setattr(self, key, self.__dict__[key])
                else:
                    setattr(self, key, None)


@dataclass
class DummyXMLElement:
    name: str

    def match_tag(self, tag) -> bool:
        if isinstance(tag, Element):
            tag = tag.tag
        return tag_eq(self.name, tag)


def is_dataclass(cls):
    return DATACLASS_PARAMS_KEY in cls.__dict__


def is_combinator(cls):
    return COMBINATOR_CTOR in cls.__dict__


def is_entity(cls):
    return ENTITY_CTOR in cls.__dict__


def xml_combinator(logic_fn):
    def __combinator__(cls):
        if isinstance(cls, str):
            cls = DummyXMLElement(cls)
        elif not issubclass(cls, XMLElement):
            raise TypeError('Excepted XMLElement or Entity, got {}'.format(cls))

        def __combinator_call__(es: [Element]) -> XMLElement:
            return logic_fn(cls, es)
        setattr(__combinator_call__, COMBINATOR_CTOR, cls)
        return __combinator_call__
    return __combinator__


@xml_combinator
def one(cls, es: [Element]) -> XMLElement:
    result, found = None, False
    for e in es:
        if cls.match_tag(e.tag):
            if not found:
                result, found = cls(e), True
            else:
                raise ValueError('Multiple {} found'.format(cls.__name__))
    if found:
        return result
    else:
        raise ValueError('No {} found'.format(cls.__name__))


@xml_combinator
def many(cls, es) -> List[XMLElement]:
        return [cls(e) for e in es if cls.match_tag(e)]


@xml_combinator
def optional(cls, es: [Element]) -> Optional[XMLElement]:
    result, found = None, False
    for e in es:
        if cls.match_tag(e):
            if not found:
                result, found = cls(e), True
            else:
                raise ValueError('Multiple {} found'.format(cls.__name__))
    return result


def entity(fn):
    def __entity__(text: str) -> fn:
        return fn(text)

    setattr(__entity__, ENTITY_CTOR, fn)
    return __entity__


def date(text):
    y, m, d = map(int, text.split('-'))
    return pydate(year=y, month=m, day=d)
