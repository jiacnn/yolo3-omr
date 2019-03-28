import cv2
import numpy as np

class Get_Duration():

    def __init__(self,image,label,txt):
        self.image = cv2.imread(image,0)
        self.label = open(label,'r')
        self.h,self.w = self.image.shape
        self.txt = txt

    def get_symbol(self):

        all_symbols = {'note': [], 'beam': [], 'hook': [], 'stem': [], 'notedot': []}
        lines = self.label.readlines()
        for line in lines:
            line = line.split(',')
            symbol_name = line[0]
            if symbol_name.lower()=='note':
                all_symbols['note'].append(line)
            elif symbol_name.lower()=='beam':
                all_symbols['beam'].append(line)
            elif symbol_name.lower()=='hook':
                all_symbols['hook'].append(line)
            elif symbol_name.lower()=='stem':
                all_symbols['stem'].append(line)
            elif symbol_name.lower()=='notedot':
                all_symbols['notedot'].append(line)
        return all_symbols

    def match_symbol(self):
        '''
        １: 判断空心实心
        ２:判断是否有符杆
        ３:判断符杠
        ４:判断钩子
        ４:判断附点
        :return:
        　   note duration
        '''
        all_symbol = self.get_symbol()
        all_note = all_symbol['note']
        all_stem = all_symbol['stem']
        all_beam = all_symbol['beam']
        all_notedot = all_symbol['notedot']
        all_hook = all_symbol['hook']
        new_txt =open('new_label.txt','w')
        for note in all_note:

            duration = 1
            note_x, note_y, note_w, note_h = map(float, note[1:])
            note_x_center,note_y_center = note_x*self.w,note_y*self.h
            note_xmin = (note_x - note_w / 2) * self.w
            note_ymin = (note_y - note_h / 2) * self.h
            note_xmax = (note_x + note_w / 2) * self.w
            note_ymax = (note_y + note_h / 2) * self.h
            note_bbox = self.image[int(note_ymin):int(note_ymax),int(note_xmin):int(note_xmax)]
           # print('-----------',np.sum(note_bbox))
            if np.sum(note_bbox)<5800:   #实心note
                duration = duration/2
                for stem in all_stem:
                    stem_x, stem_y, stem_w, stem_h = map(float, stem[1:])
                    stem_xmin = (stem_x - stem_w / 2) * self.w
                    stem_xmax = (stem_x + stem_w / 2) * self.w
                    stem_ymin = (stem_y - stem_h / 2) * self.h
                    stem_ymax = (stem_y + stem_h / 2) * self.h
                    stem_x_center, stem_y_center = stem_x * self.w, stem_y * self.h
                    #if np.abs(stem_x_center - note_x_center) < note_w and np.abs(
                     #       stem_y_center - note_y_center) < 20:  # 有　符杆
                    if (np.abs(stem_ymax-note_y_center)<note_h*self.h and np.abs(stem_x_center-note_x_center)<note_w*self.w)\
                            or (np.abs(stem_ymin-note_y_center)<note_h*self.h and np.abs(stem_x_center-note_x_center)<note_w*self.w) and \
                            (stem_x_center-1<note_xmin<stem_x_center+1 or stem_x_center-1<note_xmax<stem_x_center+1):
                        duration = duration / 2
                        for beam in all_beam:
                            beam_x, beam_y, beam_w, beam_h = map(float, beam[1:])
                            beam_x_center, beam_y_center = beam_x * self.w, beam_y * self.h
                            beam_xmin = (beam_x - beam_w / 2) * self.w
                            beam_ymin = (beam_y - beam_h / 2) * self.h
                            beam_xmax = (beam_x + beam_w / 2) * self.w
                            beam_ymax = (beam_y + beam_h / 2) * self.h
                            if (np.abs(beam_y_center - stem_ymin) < 10 or np.abs(
                                    beam_y_center - stem_ymax) < 10 )and beam_xmin-5<stem_x_center<beam_xmax+5:  # 符杆上有符杠
                                duration = duration / 2
                        for hook in all_hook:  # 符杆是否有hook
                           hook_x, hook_y, hook_w, hook_h = map(float, hook[1:])
                           hook_x_center, hook_y_center ,hook_w,hook_h= hook_x * self.w, hook_y * self.h,hook_w*self.w,hook_h*self.h
                           if 0<hook_x_center-stem_x_center<hook_w and np.abs(hook_y_center-stem_y_center)<10:
                               duration =duration/2
                for notedot in all_notedot:
                    notedot_x, notedot_y, notedot_w, notedot_h = map(float, notedot[1:])
                    notedot_x_center, notedot_y_center, notedot_w, notedot_h = notedot_x * self.w, notedot_y * self.h, notedot_w * self.w, notedot_h * self.h
                    if 0<notedot_x_center -note_xmax<5 and np.abs(notedot_y_center-note_y_center)<note_h*self.h:
                        duration = duration*1.5
            else:#空心note->判断符杆,符点
                for stem in all_stem:
                    #distance = 10
                    stem_x, stem_y, stem_w, stem_h = map(float, stem[1:])
                    stem_xmin = (stem_x - stem_w / 2) * self.w
                    stem_xmax = (stem_x + stem_w / 2) * self.w
                    stem_ymin = (stem_y - stem_h / 2) * self.h
                    stem_ymax = (stem_y + stem_h / 2) * self.h
                    stem_x_center, stem_y_center = stem_x * self.w, stem_y * self.h
                    if (np.abs(stem_ymax - note_y_center) < note_h * self.h and np.abs(
                            stem_x_center - note_x_center) < note_w * self.w) \
                            or (np.abs(stem_ymin - note_y_center) < note_h * self.h and np.abs(
                        stem_x_center - note_x_center) < note_w * self.w) and \
                            (stem_x_center - 1 < note_xmin < stem_x_center + 1 or stem_x_center - 1 < note_xmax < stem_x_center + 1):#有　符杆
                        duration = duration/2
                        for notedot in all_notedot:
                            notedot_x, notedot_y, notedot_w, notedot_h = map(float, notedot[1:])
                            notedot_x_center, notedot_y_center, notedot_w, notedot_h = notedot_x * self.w, notedot_y * self.h, notedot_w * self.w, notedot_h * self.h
                            if 0 < notedot_x_center - note_xmax < 5 and np.abs(
                                    notedot_y_center - note_y_center) < note_h * self.h:
                                duration = duration * 1.5
            if duration<1/16:
                duration=0
            #print(duration)
            self.txt.write('6 ' + ' '.join(str(i) for i in [note_x, note_y, note_w, note_h]) +' '+str(duration)+'\n' )

