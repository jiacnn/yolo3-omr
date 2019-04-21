# encoding: UTF-8

from __future__ import annotations

from lxml.etree import parse as parse_xml
from musescore.svg.part import *


__all__ = ['Estimator']


class Estimator:
    def __init__(self):
        self.path_command_to_space = {ord(c): ' ' for c in 'MLHVCSQTAZ,'}

    def parse_points(self, element: Element):
        unparsed = element.attrib.get('d', element.attrib.get('points'))  # type: str
        numbers = [float(num) for num in unparsed.translate(self.path_command_to_space).split()]
        return numbers[::2], numbers[1::2]

    def estimate(self, page, document: ElementTree) -> [Symbol]:
        svg = document.getroot()  # type: Element
        for element in svg.getchildren():  # type: Element
            tag = element.tag
            if len(tag) > 28:
                tag = tag[28:]
            classname = element.attrib.get('class', None)
            graphic_fn = getattr(self, 'on_{}'.format(tag.lower()), None)
            semantic_fn = getattr(self, 'on_{}'.format(classname), self.on_class)
            if callable(graphic_fn) and callable(semantic_fn):
                symbol = Symbol(type=classname, svg=element, is_path=element.tag == 'path')
                graphic_fn(element, symbol)
                semantic_fn(element, symbol)
                page.symbols.append(symbol)

    def on_path(self, path: Element, symbol: Symbol):
        # 估计 Bounding Box
        symbol.is_path = True
        xs, ys = self.parse_points(path)
        symbol.bbox = BoundingBox(min(xs), min(ys), max(xs), max(ys))

    def on_polyline(self, polyline: Element, symbol: Symbol):
        symbol.is_path = False
        xs, ys = self.parse_points(polyline)
        symbol.bbox = BoundingBox(min(xs), min(ys), max(xs), max(ys))

    def on_note(self, note: Element, symbol: Symbol):
        pass

    def on_stem(self, stem: Element, symbol: Symbol):
        pass

    def on_hook(self, hook: Element, symbol: Symbol):
        pass

    def on_notedot(self, dot: Element, symbol: Symbol):
        pass

    def on_clef(self, clef: Element, symbol: Symbol):
        pass

    def on_stafflines(self, line: Element, symbol: Symbol):
        pass

    def on_barline(self, line: Element, symbol: Symbol):
        pass

    def on_class(self, e: Element, symbol: Symbol):
        pass

    @staticmethod
    def parse(page, filename):
        estimator = Estimator()
        document = parse_xml(filename)  # type: ElementTree
        estimator.estimate(page, document)


def parse(filename: str) -> Page:
    page = Page()
    Estimator.parse(page, filename)
    return page
