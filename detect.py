import argparse
import time

from models import *
from utils.datasets import *
from utils.utils import *

cuda = torch.cuda.is_available()
device = torch.device('cuda:0' if cuda else 'cpu')
f_path = os.path.dirname(os.path.realpath(__file__)) + '/'

parser = argparse.ArgumentParser()
# Get data configuration

parser.add_argument('-image_folder', type=str, default='data1', help='path to images')
parser.add_argument('-output_folder', type=str, default='output', help='path to outputs')
parser.add_argument('-plot_flag', type=bool, default=True)
parser.add_argument('-txt_out', type=bool, default=False)

parser.add_argument('-cfg', type=str, default=f_path + 'cfg/yolo3-832.cfg', help='cfg file path')
parser.add_argument('-class_path', type=str, default=f_path + 'data/new_omr.names', help='path to class label file')
parser.add_argument('-conf_thres', type=float, default=0.3, help='object confidence threshold')
parser.add_argument('-nms_thres', type=float, default=0.50, help='iou threshold for non-maximum suppression')
parser.add_argument('-batch_size', type=int, default=1, help='size of the batches')
parser.add_argument('-img_size', type=int, default=64 *36, help='size of each image dimension')
opt = parser.parse_args()
print(opt)


def main(opt):
    os.system('rm -rf ' + opt.output_folder)
    os.makedirs(opt.output_folder, exist_ok=True)

    # Load model
    model = Darknet(opt.cfg, opt.img_size)

    weights_path = f_path + 'weights/best.pt'
    if weights_path.endswith('.weights'):  # saved in darknet format
        load_weights(model, weights_path)
   # else:  # endswith('.pt'), saved in pytorch format
    #    if weights_path.endswith('weights/yolov3.pt') and not os.path.isfile(weights_path):
    #        os.system('wget https://storage.googleapis.com/ultralytics/yolov3.pt -O ' + weights_path)

    checkpoint = torch.load(weights_path, map_location='cpu')
    model.load_state_dict(checkpoint['model'])
    del checkpoint

        # current = model.state_dict()
        # saved = checkpoint['model']
        # # 1. filter out unnecessary keys
        # saved = {k: v for k, v in saved.items() if ((k in current) and (current[k].shape == v.shape))}
        # # 2. overwrite entries in the existing state dict
        # current.update(saved)
        # # 3. load the new state dict
        # model.load_state_dict(current)
        # model.to(device).eval()
        # del checkpoint, current, saved

    model.to(device).eval()

    # Set Dataloader
    classes = load_classes(opt.class_path)  # Extracts class labels from file
    dataloader = load_images(opt.image_folder, batch_size=opt.batch_size, img_size=opt.img_size)

    imgs = []  # Stores image paths
    img_detections = []  # Stores detections for each image index
    prev_time = time.time()
    for i, (img_paths, img) in enumerate(dataloader):
        print('%g/%g' % (i + 1, len(dataloader)), end=' ')

        # Get detections
        with torch.no_grad():
            pred = model(torch.from_numpy(img).unsqueeze(0).to(device))
            pred = pred[pred[:, :, 4] > opt.conf_thres]
            if len(pred) > 0:
                detections = non_max_suppression(pred.unsqueeze(0), opt.conf_thres, opt.nms_thres)
                img_detections.extend(detections)
                imgs.extend(img_paths)

        print('Batch %d... Done. (%.3fs)' % (i, time.time() - prev_time))
        prev_time = time.time()

    # Bounding-box colors
    color_list = [[random.randint(0,200), random.randint(0, 200), random.randint(0, 200)] for _ in range(len(classes))]

    if len(img_detections) == 0:
        return

    # Iterate through images and save plot of detections
    for img_i, (path, detections) in enumerate(zip(imgs, img_detections)):
        print("image %g: '%s'" % (img_i, path))

        if opt.plot_flag:
            img = cv2.imread(path)
        # The amount of padding that was added
        pad_x = max(img.shape[0] - img.shape[1], 0) * (opt.img_size / max(img.shape))
        pad_y = max(img.shape[1] - img.shape[0], 0) * (opt.img_size / max(img.shape))
        # Image height and width after padding is removed
        unpad_h = opt.img_size - pad_y
        unpad_w = opt.img_size - pad_x

        # Draw bounding boxes and labels of detections
        if detections is not None:
            unique_classes = detections[:, -5].cpu().unique()
            bbox_colors = random.sample(color_list, len(unique_classes))

            # write results to .txt file
            results_img_path = os.path.join(opt.output_folder, path.split('/')[-1])
            results_txt_path = results_img_path + '.txt'
            if os.path.isfile(results_txt_path):
                os.remove(results_txt_path)

            for i in unique_classes:
                n = (detections[:, -1].cpu() == i).sum()
               # print('%g %ss' % (n, classes[int(i)]))
            for x1, y1, x2, y2, conf, cls_conf, cls_pred,duration_conf, duration_pred, pitch_conf, pitch_pred in detections:
                # Rescale coordinates to original dimensions
                box_h = ((y2 - y1) /unpad_h ) * img.shape[0]
                box_w = ((x2 - x1) /unpad_w ) * img.shape[1]
                y1 = (((y1 - pad_y // 2) / unpad_h) * img.shape[0]).round().item()
                x1 = (((x1 - pad_x // 2) / unpad_w) * img.shape[1]).round().item()
                x2 = (x1 + box_w).round().item()
                y2 = (y1 + box_h).round().item()
                x1, y1, x2, y2 = max(x1, 0), max(y1, 0), max(x2, 0), max(y2, 0)

                # write to file
               # if 1:
                if opt.txt_out:
                    with open(results_txt_path, 'a') as file:
                        file.write((' %g %g %g %g %g %g %g\n') % (x1, y1, x2, y2, cls_pred, cls_conf * conf,duration_pred))

                if opt.plot_flag:
                    # Add the bbox to the plot
                    label = '%s %d %d' % (classes[int(cls_pred)] ,int(duration_pred),int(pitch_pred))
                    
                    color = bbox_colors[int(np.where(unique_classes == int(cls_pred))[0])]
                    plot_one_box([x1, y1, x2, y2], img, label=label, color=color)

        if opt.plot_flag:
            # Save generated image with detections
            print(results_img_path)
            cv2.imwrite(results_img_path.replace('.bmp', '.jpg').replace('.tif', '.jpg'), img)

    if platform == 'darwin':  # MacOS (local)
        os.system('open ' + opt.output_folder)


if __name__ == '__main__':
    torch.cuda.empty_cache()
    main(opt)
