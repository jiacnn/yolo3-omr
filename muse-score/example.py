# encoding: UTF-8

import PIL.Image
from musescore.svg.parser import parse as parse_svg
from musescore.mxl.parser import parse as parse_mxl
from musescore.mxl.part import *
page = parse_svg('data/977.svg')
pw = parse_mxl('data/977.mxl')
R = 3.123  # re-sampled @ DPI=300
#f = open('mxl.txt','w')
im = PIL.Image.open('data/977.png')  # type: PIL.Image.Image


for (measure, graphic_measure), semantic_measure in zip(page.rearrange(), pw.part.measure):
    print(f'======== MEASURE {semantic_measure.number} ========')
    if semantic_measure.attributes:
        print(semantic_measure.attributes)
        for symbol in graphic_measure:
            if not symbol.type.startswith('Note'):
                print(symbol)
    for note in semantic_measure.note:
        if note.notation is not None and note.notation.slur is not None:
            if note.notation.slur.type == SlurType.START:
                print("Slur start")
                print(note)
            else:
                print(note)
                print("Slur stop")
        else:
            print(note)

    for symbol in graphic_measure:
        if symbol.type.startswith('Note'):
            print(symbol.bbox)
    xmin, xmax, ymin, ymax = measure.bbox.xmin, measure.bbox.xmax, measure.bbox.ymin, measure.bbox.ymax
    crop = im.crop((int(xmin * R), int((ymin - 20) * R), int(xmax * R), int((ymax + 20) * R)))
    crop.show(title=f'Measure {semantic_measure.number}')
    input()
