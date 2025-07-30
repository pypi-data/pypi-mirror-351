#----------------------------------------------------------------------------------------------------
# Work done while being at the Intelligent Robotics and Vision Lab at the University of Texas, Dallas
# Please check the licenses of the respective works utilized here before using this script.
# 🖋️ Jishnu Jaykumar Padalunkal (2025).
#----------------------------------------------------------------------------------------------------

import numpy as np
import torch
import cv2
import scipy.stats

def add_noise_to_depth(depth_img, params):
    """ Add noise to depth image
        @param depth_img: a [H x W] numpy array
        @param params: a dictionary containing noise parameters
    """
    # Multiplicative noise
    shape = depth_img.shape
    gamma_shape = params.get('gamma_shape', 1000.)
    gamma_scale = params.get('gamma_scale', 0.001)
    multiplicative_noise = np.random.gamma(shape=gamma_shape, scale=gamma_scale, size=shape)
    depth_img = depth_img * multiplicative_noise

    # Additive noise
    gaussian_scale = params.get('gaussian_scale', 0.005)
    gaussian_noise = np.random.normal(loc=0, scale=gaussian_scale, size=shape)
    depth_img = depth_img + gaussian_noise

    # Gaussian process noise
    gp_rescale_factor = params.get('gp_rescale_factor', 4)
    H, W = shape
    Hs, Ws = H // gp_rescale_factor, W // gp_rescale_factor
    gp_noise = np.random.normal(loc=0, scale=gaussian_scale, size=(Hs, Ws))
    gp_noise = cv2.resize(gp_noise, (W, H), interpolation=cv2.INTER_CUBIC)
    depth_img = depth_img + gp_noise

    return depth_img

def dropout_random_ellipses(depth_img, params):
    """ Randomly drop out ellipse-shaped regions
        @param depth_img: a [H x W] numpy array
        @param params: a dictionary containing dropout parameters
    """
    dropout_depth_img = depth_img.copy()
    H, W = dropout_depth_img.shape
    num_ellipses = int(np.random.poisson(lam=params.get('ellipse_dropout_mean', 10)))

    for _ in range(num_ellipses):
        # Sample center
        center_x = np.random.randint(0, W)
        center_y = np.random.randint(0, H)

        # Sample axes
        a = np.random.gamma(params.get('ellipse_gamma_shape', 5.0), params.get('ellipse_gamma_scale', 1.0))
        b = np.random.gamma(params.get('ellipse_gamma_shape', 5.0), params.get('ellipse_gamma_scale', 1.0))

        # Sample angle
        theta = np.random.uniform(0, 2 * np.pi)

        # Create ellipse mask
        y, x = np.ogrid[:H, :W]
        x = x - center_x
        y = y - center_y
        ellipse_mask = ((x * np.cos(theta) + y * np.sin(theta)) / a) ** 2 + ((x * np.sin(theta) - y * np.cos(theta)) / b) ** 2 <= 1

        # Apply dropout
        dropout_depth_img[ellipse_mask] = 0

    return dropout_depth_img

def add_noise_to_xyz(xyz_img, depth_img, params):
    """ Add noise to XYZ point cloud
        @param xyz_img: a [H x W x 3] numpy array
        @param depth_img: a [H x W] numpy array (for valid mask)
        @param params: a dictionary containing noise parameters
    """
    gaussian_scale = params.get('gaussian_scale', 0.005)
    shape = xyz_img.shape
    valid_mask = depth_img > 0
    gaussian_noise = np.random.normal(loc=0, scale=gaussian_scale, size=shape)
    gaussian_noise[~valid_mask] = 0
    xyz_img = xyz_img + gaussian_noise

    # Gaussian process noise
    gp_rescale_factor = params.get('gp_rescale_factor', 4)
    H, W, _ = shape
    Hs, Ws = H // gp_rescale_factor, W // gp_rescale_factor
    gp_noise = np.random.normal(loc=0, scale=gaussian_scale, size=(Hs, Ws, 3))
    gp_noise = cv2.resize(gp_noise, (W, H), interpolation=cv2.INTER_CUBIC)
    gp_noise[~valid_mask] = 0
    xyz_img = xyz_img + gp_noise

    return xyz_img

def array_to_tensor(array):
    """ Convert numpy array to pytorch tensor
        @param array: a numpy array
        @return: a pytorch tensor
    """
    return torch.from_numpy(array)