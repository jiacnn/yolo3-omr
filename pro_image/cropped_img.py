
from gluoncv.data.transforms.image import ten_crop
from gluoncv.data.transforms import bbox
import numpy as np
#from omr_dataset import OMRDtection
import copy
import cv2
import os
import mxnet as mx
class crop_image(object):
    def __init__(self,image,all_bbox,width,height):
        self.image = image   # ndarray(xmin.ymin.xmax,ymax)
        self.bbox = copy.deepcopy(all_bbox)
        #self.bbox  = all_bbox[:,1:]#(xmin,y_min.w.h)

        self.width = width
        self.height = height
        #self._crop()

    def __str__(self):
        return 'crop image '

    def _crop(self):

        cropped_image = ten_crop(self.image,(self.width,self.height))  # center, tl,bl,tr,br
        h,w,c = self.image.shape
        oh ,ow= self.height,self.width
        c_crop_box = ((w - ow) // 2,(h - oh) // 2,self.width,self.height)
        tl_crop_box = (0,0,self.width,self.height)
        bl_crop_box = (0,h-oh,self.width,self.height)
        tr_crop_box = (w-ow,0,self.width,self.height)
        br_crop_box = (w-ow,h-oh,self.width,self.height)

        center = self.image[(h - oh) // 2:(h + oh) // 2, (w - ow) // 2:(w + ow) // 2, :]
        tl = self.image[0:oh, 0:ow, :]
        bl = self.image[h - oh:h, 0:ow, :]
        tr = self.image[0:oh, w - ow:w, :]
        br = self.image[h - oh:h, w - ow:w, :]
        all_images = [center,tl,bl,tr,br]
        self.bbox [:,1:]= self.transform_albel( self.bbox [:,1:])
        new_bbox = np.zeros((self.bbox.shape))
        new_bbox[:, :6] = self.bbox[:, 1:]
        new_bbox[:, 6] = self.bbox[:, 0]
        c_crop_box_label = bbox.crop(new_bbox,crop_box=c_crop_box,allow_outside_center=False)
        bl_crop_box_label = bbox.crop(new_bbox,crop_box=bl_crop_box,allow_outside_center=False)
        tl_crop_box_bael = bbox.crop(new_bbox,crop_box=tl_crop_box,allow_outside_center=False)
        tr_crop_box_label = bbox.crop(new_bbox,crop_box=tr_crop_box,allow_outside_center=False)
        br_crop_box_label = bbox.crop(new_bbox,crop_box=br_crop_box,allow_outside_center= False)
        # crop_bbox = np.stack(*[c_crop_box_label,bl_crop_box_label,tr_crop_box_label,tl])
        all_crop_bbox = [c_crop_box_label,tl_crop_box_bael,bl_crop_box_label,tr_crop_box_label,br_crop_box_label]

        return  zip(all_images,all_crop_bbox)
    def transform_albel(self,bbox):
        """
        transfrom (xc,yc,w,h)->(xmin,ymin,xmax,ymax)
        :return: ndnumpy
        """
        h, w, c = self.image.shape
        bbox[:,:1] =bbox[:,:1]*w-bbox[:,2:3]*w/2
        bbox[:,1:2] = bbox[:,1:2]*h -bbox[:,3:4]*h/2
        bbox[:, 2:3] = bbox[:, :1] +bbox[:,2:3]*w
        bbox[:, 3:4] = bbox[:, 1:2]+bbox[:,3:4]*h
        bbox
        return bbox

if __name__ == '__main__':
    #image_path = 'home/jx/'

    image_path = "/Users/jx/Desktop/jjjjjxxxx/CODED_LABEL"
    import glob
    imgs = glob.glob(image_path+'/*.png')
    count = 0
    for img in imgs[:]:

        label_txt = img.replace('.png','_coded_label.txt')
        if not os.path.exists(label_txt):
            continue
        img = mx.img.imread(img)
        label = np.loadtxt(label_txt)
        h, w, _ = img.shape
        b = crop_image(img,label,int(w/2),int(h/2))
        c=b._crop()

        for img,labels in c:
            img = img.asnumpy()
            cv2.imwrite('{}.png'.format(count),img)
            f = open('{}.txt'.format(count),'w')
            for label in labels:
                cls = label[-1]
                f.write(str(cls)+' '+' '.join(map(str,label[:6]))+'\n')
            count+=1

        """
        验证正确性
        
        for img, i in c:
            img = img.asnumpy()
            for x in i:
                x0,y0,x1,y1 =list(map(int,x[:4]))
                img = cv2.rectangle(img,(x0,y0),(x1,y1),(0,0,255))

            cv2.imwrite('{}.png'.format(count),img)
            count+=1
            print('saved image')

        raise('fuck zj')
        """



