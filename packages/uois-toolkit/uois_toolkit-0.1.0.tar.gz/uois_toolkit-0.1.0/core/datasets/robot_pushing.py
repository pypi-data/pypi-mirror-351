#----------------------------------------------------------------------------------------------------
# Work done while being at the Intelligent Robotics and Vision Lab at the University of Texas, Dallas
# Please check the licenses of the respective works utilized here before using this script.
# 🖋️ Jishnu Jaykumar Padalunkal (2025).
#----------------------------------------------------------------------------------------------------
# Class for RobotPushingDataset
#----------------------------------------------------------------------------------------------------

import os
import cv2
import torch
import numpy as np
from pathlib import Path
import scipy.io
from .base import BaseUOISDataset
from .utils import (augmentation, blob)
from detectron2.structures import BoxMode
import pycocotools
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


data_loading_params = {
    'img_width': 640,
    'img_height': 480,
    'near': 0.01,
    'far': 100,
    'fov': 45,
    'use_data_augmentation': True,
    'gamma_shape': 1000.,
    'gamma_scale': 0.001,
    'gaussian_scale': 0.005,
    'gp_rescale_factor': 4,
    'ellipse_dropout_mean': 10,
    'ellipse_gamma_shape': 5.0,
    'ellipse_gamma_scale': 1.0,
    'gradient_dropout_left_mean': 15,
    'gradient_dropout_alpha': 2.,
    'gradient_dropout_beta': 5.,
    'pixel_dropout_alpha': 1.,
    'pixel_dropout_beta': 10.,
}

