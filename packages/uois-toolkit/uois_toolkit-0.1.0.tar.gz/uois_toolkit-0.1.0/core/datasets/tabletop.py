#----------------------------------------------------------------------------------------------------
# Work done while being at the Intelligent Robotics and Vision Lab at the University of Texas, Dallas
# Please check the licenses of the respective works utilized here before using this script.
# 🖋️ Jishnu Jaykumar Padalunkal (2025).
#----------------------------------------------------------------------------------------------------
# Class for TabletopObjectDataset
#----------------------------------------------------------------------------------------------------


import os
import cv2
import torch
import numpy as np
from pathlib import Path
from .base import BaseUOISDataset
from .utils import (augmentation, blob)
from detectron2.structures import BoxMode
import pycocotools
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TabletopDataset(BaseUOISDataset):
    BACKGROUND_LABEL = 0
    TABLE_LABEL = 1
    OBJECTS_LABEL = 2  # TODv5; set to 4 for TODv6

    def __init__(self, image_set="train", data_path=None, eval=False, config=None):
        super().__init__(image_set, data_path, eval, config)
        self._name = f'tabletop_object_{image_set}'
        self.data_loading_params = {
            'img_width': self.cfg['FLOW_WIDTH'],
            'img_height': self.cfg['FLOW_HEIGHT'],
            'near': 0.01,
            'far': 100,
            'fov': 45,
            'use_data_augmentation': self.cfg['TRAIN']['CHROMATIC'] or self.cfg['TRAIN']['ADD_NOISE'],
            'min_pixels': 200,
            'max_pixels': 10000,
        }
        if image_set == 'train':
            self._data_path = os.path.join(self._data_path, 'training_set')
        elif image_set == 'test':
            self._data_path = os.path.join(self._data_path, 'test_set')
        
        self.image_paths = self.list_dataset()
        logger.info(f'{len(self.image_paths)} images for dataset {self._name}')

    def list_dataset(self):
        data_path = Path(self._data_path)
        seqs = sorted(list(data_path.glob('scene_*')))
        image_paths = []
        for seq in seqs:
            paths = sorted(list(seq.glob('rgb_*.jpeg')))
            image_paths += paths
        return image_paths

    def _get_default_path(self):
        return os.path.join(os.path.expanduser("~"), 'iTeach-UOIS-Data-Collection', 'data', 'tabletop')

    def process_depth(self, depth, color):
        if depth is None:
            logger.warning("Depth image is None, returning zero tensors")
            return torch.zeros((self.data_loading_params['img_height'], self.data_loading_params['img_width'])), torch.zeros((self.data_loading_params['img_height'], self.data_loading_params['img_width'], 3))

        depth = np.expand_dims(depth, 2).astype(np.float32) / 1000.0  # mm to meters
        if self.data_loading_params['use_data_augmentation'] and not self.eval:
            depth = augmentation.add_noise_to_depth(depth, self.data_loading_params)
            depth = augmentation.dropout_random_ellipses(depth, self.data_loading_params)
        depth = augmentation.array_to_tensor(depth)
        depth = depth.squeeze()

        fx = self.data_loading_params['img_width'] / (2 * np.tan(self.data_loading_params['fov'] * np.pi / 360))
        fy = fx
        cx = self.data_loading_params['img_width'] / 2
        cy = self.data_loading_params['img_height'] / 2
        h, w = depth.shape
        x = torch.arange(w, dtype=torch.float32).unsqueeze(0).repeat(h, 1)
        y = torch.arange(h, dtype=torch.float32).unsqueeze(1).repeat(1, w)
        xx = (x - cx) * depth / fx
        yy = (y - cy) * depth / fy
        xyz = torch.stack([xx, yy, depth], dim=2)
        if self.data_loading_params['use_data_augmentation'] and not self.eval:
            xyz = augmentation.add_noise_to_xyz(xyz, depth, self.data_loading_params)
        return depth, xyz

    def process_label_to_annos(self, foreground_labels):
        if foreground_labels is None:
            logger.error("Foreground labels are None, returning empty annotations")
            return np.zeros((0, 4)), np.zeros((0, foreground_labels.shape[0], foreground_labels.shape[1]), dtype=np.float32), np.zeros(0, dtype=np.int64)

        object_mask = (foreground_labels >= self.OBJECTS_LABEL)
        unique_labels = np.unique(foreground_labels[object_mask])
        if len(unique_labels) == 0:
            return np.zeros((0, 4)), np.zeros((0, foreground_labels.shape[0], foreground_labels.shape[1]), dtype=np.float32), np.zeros(0, dtype=np.int64)

        num_instances = 0
        binary_masks = []
        boxes = []
        for label in unique_labels:
            mask = (foreground_labels == label).astype(np.float32)
            pixel_count = np.sum(mask)
            if self.data_loading_params['min_pixels'] <= pixel_count <= self.data_loading_params['max_pixels']:
                binary_masks.append(mask)
                box = self._mask_to_tight_box(mask)
                boxes.append(box)
                num_instances += 1

        if num_instances == 0:
            return np.zeros((0, 4)), np.zeros((0, foreground_labels.shape[0], foreground_labels.shape[1]), dtype=np.float32), np.zeros(0, dtype=np.int64)

        binary_masks = np.stack(binary_masks, axis=2)
        boxes = np.array(boxes)
        labels = np.ones(num_instances, dtype=np.int64)
        return boxes, binary_masks, labels

    def _mask_to_tight_box(self, mask):
        rows = np.any(mask, axis=1)
        cols = np.any(mask, axis=0)
        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]
        return [cmin, rmin, cmax + 1, rmax + 1]  # [x1, y1, x2, y2]

    def __getitem__(self, idx):
        filename = str(self.image_paths[idx])
        im = cv2.imread(filename)
        if im is None:
            logger.error(f"Failed to load image: {filename}")
            raise FileNotFoundError(f"Image not found or invalid: {filename}")

        depth_filename = filename.replace('rgb_', 'depth_').replace('.jpeg', '.png')
        depth = cv2.imread(depth_filename, cv2.IMREAD_GRAYSCALE)
        if depth is None:
            logger.warning(f"Missing depth image: {depth_filename}")

        labels_filename = filename.replace('rgb_', 'segmentation_').replace('.jpeg', '.png')
        foreground_labels = cv2.imread(labels_filename, cv2.IMREAD_GRAYSCALE)
        if foreground_labels is None:
            logger.warning(f"Skipping item {idx} due to missing or invalid mask: {labels_filename}")
            return None

        if self.data_loading_params['use_data_augmentation'] and not self.eval:
            if self.cfg['TRAIN']['CHROMATIC']:
                im = blob.chromatic_transform(im)
            if self.cfg['TRAIN']['ADD_NOISE']:
                im = blob.add_noise(im)
        im = torch.from_numpy(im).permute(2, 0, 1)

        depth, xyz = self.process_depth(depth, im) if depth is not None else (torch.zeros_like(im[0]), torch.zeros((im.shape[1], im.shape[2], 3)))

        boxes, binary_masks, labels = self.process_label_to_annos(foreground_labels)
        boxes = torch.from_numpy(boxes)
        binary_masks = torch.from_numpy(binary_masks)
        labels = torch.from_numpy(labels).long()

        record = {
            "file_name": filename,
            "image_id": idx,
            "image_color": im,
            "height": im.shape[1],
            "width": im.shape[2],
            "depth": depth,
            "xyz": xyz
        }
        objs = []
        for box, mask, label in zip(boxes, binary_masks, labels):
            obj = {
                "bbox": box.numpy(),
                "bbox_mode": BoxMode.XYXY_ABS,
                "segmentation": pycocotools.mask.encode(np.asarray(mask.to(torch.uint8), order="F")),
                "category_id": 1,
            }
            objs.append(obj)
        record["annotations"] = objs
        return record