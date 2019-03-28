
from gluoncv.data.transforms.image import ten_crop
from gluoncv.data.transforms import bbox
import numpy as np
from omr_dataset import OMRDtection
import copy

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
        # for idx,img in cropped_image:
        #     bbox.crop(self.bbox,crop_box=i)
        self.bbox [:,1:]= self.transform_albel( self.bbox [:,1:])

        c_crop_box_label = bbox.crop(self.bbox [:,1:],crop_box=c_crop_box,allow_outside_center=False)
        bl_crop_box_label = bbox.crop(self.bbox [:,1:],crop_box=bl_crop_box,allow_outside_center=False)
        tl_crop_box_bael = bbox.crop(self.bbox [:,1:],crop_box=tl_crop_box,allow_outside_center=False)
        tr_crop_box_label = bbox.crop(self.bbox [:,1:],crop_box=tr_crop_box,allow_outside_center=False)
        br_crop_box_label = bbox.crop(self.bbox [:,1:],crop_box=br_crop_box,allow_outside_center= False)
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
        bbox[:,1:2] = bbox[:,1:2]*h -bbox[:,3:]*h/2
        bbox[:, 2:3] = bbox[:, :1] +bbox[:,2:3]*w
        bbox[:, 3:] = bbox[:, 1:2]+bbox[:,3:]*h
        return bbox

if __name__ == '__main__':
    #image_path = 'home/jx/'
 """  import os
 
   # a = OMRDtection
   a=OMRDtection(root=os.path.join('~', 'augimg_data'))
   image,label = a[100]
   b=crop_image(image,label,400,400)
   c= b._crop()
   import cv2
   img = cv2.imread('/home/jx/augimg_data/1279001.png')

   for idx,i in enumerate(c):
      try:
          for x in i[1]:
              x0,y0,x1,y1 =map(int,x)
              if idx==1:
                cv2.rectangle(img,(x0,y0),(x1,y1),(0,0,255))
          if idx ==1:
            cv2.imwrite('/home/jx/1121.png',img)
            print('saved image')
      except:
          print(123)

"""
