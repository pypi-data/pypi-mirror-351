"""
    Random auxiliary functions.
"""

__all__ = ['init_rand']

import sys


def init_rand(seed: int,
              forced: bool = False) -> int:
    """
    Initialize all random generators by seed.

    Parameters
    ----------
    seed : int
        Seed value.
    forced : bool, default False
        Whether to set seed forcibly.

    Returns
    -------
    int
        Generated seed value.
    """
    if seed < 0:
        import secrets
        seed = secrets.randbelow(2 ** 16)
    if ("random" in sys.modules) or forced:
        import random
        random.seed(seed)
    if ("numpy" in sys.modules) or forced:
        try:
            import numpy as np
            np.random.seed(seed)
        except Exception:
            pass
    if ("torch" in sys.modules) or forced:
        try:
            import torch
            torch.backends.cudnn.deterministic = True
            torch.manual_seed(seed)
        except Exception:
            pass
    return seed
