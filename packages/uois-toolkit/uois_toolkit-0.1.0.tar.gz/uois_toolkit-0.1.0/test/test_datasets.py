# ----------------------------------------------------------------------------------------------------
# Work done while being at the Intelligent Robotics and Vision Lab at the University of Texas, Dallas
# Please check the licenses of the respective works utilized here before using this script.
# 🖋️ Jishnu Jaykumar Padalunkal (2025).
# ----------------------------------------------------------------------------------------------------

# Import required libraries
import numpy as np
from uois_toolkit.core import get_dataset  # Importing dataset loading utility from uois_toolkit

# Define configuration for dataset processing
custom_config = {
    'PIXEL_MEANS': np.array([102.9801, 115.9465, 122.7717]),  # Mean pixel values for RGB normalization
    'TRAIN': {
        'CHROMATIC': False,  # Disable chromatic augmentation
        'ADD_NOISE': False,  # Disable noise addition
        'SYN_CROP': True,  # Enable synthetic cropping
        'SYN_CROP_SIZE': 224,  # Set crop size to 224x224 pixels
        'EMBEDDING_SAMPLING': True,  # Enable embedding sampling
        'EMBEDDING_SAMPLING_NUM': 1000,  # Number of samples for embedding
        'min_pixels': 200,  # Minimum pixel count for objects
        'max_pixels': 10000,  # Maximum pixel count for objects
        'min_padding_percentage': 0.05,  # Minimum padding around objects
        'max_padding_percentage': 0.5,  # Maximum padding around objects
        'CLASSES': (0, 1),  # Binary classification classes
    },
    'INPUT': 'RGBD',  # Input type: RGB + Depth
    'MODE': 'TRAIN',  # Set mode to training
    'FLOW_HEIGHT': 480,  # Height for optical flow or image processing
    'FLOW_WIDTH': 640  # Width for optical flow or image processing
}

# Load iTeach HumanPlay dataset (d5 split) for training
d5 = get_dataset(
    "iteach_humanplay",  # Dataset name
    image_set="train",  # Training split
    data_path="/home/jishnu/iTeach-UOIS-Data-Collection/data/humanplay-d5",  # Path to dataset
    config=custom_config,  # Apply custom configuration
)

# Load iTeach HumanPlay dataset (d40 split) for training
d40 = get_dataset(
    "iteach_humanplay",
    image_set="train",
    data_path="/home/jishnu/iTeach-UOIS-Data-Collection/data/humanplay-d40",
    config=custom_config,
)

# Load iTeach HumanPlay dataset for testing
dtest = get_dataset(
    "iteach_humanplay",
    image_set="test",
    data_path="/home/jishnu/iTeach-UOIS-Data-Collection/data/test_set",
    config=custom_config,
)

# Load OCID dataset for training
ocid_train = get_dataset(
    "ocid",
    image_set="train",
    data_path="/home/jishnu/Projects/iTeach-UOIS/DATA/OCID-dataset",
    config=custom_config,
)

# Load OCID dataset for testing
ocid_test = get_dataset(
    "ocid",
    image_set="test",
    data_path="/home/jishnu/Projects/iTeach-UOIS/DATA/OCID-dataset",
    config=custom_config,
)

# Load Tabletop dataset for training
tabletop = get_dataset(
    "tabletop",
    image_set="train",
    data_path="/home/jishnu/Projects/iTeach-UOIS/DATA/tabletop",
    config=custom_config,
)

# Load Tabletop dataset for testing
tabletop_test = get_dataset(
    "tabletop",
    image_set="test",
    data_path="/home/jishnu/Projects/iTeach-UOIS/DATA/tabletop",
    config=custom_config,
)

# Load Robot Pushing dataset for training
rpushing_train = get_dataset(
    "robot_pushing",
    image_set="train",
    data_path="/home/jishnu/Projects/iTeach-UOIS/DATA/pushing_data",
    config=custom_config,
)

# Load Robot Pushing dataset for testing
rpushing = get_dataset(
    "robot_pushing",
    image_set="test",
    data_path="/home/jishnu/Projects/iTeach-UOIS/DATA/pushing_data",
    config=custom_config,
)

# Load OSD dataset for training
osd = get_dataset(
    "osd",
    image_set="train",
    data_path="/home/jishnu/Projects/iTeach-UOIS/DATA/OSD",
    config=custom_config,
)

# Load OSD dataset for testing
# Note: This overwrites the previous 'osd' variable; consider renaming to avoid confusion
osd = get_dataset(
    "osd",
    image_set="test",
    data_path="/home/jishnu/Projects/iTeach-UOIS/DATA/OSD",
    config=custom_config,
)