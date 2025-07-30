#----------------------------------------------------------------------------------------------------
# Work done while being at the Intelligent Robotics and Vision Lab at the University of Texas, Dallas
# Please check the licenses of the respective works utilized here before using this script.
# 🖋️ Jishnu Jaykumar Padalunkal (2025).
#----------------------------------------------------------------------------------------------------

import torch
import numpy as np
import random
import logging

logger = logging.getLogger(__name__)

def set_seeds(seed=1):
    """
    Set random seeds for Python, NumPy, and PyTorch for reproducibility.
    
    Args:
        seed (int): Seed value, default is 1.
    """
    logger.info(f"Setting random seeds to {seed}")
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    logger.debug("Seeds set: Python=%d, NumPy=%d, PyTorch=%d", seed, seed, seed)