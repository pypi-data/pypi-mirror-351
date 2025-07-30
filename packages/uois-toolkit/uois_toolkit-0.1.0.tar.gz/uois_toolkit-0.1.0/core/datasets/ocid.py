#----------------------------------------------------------------------------------------------------
# Work done while being at the Intelligent Robotics and Vision Lab at the University of Texas, Dallas
# Please check the licenses of the respective works utilized here before using this script.
# 🖋️ Jishnu Jaykumar Padalunkal (2025).
#----------------------------------------------------------------------------------------------------
# Class for OCIDDataset
#----------------------------------------------------------------------------------------------------


import os
import cv2
import torch
import numpy as np
from pathlib import Path
from .base import BaseUOISDataset
from .utils import (augmentation, blob)
import open3d
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OCIDDataset(BaseUOISDataset):
    def __init__(self, image_set="train", data_path=None, eval=False, config=None):
        super().__init__(image_set, data_path, eval, config)
        self._name = f'ocid_object_{image_set}'
        self._classes = ('__background__', 'foreground')
        self._pixel_mean = torch.tensor(self.cfg['PIXEL_MEANS'] / 255.0).float()
        self._width = 640
        self._height = 480
        self.image_paths = self.list_dataset()
        logger.info(f'{len(self.image_paths)} images for dataset {self._name}')
        self.max_num_object = 0
        if not os.path.exists(self._data_path):
            raise FileNotFoundError(f'OCID path does not exist: {self._data_path}')

    def list_dataset(self):
        data_path = Path(self._data_path)
        seqs = sorted(list(data_path.glob('**/*seq*')))
        image_paths = []
        for seq in seqs:
            paths = sorted(list((seq / 'rgb').glob('*.png')))
            image_paths += paths
        return image_paths

    def _get_default_path(self):
        return os.path.join(os.path.expanduser("~"), 'Projects', 'iTeach-UOIS', 'OCID')

    def process_label(self, foreground_labels):
        unique_nonnegative_indices = np.unique(foreground_labels)
        object_num = unique_nonnegative_indices.shape[0] - 1
        if object_num > self.max_num_object:
            self.max_num_object = object_num
        mapped_labels = foreground_labels.copy()
        for k, val in enumerate(unique_nonnegative_indices):
            mapped_labels[foreground_labels == val] = k
        return mapped_labels

    def __getitem__(self, idx):
        filename = str(self.image_paths[idx])
        im = cv2.imread(filename)
        if im is None:
            logger.error(f"Failed to load image: {filename}")
            raise FileNotFoundError(f"Image not found or invalid: {filename}")

        im_tensor = torch.from_numpy(im) / 255.0
        im_tensor_bgr = im_tensor.clone().permute(2, 0, 1)
        im_tensor -= self._pixel_mean
        image_blob = im_tensor.permute(2, 0, 1)

        labels_filename = filename.replace('rgb', 'label')
        foreground_labels = cv2.imread(labels_filename, cv2.IMREAD_GRAYSCALE)
        if foreground_labels is None:
            logger.warning(f"Skipping item {idx} due to missing or invalid mask: {labels_filename}")
            return None

        foreground_labels[foreground_labels == 1] = 0  # Table as background
        if 'table' in labels_filename:
            foreground_labels[foreground_labels == 2] = 0
        foreground_labels = self.process_label(foreground_labels)
        label_blob = torch.from_numpy(foreground_labels).unsqueeze(0)

        if self.cfg['INPUT'] == 'COLOR':
            image_blob = (torch.from_numpy(im).permute(2, 0, 1) - torch.tensor([123.675, 116.280, 103.530]).view(-1, 1, 1)) / torch.tensor([58.395, 57.120, 57.375]).view(-1, 1, 1)

        sample = {
            'image_color': image_blob,
            'image_color_bgr': im_tensor_bgr,
            'label': label_blob,
            'filename': filename[filename.find('OCID') + 5:],
            'file_name': filename,
            'image_id': idx,
            'height': self._height,
            'width': self._width,
        }

        pcd_filename = filename.replace('rgb', 'pcd').replace('.png', '.pcd')
        if os.path.exists(pcd_filename):
            try:
                pcd = open3d.io.read_point_cloud(pcd_filename)
                pcloud = np.asarray(pcd.points).astype(np.float32)
                pcloud[np.isnan(pcloud)] = 0
                xyz_img = pcloud.reshape((self._height, self._width, 3))
                depth_blob = torch.from_numpy(xyz_img).permute(2, 0, 1)
                sample['depth'] = depth_blob
                sample['raw_depth'] = xyz_img
            except Exception as e:
                logger.warning(f"Failed to load PCD file {pcd_filename}: {e}")
                sample['depth'] = torch.zeros((3, self._height, self._width))
                sample['raw_depth'] = np.zeros((self._height, self._width, 3))

        return sample