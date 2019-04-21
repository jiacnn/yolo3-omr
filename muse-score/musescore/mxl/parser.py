# encoding: UTF-8

from zipfile import ZipFile
from lxml import etree
from musescore.mxl.part import PartWise

__all__ = ['parse']


def parse(filename: str) -> PartWise:
    mxlfile = ZipFile(filename)
    for info in mxlfile.filelist:
        if not info.filename.startswith('META-INF'):
            xml = mxlfile.read(info.filename)  # type: bytes
            doc = etree.fromstring(xml)  # type: etree._ElementTree
            return PartWise(doc)
    else:
        raise ValueError(f'Invalid file {filename!r}')
