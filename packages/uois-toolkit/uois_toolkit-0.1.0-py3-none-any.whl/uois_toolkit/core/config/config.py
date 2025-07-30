#----------------------------------------------------------------------------------------------------
# Work done while being at the Intelligent Robotics and Vision Lab at the University of Texas, Dallas
# Please check the licenses of the respective works utilized here before using this script.
# 🖋️ Jishnu Jaykumar Padalunkal (2025).
#----------------------------------------------------------------------------------------------------
# Config for UOIS Datasets
#----------------------------------------------------------------------------------------------------

import numpy as np

import numpy as np

config = {
    'PIXEL_MEANS': np.array([102.9801, 115.9465, 122.7717]),  # BGR
    'INPUT': 'RGBD',
    'MODE': 'TRAIN',
    'FLOW_HEIGHT': 480,
    'FLOW_WIDTH': 640,
    'TRAIN': {
        'CHROMATIC': True,
        'ADD_NOISE': True,
        'SYN_CROP': True,
        'SYN_CROP_SIZE': 224,
        'EMBEDDING_SAMPLING': True,
        'EMBEDDING_SAMPLING_NUM': 1000,
        'min_pixels': 200,
        'max_pixels': 10000,
        'min_padding_percentage': 0.05,
        'max_padding_percentage': 0.5,
        'CLASSES': (0, 1),
    }
}