import imgaug as ia
from imgaug import augmenters as iaa
import cv2
import random
import glob
from multiprocessing import Pool

    #@property
def Transform_method():
    sometimes = lambda aug: iaa.Sometimes(0.6, aug)
    # Define our sequence of augmentation steps that will be applied to every image
    # All augmenters with per_channel=0.5 will sample one value _per image_
    # in 50% of all cases. In all other cases they will sample new values
    # _per channel_.
    seq = iaa.Sequential(
        [
            # apply the following augmenters to most images
           # iaa.Fliplr(0.5), # horizontally flip 50% of all images
            #iaa.Flipud(0.2), # vertically flip 20% of all images
             sometimes(iaa.Affine(
               scale={"x": (0.9, 1.1), "y": (0.8, 1.2)}, # scale images to 80-120% of their size, individually per axis
                #translate_percent={"x": (-0.1, 0.1), "y": (-0.1, 0.1)}, # translate by -20 to +20 percent (per axis)
                rotate=(-2, 2), # rotate by -45 to +45 degrees
                shear=(-2, 2), # shear by -16 to +16 degrees
                order=[0,1], # use nearest neighbour or bilinear interpolation (fast)
           #     cval=(0, 255), # if mode is constant, use a cval between 0 and 255
                #mode=ia.ALL # use any of scikit-image's warping modes (see 2nd image from the top for examples)
            )),
            iaa.Grayscale(alpha=(0.0, 1.0)),
            #sometimes(iaa.ElasticTransformation(alpha=(1.5, 3.5), sigma=2)),
            # move pixels locally around (with random strengths)
            # sometimes(iaa.PiecewiseAffine(scale=(0.03, 0.05))), # sometimes move parts of the image around
            #sometimes(iaa.PerspectiveTransform(scale=(0.04, 0.075))),
            # execute 0 to 5 of the following (less important) augmenters per image
            # don't execute all of them, as that would often be way too strong

            iaa.SomeOf((1,3),
                [
                    #sometimes(iaa.Superpixels(p_replace=(0, 1.0), n_segments=(20, 200))), # convert images into their superpixel representation
                   iaa.OneOf([
                     iaa.GaussianBlur((0, 2.0)), # blur images with a sigma between 0 and 3.0
                      iaa.AverageBlur(k=(1, 3)), # blur image using local means with kernel sizes between 2 and 7
                       iaa.MedianBlur(k=(1, 3)), # blur image using local medians with kernel sizes between 2 and 7
                   ]),
                   #iaa.Sharpen(alpha=(0, 1.0), lightness=(0.25, 0.5)), # sharpen images
                    #iaa.SimplexNoiseAlpha(iaa.OneOf([
                   #     iaa.EdgeDetect(alpha=(0.2, 0.5)),
                   #    iaa.DirectedEdgeDetect(alpha=(0.2, 0.5), direction=(0.0, 1.0)),
                   # ])),
                     iaa.AdditiveGaussianNoise(loc=0, scale=(0.0, 0.005*255), per_channel=0.5), # add gaussian noise to images
                  #  iaa.OneOf([
                   #    iaa.Multiply((0.5, 1.5), per_channel=0.5),
                  #    iaa.Dropout((0.01, 0.1), per_channel=0.5), # randomly remove up to 10% of the pixels
                  # ]),
                    #iaa.Invert(0.05, per_channel=True), # invert color channels
                    iaa.Add((-10, 10), per_channel=0.5), # change brightness of images (by -10 to 10 of original value)
                    iaa.AddToHueAndSaturation((-20, 20)), # change hue and saturation
                    iaa.ContrastNormalization((0.5, 1.0), per_channel=0.5), # improve or worsen the contrast
                    iaa.Grayscale(alpha=(0.0, 1.0)),
                    iaa.ElasticTransformation(alpha=(5, 25), sigma=5), # move pixels locally around (with random strengths)
                   # sometimes(iaa.PiecewiseAffine(scale=(0.01, 0.05))), # sometimes move parts of the image around
                ],
                random_order=True
            )
        ],
        random_order=True
    )
    seq_det = seq.to_deterministic()
    return seq_det

#@staticmethod
def change_bg(image):
    color = random.choice([232,207,211])
    image[image > 200] = color
    return image

def Start_transfrom(input_image):
    #ia.seed(100)
    #seq_det = self.Transform_method

    save_path = '/home/jx/test_chard1'
    image = cv2.imread(input_image)
    image_name = input_image.split('/')[-1:]
    label = input_image.replace('png', 'txt')
    labels = open(label, 'r')
    label_name = label.split('/')[-1:]
    labels = labels.readlines()
    all_label = []
    h, w, c = image.shape
    for label in labels:
        label = label.split(' ')
        all_label.append(label)
    bbs = ia.BoundingBoxesOnImage([
        ia.BoundingBox(x1=(float(label[1])) ,#* float(w),
                       y1=(float(label[2]) ), #* float(h),
                       x2=(float(label[1]) + float(label[3])) ,#* float(w),
                       y2=(float(label[2]) + float(label[4])), #* float(h),
                       label=label[0]) for label in all_label],
        shape=image.shape)
    print(image_name)
    #for i in range(3):
    seq_det = Transform_method()
    image_aug = seq_det.augment_images([image])[0]
    bbs_aug = seq_det.augment_bounding_boxes([bbs])[0].remove_out_of_image().cut_out_of_image()
    img_label = open( '{}/_{}'.format(save_path,label_name[0]), 'w')
#    image = change_bg(image_aug)
    cv2.imwrite('{}/_{}'.format(save_path,image_name[0]), image_aug)
    for bbox in bbs_aug.bounding_boxes:
        x1,y1,x2,y2,label = bbox.x1,bbox.y1,bbox.x2,bbox.y2,bbox.label
        x_center,y_center,w1,h1 = (x1+x2)/(2*w),(y1+y2)/(2*h),(x2-x1)/w,(y2-y1)/h
        img_label.write(str(label)+' '+str(x_center)+' '+str(y_center)+' '+str(w1)+' '+str(h1)+'\n')
    img_label.close()
    return
def main():
   # ia.seed(100)
    imgs = glob.glob('/home/jx/下载/generated_data/*.png')


    pool = Pool(8)
    pool.map(Start_transfrom,imgs)
#pool.map(Process_Img,imgs)
if __name__ == '__main__':
    main()