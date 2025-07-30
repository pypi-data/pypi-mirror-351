#----------------------------------------------------------------------------------------------------
# Work done while being at the Intelligent Robotics and Vision Lab at the University of Texas, Dallas
# Please check the licenses of the respective works utilized here before using this script.
# 🖋️ Jishnu Jaykumar Padalunkal (2025).
#----------------------------------------------------------------------------------------------------
# Base class for UOIS datasets
# This class provides a common interface and basic functionality for UOIS datasets.
# It handles image loading, data augmentation, and annotation processing.
#----------------------------------------------------------------------------------------------------

import os
import cv2
import torch
import numpy as np
import pycocotools
from pathlib import Path
from ..config import cfg
from .utils import (augmentation, blob)
from ..utils.seed import set_seeds
from torchvision import transforms
from detectron2.structures import BoxMode
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseUOISDataset(torch.utils.data.Dataset):
    def __init__(self, image_set="train", data_path=None, eval=False, config=None):
        set_seeds(seed=1)  # Set seed for reproducibility
        self._name = f"{self.__class__.__name__.lower()}_{image_set}"
        self._image_set = image_set
        self._data_path = self._get_default_path() if data_path is None else data_path
        self._classes_all = ("__background__", "foreground")
        self._classes = self._classes_all
        self.cfg = config if config is not None else cfg
        self._pixel_mean = torch.tensor(self.cfg["PIXEL_MEANS"] / 255.0).float()
        self.eval = eval
        self.params = {
            "img_width": 640,
            "img_height": 480,
            "near": 0.01,
            "far": 100,
            "fov": 45,
            "use_data_augmentation": self.cfg["TRAIN"]["CHROMATIC"]
            or self.cfg["TRAIN"]["ADD_NOISE"],
        }

        self.image_paths = self.list_dataset()
        self._size = len(self.image_paths)

        if not os.path.exists(self._data_path):
            raise FileNotFoundError(f"Data path does not exist: {self._data_path}")

    def list_dataset(self):
        raise NotImplementedError("Subclasses must implement list_dataset")

    def _get_default_path(self):
        raise NotImplementedError("Subclasses must implement _get_default_path")

    def process_label_to_annos(self, foreground_labels):
        if foreground_labels is None:
            logger.error("Foreground labels are None, cannot process annotations")
            return (
                np.zeros((0, 4)),
                np.zeros((0, 0, 0), dtype=np.float32),
                np.zeros(0, dtype=np.int64),
            )

        unique_labels = np.unique(foreground_labels)
        if unique_labels[0] == 0:
            unique_labels = unique_labels[1:]
        num_instances = len(unique_labels)
        binary_masks = np.zeros(
            (foreground_labels.shape[0], foreground_labels.shape[1], num_instances),
            dtype=np.float32,
        )
        boxes = np.zeros((num_instances, 4))
        for i, label in enumerate(unique_labels):
            binary_masks[..., i] = (foreground_labels == label).astype(np.float32)
            boxes[i, :] = np.array(util_.mask_to_tight_box(binary_masks[..., i]))
        labels = np.ones(num_instances, dtype=np.int64)
        return boxes, binary_masks, labels

    def __getitem__(self, idx):
        filename = str(self.image_paths[idx])
        im = cv2.imread(filename)
        if im is None:
            logger.error(f"Failed to load image: {filename}")
            raise FileNotFoundError(f"Image not found or invalid: {filename}")

        labels_filename = filename.replace("rgb", "gt_masks").replace(".png", ".png")
        foreground_labels = cv2.imread(labels_filename, cv2.IMREAD_GRAYSCALE)
        if foreground_labels is None:
            logger.warning(
                f"Failed to load mask: {labels_filename}, returning empty annotations"
            )

        # Process image
        if self.params["use_data_augmentation"] and not self.eval:
            if self.cfg["TRAIN"]["CHROMATIC"]:
                im = blob.chromatic_transform(im)
            if self.cfg["TRAIN"]["ADD_NOISE"]:
                im = blob.add_noise(im)
        im = torch.from_numpy(im).permute(2, 0, 1)

        # Process labels
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

    def __len__(self):
        return self._size
