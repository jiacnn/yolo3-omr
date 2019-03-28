#!/usr/bin/env python
# coding=utf-8
#生成特定label的ｂｂｏｘ
import glob
from multiprocessing import Pool

all_label = ['accidental','beam','clef','hook','keysig','note','notedot','rest','slursegment','timesig']
all_labels = ['0','1','2','3','4','5','6','7','8','9']
def txt_change(txt):
    #path = '/home/jx/下载/phantomjs-2.1.1-linux-x86_64/txt/'
    #all_txt = glob.glob('{}*.txt'.format(path))
    #for txt in all_txt:
    print(txt)
    a = open(txt.replace('/imgs/', '/txt1/'), 'w')
    doc = open(txt,'r')
    all_lines = doc.readlines()
    for line in all_lines:
        line = line.split(',')
        label = line[0].lower()
        for index,i in enumerate(all_labels):
            if label == i and i!='StaffLines':
                line[0]=str(all_label[index])
                a.write(','.join(i for i in line ) )
def print_txt(a,b,txt):
    #a = open('/home/jx/label.txt',"w")
    a.write(txt+'\n')
    #b = open('/home/jx/train.txt',"w")
    b.write(txt.replace('.txt','.png')+'\n')

def main():
    path = '/home/jx/下载/phantomjs-2.1.1-linux-x86_64/imgs/'
    all_txt = glob.glob('{}*.txt'.format(path))
    pool = Pool(8)
    pool.map(txt_change,all_txt)
   # a = open('/home/jx/label.txt', "w")
   # b = open('/home/jx/train.txt', "w")
    #for txt in all_txt:
     #   print_txt(a,b,txt)

if __name__=='__main__':
    main()
