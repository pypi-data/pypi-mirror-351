"""
    Random auxiliary functions.
"""

__all__ = ['init_rand']

import os
import sys
import logging


def init_rand(seed: int,
              forced: bool = False,
              hard: bool = False) -> int:
    """
    Initialize all random generators by seed.

    Parameters
    ----------
    seed : int
        Seed value.
    forced : bool, default False
        Whether to set seed forcibly.
    hard : bool, default False
        Whether to use hard way.

    Returns
    -------
    int
        Generated seed value.
    """
    if seed < 0:
        import secrets
        seed = secrets.randbelow(2 ** 16)
    if not os.environ.get("PYTHONHASHSEED"):
        logging.warning("Set PYTHONHASHSEED={}!".format(seed))
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
            if hard:
                os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
            import torch
            torch.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
            if hard:
                torch.use_deterministic_algorithms(True)
        except Exception:
            pass
    return seed
