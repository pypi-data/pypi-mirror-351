"""LR finder that branches from a base training run for a range of learning 
rates.

The training process is:
    1. Train a model with an initial learning rate fully. Fully here means until
    the provided number of steps is reached, or the provided early stopping is
    triggered. 
        - Training is done with a constant learning rate.
        - There are regularly spaced checkpoints (future feature: evaluate
            using the validation dataset).
    2. At regular intervals of the checkpoints, for a short number of steps,
    train the model with a range of learning rates.
    3. Record all loss "branches" and return this data.

The choice is made by taking in this data and choosing the highest learning
rate that at some point was the most beneficial.
"""
import kddl
import kddl.train as train
import polars as pl
import math
import logging
from typing import Tuple, Optional, Sequence, List
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
import scipy.stats
import itertools

_logger = logging.getLogger(__name__)