class RobotPushingDataset(BaseUOISDataset):
    def __init__(self, image_set="train", data_path=None, eval=False, config=None):
        super().__init__(image_set, data_path, eval, config)
        self._name = f'robot_pushing_object_{image_set}'
        self._classes = ('__background__', 'foreground')
        self._pixel_mean = torch.tensor(self.cfg['PIXEL_MEANS'] / 255.0).float()
        self.params = data_loading_params
        self.eval = eval
        if image_set == 'train':
            self._data_path = os.path.join(self._data_path, 'training_set')
        elif image_set == 'test':
            self._data_path = os.path.join(self._data_path, 'test_set')
        self.image_paths = self.list_dataset()
        logger.info(f'{len(self.image_paths)} images for dataset {self._name}')
        if not os.path.exists(self._data_path):
            raise FileNotFoundError(f'RobotPushing path does not exist: {self._data_path}')

    def list_dataset(self):
        data_path = Path(self._data_path)
        seqs = sorted(list(data_path.glob('*T*')))
        image_paths = []
        for seq in seqs:
            paths = sorted(list(seq.glob('color*.jpg')))
            image_paths += paths
        return image_paths

    def _get_default_path(self):
        return os.path.join(os.path.expanduser("~"), 'iTeach-UOIS-Data-Collection', 'data', 'robot_pushing')

    def process_label(self, foreground_labels):
        unique_nonnegative_indices = np.unique(foreground_labels)
        mapped_labels = foreground_labels.copy()
        for k, val in enumerate(unique_nonnegative_indices):
            mapped_labels[foreground_labels == val] = k
        return mapped_labels

    def process_label_to_annos(self, labels):
        H, W = labels.shape
        unique_nonnegative_indices = np.unique(labels)
        if unique_nonnegative_indices[0] == 0:
            unique_nonnegative_indices = unique_nonnegative_indices[1:]
        num_instances = unique_nonnegative_indices.shape[0]
        binary_masks = np.zeros((H, W, num_instances), dtype=np.float32)
        for i, label in enumerate(unique_nonnegative_indices):
            binary_masks[..., i] = (labels == label).astype(np.float32)
        boxes = np.zeros((num_instances, 4))
        for i in range(num_instances):
            rows = np.any(binary_masks[..., i], axis=1)
            cols = np.any(binary_masks[..., i], axis=0)
            rmin, rmax = np.where(rows)[0][[0, -1]]
            cmin, cmax = np.where(cols)[0][[0, -1]]
            boxes[i, :] = [cmin, rmin, cmax + 1, rmax + 1]
        labels = unique_nonnegative_indices.clip(1, 2)
        boxes = augmentation.array_to_tensor(boxes)
        binary_masks = augmentation.array_to_tensor(binary_masks)
        labels = augmentation.array_to_tensor(labels).long()
        return boxes, binary_masks, labels

    def compute_xyz(self, depth_img, fx, fy, px, py, height, width):
        indices = np.indices((height, width), dtype=np.float32).transpose(1, 2, 0)
        z_e = depth_img
        x_e = (indices[..., 1] - px) * z_e / fx
        y_e = (indices[..., 0] - py) * z_e / fy
        xyz_img = np.stack([x_e, y_e, z_e], axis=-1)
        return xyz_img

    def process_depth(self, depth_img, meta_data):
        depth_img = (depth_img / meta_data['factor_depth']).astype(np.float32)
        if self.params['use_data_augmentation'] and not self.eval:
            depth_img = augmentation.add_noise_to_depth(depth_img, self.params)
            depth_img = augmentation.dropout_random_ellipses(depth_img, self.params)
        height, width = depth_img.shape
        intrinsics = meta_data['intrinsic_matrix']
        fx, fy, px, py = intrinsics[0, 0], intrinsics[1, 1], intrinsics[0, 2], intrinsics[1, 2]
        xyz_img = self.compute_xyz(depth_img, fx, fy, px, py, height, width)
        if self.params['use_data_augmentation'] and not self.eval:
            xyz_img = augmentation.add_noise_to_xyz(xyz_img, depth_img, self.params)
        return xyz_img

    def pad_crop_resize(self, img, label, depth):
        H, W, _ = img.shape
        K = np.max(label)
        while True:
            idx = np.random.randint(1, K + 1) if K > 0 else 0
            foreground = (label == idx).astype(np.float32)
            rows = np.any(foreground, axis=1)
            cols = np.any(foreground, axis=0)
            if not np.any(rows) or not np.any(cols):
                continue
            y_min, y_max = np.where(rows)[0][[0, -1]]
            x_min, x_max = np.where(cols)[0][[0, -1]]
            cx = (x_min + x_max) / 2
            cy = (y_min + y_max) / 2
            x_delta = x_max - x_min
            y_delta = y_max - y_min
            if x_delta > y_delta:
                y_min = cy - x_delta / 2
                y_max = cy + x_delta / 2
            else:
                x_min = cx - y_delta / 2
                x_max = cx + y_delta / 2
            sidelength = x_max - x_min
            padding_percentage = np.random.uniform(self.cfg['TRAIN']['min_padding_percentage'], self.cfg['TRAIN']['max_padding_percentage'])
            padding = int(round(sidelength * padding_percentage)) or 25
            x_min = max(int(x_min - padding), 0)
            x_max = min(int(x_max + padding), W - 1)
            y_min = max(int(y_min - padding), 0)
            y_max = min(int(y_max + padding), H - 1)
            if y_min == y_max or x_min == x_max:
                continue
            img_crop = img[y_min:y_max + 1, x_min:x_max + 1]
            label_crop = label[y_min:y_max + 1, x_min:x_max + 1]
            depth_crop = depth[y_min:y_max + 1, x_min:x_max + 1] if depth is not None else None
            break
        s = self.cfg['TRAIN']['SYN_CROP_SIZE']
        img_crop = cv2.resize(img_crop, (s, s))
        label_crop = cv2.resize(label_crop, (s, s), interpolation=cv2.INTER_NEAREST)
        depth_crop = cv2.resize(depth_crop, (s, s), interpolation=cv2.INTER_NEAREST) if depth_crop is not None else None
        return img_crop, label_crop, depth_crop

    def sample_pixels(self, labels, num=1000):
        labels_new = -1 * np.ones_like(labels)
        K = np.max(labels)
        for i in range(K + 1):
            index = np.where(labels == i)
            n = len(index[0])
            if n <= num:
                labels_new[index[0], index[1]] = i
            else:
                perm = np.random.permutation(n)
                selected = perm[:num]
                labels_new[index[0][selected], index[1][selected]] = i
        return labels_new

    def __getitem__(self, idx):
        filename = str(self.image_paths[idx])
        im = cv2.imread(filename)
        if im is None:
            logger.error(f"Failed to load image: {filename}")
            raise FileNotFoundError(f"Image not found or invalid: {filename}")

        meta_filename = filename.replace('color', 'meta').replace('.jpg', '.mat')
        try:
            meta_data = scipy.io.loadmat(meta_filename)
        except Exception as e:
            logger.warning(f"Failed to load meta file {meta_filename}: {e}")
            meta_data = {'factor_depth': 1.0, 'intrinsic_matrix': np.eye(3)}

        labels_filename = filename.replace('color', 'label-final').replace('.jpg', '.png')
        foreground_labels = cv2.imread(labels_filename, cv2.IMREAD_GRAYSCALE)
        if foreground_labels is None:
            logger.warning(f"Skipping item {idx} due to missing or invalid mask: {labels_filename}")
            return None

        boxes, binary_masks, labels = self.process_label_to_annos(foreground_labels)
        foreground_labels = self.process_label(foreground_labels)

        xyz_img = None
        if self.cfg['INPUT'] in ['DEPTH', 'RGBD']:
            depth_filename = filename.replace('color', 'depth').replace('.jpg', '.png')
            if os.path.exists(depth_filename):
                depth_img = cv2.imread(depth_filename, cv2.IMREAD_ANYDEPTH).astype(np.float32)
                xyz_img = self.process_depth(depth_img, meta_data)
            else:
                logger.warning(f"Missing depth image: {depth_filename}")
                xyz_img = np.zeros((foreground_labels.shape[0], foreground_labels.shape[1], 3))

        if self.cfg['TRAIN']['SYN_CROP'] and self.cfg['MODE'] == 'TRAIN' and not self.eval:
            im, foreground_labels, xyz_img = self.pad_crop_resize(im, foreground_labels, xyz_img)
            boxes, binary_masks, labels = self.process_label_to_annos(foreground_labels)

        if self.cfg['TRAIN']['EMBEDDING_SAMPLING'] and not self.eval:
            foreground_labels = self.sample_pixels(foreground_labels, self.cfg['TRAIN']['EMBEDDING_SAMPLING_NUM'])

        if self.cfg['TRAIN']['CHROMATIC'] and self.cfg['MODE'] == 'TRAIN' and not self.eval and np.random.rand() > 0.1:
            im = blob.chromatic_transform(im)
        if self.cfg['TRAIN']['ADD_NOISE'] and self.cfg['MODE'] == 'TRAIN' and not self.eval and np.random.rand() > 0.1:
            im = blob.add_noise(im)

        im_tensor = torch.from_numpy(im) / 255.0
        image_blob = im_tensor.permute(2, 0, 1)
        if self.cfg['INPUT'] == 'COLOR':
            image_blob = (torch.from_numpy(im).permute(2, 0, 1) - torch.tensor([123.675, 116.280, 103.530]).view(-1, 1, 1)) / torch.tensor([58.395, 57.120, 57.375]).view(-1, 1, 1)

        record = {
            'image_color': image_blob,
            'file_name': filename,
            'image_id': idx,
            'height': image_blob.shape[1],
            'width': image_blob.shape[2],
            'label': torch.from_numpy(foreground_labels).unsqueeze(0),
        }

        if xyz_img is not None:
            record['depth'] = torch.from_numpy(xyz_img).permute(2, 0, 1)
            record['raw_depth'] = xyz_img

        objs = []
        for box, mask, label in zip(boxes, binary_masks, labels):
            obj = {
                'bbox': box.numpy(),
                'bbox_mode': BoxMode.XYXY_ABS,
                'segmentation': pycocotools.mask.encode(np.asarray(mask.to(torch.uint8), order='F')),
                'category_id': 1,
            }
            objs.append(obj)
        record['annotations'] = objs

        return record