#!/usr/bin/env python
# coding=utf-8

import glob
from multiprocessing import Pool

#all_labels = ['0','2','4','7','8','9']
all_labels = ['accidental','clef','keysig','rest','slursegment','timesig']
# ['accidental','beam','clef','hook','keysig','note','notedot','rest','slursegment','timesig']
def txt_change(txt):
    #path = '/home/jx/下载/phantomjs-2.1.1-linux-x86_64/txt/'
    #all_txt = glob.glob('{}*.txt'.format(path))
    #for txt in all_txt:
    print(txt)
    a = open(txt.replace('/txt/', '/txt1/'), 'w')
    img_path = '/home/jx/下载/phantomjs-2.1.1-linux-x86_64/imgs/'
    img = img_path+txt.split('/')[-1].replace('txt','png')
    import os
    if os.path.isfile(img):

        C_duration = Get_Duration(img, txt, a)
        C_duration.match_symbol()
        doc = open(txt,'r')
        all_lines = doc.readlines()
        for line in all_lines:
            line = line.strip('\n').split(',')
            label = line[0].lower()
            if label not in all_labels:
                pass
            else:
                for index, i in enumerate(all_labels):
                    if label == i :
                        line[0] = str(index)
                        a.write(' '.join(i for i in line) +' 0'+'\n')
def print_txt(a,b,txt):
    #a = open('/home/jx/label.txt',"w")
    a.write(txt+'\n')
    #b = open('/home/jx/train.txt',"w")
    b.write(txt.replace('.txt','.png')+'\n')

def main():
    path = '/home/jx/下载/phantomjs-2.1.1-linux-x86_64/txt/'
    all_txt = glob.glob('{}*.txt'.format(path))
    pool = Pool(8)
    pool.map(txt_change,all_txt)
   # a = open('/home/jx/label.txt', "w")
   # b = open('/home/jx/train.txt', "w")
    #for txt in all_txt:
     #   print_txt(a,b,txt)

if __name__=='__main__':
    main()
'''
if __name__ =="__main__":
     img = '/home/jx/3442.png'
     label = '/home/jx/3442.txt'
     a = Get_Duration(img,label)
     a.match_symbol()

'''