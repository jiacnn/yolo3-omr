# encoding: UTF-8

from musescore.mxl.combinator import one, many, optional, XMLElement, entity, date
from dataclasses import dataclass
from enum import IntEnum, Enum


class StemDirection(Enum):
    UP, DOWN = 'up', 'down'

    @staticmethod
    def from_string(text) -> 'StemDirection':
        if text in ('up', 'down'):
            return StemDirection(text)
        else:
            raise ValueError('Excepted up | down')


class PitchStep(IntEnum):
    A, B, C, D, E, F, G = 0, 1, 2, 3, 4, 5, 6

    @staticmethod
    def from_string(text) -> 'PitchStep':
        if not isinstance(text, str) or len(text) != 1:
            raise ValueError(f'Excepted [A-G], got {text!r}')
        step = ord(text) - ord('A')
        if not 0 <= step < 7:
            raise ValueError(f'Excepted [A-G], got {text!r}')
        return PitchStep(step)


class SlurType(Enum):
    START, STOP = 'start', 'stop'


@dataclass(init=False)
class Pitch(XMLElement):
    step: entity(PitchStep.from_string)
    octave: entity(int)


@dataclass(init=False)
class Slur(XMLElement):
    type: SlurType
    number: int


@dataclass(init=False)
class Notations(XMLElement):
    slur: optional(Slur)


@dataclass(init=False)
class Note(XMLElement):
    pitch: one(Pitch)
    duration: entity(int)
    voice: entity(int)
    type: entity(str)
    stem: entity(StemDirection.from_string)
    notation: optional(Notations)


@dataclass(init=False)
class Encoding(XMLElement):
    encoder:  entity(str)
    software: entity(str)
    supports: entity(str)
    encoding_date: entity(date)
    encoding_description: entity(str)


@dataclass(init=False)
class Identification(XMLElement):
    encoding: optional(Encoding)


@dataclass(init=False)
class Key(XMLElement):
    fifths: entity(int)
    mode: entity(str)


@dataclass(init=False)
class Time(XMLElement):
    beats: entity(int)
    beat_type: entity(int)


@dataclass(init=False)
class Clef(XMLElement):
    sign: entity(PitchStep.from_string)
    line: entity(int)


@dataclass(init=False)
class Transpose(XMLElement):
    diatonic: entity(int)
    chromatic: entity(int)


@dataclass(init=False)
class Attributes(XMLElement):
    divisions: entity(int)
    time: one(Time)
    key: one(Key)
    clef: one(Clef)
    transpose: one(Transpose)


@dataclass(init=False)
class Measure(XMLElement):
    number: int
    attributes: optional(Attributes)
    note: many(Note)


@dataclass(init=False)
class Part(XMLElement):
    id: str
    measure: many(Measure)


@dataclass(init=False)
class PartWise(XMLElement):
    identification: one(Identification)
    part: one(Part)
