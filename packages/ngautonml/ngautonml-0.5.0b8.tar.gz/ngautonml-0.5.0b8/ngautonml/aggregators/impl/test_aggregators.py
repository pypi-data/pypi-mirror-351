'''Aggregators for testing purposes'''
from typing import Tuple

import numpy as np


def identity(ranks: np.ndarray,
             reverse: bool = False,
             fail: bool = False) -> Tuple[float, np.ndarray]:
    '''Returns the identity or reversed rank of the first ranking'''
    ranking = ranks[0]
    if fail:
        raise ValueError('intentional failure')
    if reverse:
        return 0., np.flip(ranking)
    return 0., ranking
