#!/usr/bin/env python
# coding=utf-8
#svgcairo转图围rgba，转化为rgb
import cv2
import glob
import os
from multiprocessing import Pool

def To_rgb(image):
    save_path = '/home/jx/下载/phantomjs-2.1.1-linux-x86_64/imgs'
    img_name = image.split('/')[-1:]
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    img = cv2.imread(image,cv2.IMREAD_UNCHANGED)
    alpha = img[:,:,3:4]
    rgb_img = 255 - cv2.cvtColor(alpha,cv2.COLOR_GRAY2RGB)
    cv2.imwrite('{}/{}'.format(save_path,img_name[0]),rgb_img)

def main():
    image_path = '/home/jx/下载/phantomjs-2.1.1-linux-x86_64/images/'
    images = glob.glob('{}*.png'.format(image_path))
    pool = Pool(8)
    pool.map(To_rgb,images)

if __name__ == '__main__':
    main()