import os
import glob
all_txt = glob.glob('../pro_image/data/*.txt')
for txt in all_txt:
    a = open(txt,'r')
    lines = a.readlines()
    if lines ==[]:
        os.remove(txt)
        print(txt)
        os.remove(txt.replace('txt','png'))

