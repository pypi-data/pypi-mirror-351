import numpy as np

def mask_to_tight_box(mask):
    a = np.transpose(np.nonzero(mask))
    if len(a) == 0:
        return 0, 0, 0, 0
    return np.min(a[:, 1]), np.min(a[:, 0]), np.max(a[:, 1]), np.max(a[:, 0])