#!/usr/bin/env python
# coding=utf-8

import cairosvg
import glob
import multiprocessing 

def change(svg):
   print(svg)
   cairosvg.svg2png(
        url = svg,write_to=svg.replace('.svg','.png')
        )

all_svg = glob.glob('/home/jx/svg_single/*.svg')
pool = multiprocessing.Pool(8)
pool.map(change,all_svg)
