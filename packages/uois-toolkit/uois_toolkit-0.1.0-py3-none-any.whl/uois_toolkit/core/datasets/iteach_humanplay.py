#----------------------------------------------------------------------------------------------------
# Work done while being at the Intelligent Robotics and Vision Lab at the University of Texas, Dallas
# Please check the licenses of the respective works utilized here before using this script.
# 🖋️ Jishnu Jaykumar Padalunkal (2025).
#----------------------------------------------------------------------------------------------------
# Class for iTeachHumanPlayDataset
#----------------------------------------------------------------------------------------------------

import os
import cv2
import torch
import numpy as np
from pathlib import Path
from .base import BaseUOISDataset
from .utils import augmentation
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class iTeachHumanPlayDataset(BaseUOISDataset):
    def __init__(self, image_set="train", data_path=None, eval=False, config=None):
        super().__init__(image_set, data_path, eval, config)
        self._name = f'iteach_humanplay_object_{image_set}'
        self.data_loading_params = {
            "img_width": 640,
            "img_height": 480,
            "near": 0.01,
            "far": 100,
            "fov": 45,
            "use_data_augmentation": self.cfg["TRAIN"]["CHROMATIC"]
            or self.cfg["TRAIN"]["ADD_NOISE"],
            "gamma_shape": 1000.0,
            "gamma_scale": 0.001,
            "gaussian_scale": 0.005,
            "gp_rescale_factor": 4,
            "ellipse_dropout_mean": 10,
            "ellipse_gamma_shape": 5.0,
            "ellipse_gamma_scale": 1.0,
        }
        self.image_paths = self.list_dataset()
        logger.info(f'{len(self.image_paths)} images for dataset {self._name}')


    def list_dataset(self):
        data_path = Path(self._data_path)
        seqs = sorted(list(data_path.glob("scene*")))
        image_paths = []
        for seq in seqs:
            paths = sorted(list(seq.glob("rgb/*.png")))
            image_paths += paths
        return image_paths

    def _get_default_path(self):
        return os.path.join(os.path.expanduser("~"), "data", "iteach_humanplay_data")

    def process_depth(self, depth, color):
        depth = np.expand_dims(depth, 2)
        if self.data_loading_params["use_data_augmentation"] and not self.eval:
            depth = augmentation.add_noise_to_depth(depth, self.data_loading_params)
            depth = augmentation.dropout_random_ellipses(
                depth, self.data_loading_params
            )
        depth = augmentation.array_to_tensor(depth)
        depth = depth.squeeze()

        # Convert to XYZ using K of IRVLUTD fetch robot after ft sensor installation-calibration (as of May 29 2025)
        fx = 527.8869068647631
        fy = 524.7942507494529
        cx = 230.2819198622499
        cy = self.data_loading_params["img_height"] / 2
        h, w = depth.shape
        x = torch.arange(w, dtype=torch.float32).unsqueeze(0).repeat(h, 1)
        y = torch.arange(h, dtype=torch.float32).unsqueeze(1).repeat(1, w)
        xx = (x - cx) * depth / fx
        yy = (y - cy) * depth / fy
        xyz = torch.stack([xx, yy, depth], dim=2)
        if self.data_loading_params["use_data_augmentation"] and not self.eval:
            xyz = augmentation.add_noise_to_xyz(xyz, depth, self.data_loading_params)
        return depth, xyz

    def __getitem__(self, idx):
        filename = str(self.image_paths[idx])
        im = cv2.imread(filename)
        depth_filename = filename.replace("rgb", "depth")
        depth = cv2.imread(depth_filename, cv2.IMREAD_GRAYSCALE)
        labels_filename = filename.replace("rgb", "gt_masks")
        foreground_labels = cv2.imread(labels_filename, cv2.IMREAD_GRAYSCALE)

        # Process image
        if self.data_loading_params["use_data_augmentation"] and not self.eval:
            if self.cfg["TRAIN"]["CHROMATIC"]:
                im = blob.chromatic_transform(im)
            if self.cfg["TRAIN"]["ADD_NOISE"]:
                im = blob.add_noise(im)
        im = torch.from_numpy(im).permute(2, 0, 1)

        # Process depth
        depth, xyz = self.process_depth(depth, im)

        # Process labels
        boxes, binary_masks, labels = self.process_label_to_annos(foreground_labels)
        boxes = augmentation.array_to_tensor(boxes)
        binary_masks = augmentation.array_to_tensor(binary_masks)
        labels = augmentation.array_to_tensor(labels).long()

        record = {
            "file_name": filename,
            "image_id": idx,
            "image_color": im,
            "height": im.shape[1],
            "width": im.shape[2],
            "depth": depth,
            "xyz": xyz,
        }
        objs = []
        for box, mask, label in zip(boxes, binary_masks, labels):
            obj = {
                "bbox": box.numpy(),
                "bbox_mode": BoxMode.XYXY_ABS,
                "segmentation": pycocotools.mask.encode(
                    np.asarray(mask.to(torch.uint8), order="F")
                ),
                "category_id": 1,
            }
            objs.append(obj)
        record["annotations"] = objs
        return record
