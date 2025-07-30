import math
import torch
import bisect
import numpy as np
from numpy.typing import ArrayLike
from typing import Sequence, Literal, Tuple
import logging
import itertools
import deprecated

_logger = logging.getLogger(__name__)


"""
Useful methods:

Convert 1D array to a 2D "rolling-window" matrix:
lib.stride_tricks.sliding_window_view(x, window_shape, ...)
"""


def estimate_batch_size(sample):
    """Estimate the batch size of a sample."""
    if isinstance(sample, (list, tuple)):
        return len(sample[0])
    elif isinstance(sample, dict):
        return len(next(iter(sample.values())))
    else:
        raise ValueError(f"Unknown sample type. {type(sample)}")


def constrained_iter(iter, max_n=None, len_fn=estimate_batch_size):
    """Enumerate a batched iterable up to max_n samples."""

    max_n = max_n or math.inf
    n = 0
    for sample in iter:
        n += len_fn(sample)
        yield sample
        if n >= max_n:
            break


class ConstrainedIterable:
    """An iteratable limited by number of samples, which are batched.

    The number of samples can be at most max_n + batch_size - 1.
    """

    def __init__(self, iterable, max_n, len_fn=estimate_batch_size):
        self.iterable = iterable
        self.max_n = max_n
        self.len_fn = len_fn

    def __iter__(self):
        return constrained_iter(iter(self.iterable), self.max_n, self.len_fn)

    def __getattr__(self, name):
        """Pass other function calls to the underlying iterable."""
        return getattr(self.iterable, name)


def split_seq1d(seq: ArrayLike, ratios: ArrayLike, interval_len: int):
    """Split an index sequence by splitting [0, t_max] by a given ratio.

    A sequence like [3, 10, 15, 16] that points into a time interval [0, 20]
    would be split into [[3], [10], [15, 16]] with ratios [1, 1, 1].

    [0, 1, 2, 3, 4, 5, 6, 7], [8, 9, 10, 11, 12, 13], [14, 15, 16, 17, 18, 19]

    Args:
        seq: sequence of indices, such as [0, 25, 54, 100]
        ratios: list of ratios for splitting the sequence
        interval_len: the length of the time interval
    """
    ratios = np.array(ratios)
    if len(ratios.shape) != 1:
        raise ValueError("ratios must be a 1D array.")
    boundaries = split_borders(ratios, interval_len)
    seqs = np.split(seq, np.searchsorted(seq, boundaries))
    return seqs


def split_seq(seq, ratios, interval_len, key=lambda x: x):
    """Split an index sequence by splitting [0, t_max] by a given ratio.

    The input list is assumed (not checked) to be sorted.

    This generalizes split_seq1d to work with any list of objects.

    Args:
        seq: sequence of indices, such as [0, 25, 54, 100]
        ratios: list of ratios for splitting the sequence
        interval_len: the length of the time interval
        key: function to extract the value to compare for sorting
    """
    borders = split_borders(ratios, interval_len)
    lo = 0
    res = []
    for b in borders:
        i = bisect.bisect_left(seq, b, lo, key=key)
        res.append(seq[lo:i])
        lo = i
    res.append(seq[lo:])
    return res


def split_borders(ratios: ArrayLike, len: int):
    """
    Calculates the inner borders to split an array by the given ratios.

    Example:

        split_borders((5, 3, 2), 10) -> (5, 8)

    This corresponds to the following splits:

        [0, 1, 2, 3, 4], [5, 6, 7], [8, 9]
         0  1  2  3  4    5  6  7    8  9
                          ^          ^

    Note that (5, 3, 2) are ratios, not the array data. The array data is
    not needed and isn't an argument to this function.
    """
    ratios = np.array(ratios) / np.gcd.reduce(ratios)
    n_divisions = np.sum(ratios)
    if n_divisions > len:
        raise ValueError(
            "The sum of ratios must be less than or equal to the "
            f"length. ({n_divisions} > {len})"
        )
    num_per_division, remainder = divmod(len, n_divisions)
    borders = np.cumsum(ratios * num_per_division) + remainder
    assert borders[-1] == len
    res = borders[:-1].astype(int).tolist()
    return res


def split(arr, ratios):
    """
    Splits an array along the first axis by the given ratios.

    Remaining elements are given to the first split.
    """
    splits = np.split(arr, split_borders(ratios, len(arr)))
    return splits


def split2(data: Sequence, split_ratio: Sequence[int]):
    """
    Splits a sequence by the given ratios.

    This is a non-numpy alternative to split() above.
    """
    divisions = sum(split_ratio)
    if divisions > len(data):
        raise ValueError(
            "The sum of ratios must be less than or equal to the length. "
            f"({divisions} > {len})"
        )
    num_per_division, remainder = divmod(len(data), divisions)
    num_per_split = [num_per_division * ratio for ratio in split_ratio]
    # Give the extra samples to the first split
    num_per_split[0] += remainder
    split_starts = itertools.accumulate([0] + num_per_split)
    splits = [data[s:e] for s, e in itertools.pairwise(split_starts)]
    assert sum(len(s) for s in splits) == len(data)
    return splits


def decompress_seq(seq, t_max, downsample_factor=1):
    seq_ds = np.floor_divide(seq, downsample_factor)
    res = np.zeros(shape=[math.ceil(t_max / downsample_factor)], dtype=int)
    # Allow for multiple events at the same time, which can happen either due
    # to the original sequence having concurrent events or due to downsampling
    # placing multiple events in the same bin.
    np.add.at(res, seq_ds, 1)
    return res


# Switch to warnings.deprecated once Python 3.13.
@deprecated.deprecated("Specify samples_per_epoch instead (input to train()).")
class LongerDataset:
    """
    Loops over a dataset to have a given length.

    All other function calls or attribute accesses are passed through to the
    original dataset.

    The remainder of the division is assigned to first elements of the dataset.
    To fix this, there would need to be random sampling that changes on
    each epoch, which is the responsibility of the DataLoader. So, it's not
    quite so easy to address. So we live with this limitation for now.
    """

    def __init__(self, dataset, length):
        self.dataset = dataset
        self.length = length

    @staticmethod
    def repeat(dataset, n_repeats):
        return LongerDataset(dataset, len(dataset) * n_repeats)

    def __len__(self):
        return self.length

    def __getitem__(self, idx):
        return self.dataset[idx % len(self.dataset)]

    def __getattr__(self, name):
        return getattr(self.dataset, name)


def slice_to_cum_len(
    seqs, length, how: Literal["exact", "under", "over"] = "exact"
):
    """Slice a list of sequences to a cumulative length.

    The `how` parameter determines whether the last sequence is cut to match the target
    length, or whether it is dropped (under) or included in full (over).
    """
    if len(seqs) == 0:
        return []
    cum_len = 0
    for i, seq in enumerate(seqs):
        cum_len += len(seq)
        if cum_len >= length:
            break
    assert i is not None
    if cum_len < length:
        raise ValueError(f"Not enough data to reach length {length}.")
    if how == "over":
        res = seqs[: i + 1]
    elif how == "exact":
        res = seqs[: i + 1]
        res[-1] = res[-1][: length - cum_len]
    elif how == "under":
        res = seqs[:i]
    else:
        raise ValueError(f"Invalid value for how: {how}")
    return res


def num_windows(seq_len: int, win_len: int, stride: int) -> int:
    """Returns the number of position a window can be placed along a sequence.

    Assume for sake of explanation that the dimension the window will move
    along is time. The window starts at the first timestep (t=0) and
    moves forward by stride timesteps to the next position. The window will
    not move forward if any part of it would be outside the sequence.

    Args:
        seq_len: length of the sequence. Or can be thought of as the length
            of which ever dimension the window is moving along.
        win_len: length of the window.
        stride: number of timesteps to move forward for each step.
    """
    # The most likely place for insidious bugs to hide is here. So try two
    # ways.
    # 1. Find the last strided timestep, then divide by stride.
    last_nonstrided = seq_len - win_len
    last_strided = last_nonstrided - (last_nonstrided % stride)
    n_windows1 = last_strided // stride + 1
    # 2. Same deal, but mindlessly copying the formula from Pytorch docs.
    # https://pytorch.org/docs/stable/generated/torch.nn.Conv1d.html
    # Padding is 0, and dilation is 1.
    n_windows2 = math.floor((seq_len - (win_len - 1) - 1) / stride + 1)
    assert n_windows1 == n_windows2, (
        f"Strided snippet calculation is wrong. {n_windows1} != "
        f"{n_windows2}."
    )
    return n_windows1


def num_windows_2d(
    seq_lens: "np.ndarray", win_len: int, stride: int
) -> "np.ndarray":
    """
    A 2D version of n_windows() where there is a list of sequences of different
    lengths.

    The implementation is the same! But is array based. The above function is
    therefore not really needed, but we keep it around anyway as sometimes
    you don't want or need to think of multi-dimensional arrays.
    """
    last_nonstrided = seq_lens - win_len
    last_strided_timestep = last_nonstrided - (last_nonstrided % stride)
    n_windows1 = last_strided_timestep // stride + 1
    # 2. Same deal, but mindlessly copying the formula from Pytorch docs.
    # https://pytorch.org/docs/stable/generated/torch.nn.Conv1d.html
    # Padding is 0, and dilation is 1.
    n_windows2 = np.floor((seq_lens - (win_len - 1) - 1) / stride + 1)
    assert np.array_equal(n_windows1, n_windows2), (
        f"Strided snippet calculation is wrong. {n_windows1} != "
        f"{n_windows2}."
    )
    return n_windows1


def decode_strided_wrap(
    index, seq_len, win_len, stride, shuffle
) -> Tuple[int, int]:
    """Decode an index to the (y, x) coordinates of a window in a 2D array.

    A 1D window moves along a dimension of a sequence and when it reaches the
    end, it wraps around and increments another dimension. This function
    converts a scalar index to the (y, x) coordinates of the window in a
    2D array. If shuffle is enabled, then to the y-coordinate a random number
    less than the stride is added to the y-coordinate. The random number is
    chosen uniformly in the range [0, stride), or [0, max) where max represents
    the largest number less than stride such that the window does not overflow
    the sequence length.

    Args:
        index: the index to decode.
        seq_len: the length of the sequence.
        win_len: the length of the window.
        stride: the number of timesteps to move forward for each step.
        shuffle: whether to add a random number to the window coordinate.
    """
    # Last position a window can be placed at:
    last_nonstrided = seq_len - win_len
    # Last position in [0, w, 2w, 3w, ...] that a window can be placed at:
    last_strided = last_nonstrided - (last_nonstrided % stride)
    n_ys = last_strided // stride + 1
    y = stride * (index % n_ys)
    if shuffle and stride > 1:
        y += torch.randint(0, stride, (1,), dtype=torch.long).item()
        # Randomly shift forward, but not past the last legal window position.
        y = min(y, last_nonstrided)
    x = index // n_ys
    return y, x


def decode_strided_ragged_wrap(
    idx, seq_lens, win_len, stride, shuffle
) -> Tuple[int, int]:
    """
    Decodes the index into the timestep and cell id.

    Similar to _decode_strided_wrap, but for the case where each cell has a
    different number of timesteps. The difference in arguments is that
    num_strided_timesteps is a 1D array instead of a single value.

    Args:
        index (int): The index to decode. In the range [0, ds_len)
        stride (int): The stride used to create the dataset.
        num_strided_timesteps (np.ndarray[int]): The number of strided
        timesteps for each cell.
        max_start_t (np.ndarray[int]): The maximum timestep a snippet can
        start, for each cell.

    """
    seq_lens = np.array(seq_lens) # Ensure it's a numpy array
    n_seqs = len(seq_lens)
    # Last positions a window can be placed at:
    last_nonstrided = seq_lens - win_len
    # Last positions in [0, w, 2w, 3w, ...] that a window can be placed at:
    last_strided = last_nonstrided - (last_nonstrided % stride)
    # Number of elments in [0, w, 2w, 3w, ...] for each sequence.
    n_ys = last_strided // stride + 1

    cumulative_starts = np.concatenate([[0], n_ys.cumsum()])
    # right and left bisects only differ when the requested value equals one of
    # the values in the list.
    #   - bisect_left([0, 5], 0) returns 0
    #   - bisect_right([0, 5], 0) returns 1.
    # Don't try the following line:
    ## seq_idx = bisect.bisect_left(self.cumulative_starts, idx)
    # Why? Example case: [0, 5, 12], idx=4 => 1 (correct is 0)
    x = bisect.bisect_right(cumulative_starts, idx) - 1
    if x >= n_seqs:
        raise ValueError(
            f"Index {idx} is out of bounds for the number of sequences "
            f"{n_seqs} ({cumulative_starts=}, {idx=})"
        )
    y = stride * (idx - cumulative_starts[x])
    if shuffle and stride > 1:
        y += torch.randint(0, stride, (1,), dtype=torch.long).item()
        # Randomly shift forward, but not past the last legal window position.
        y = min(y, last_nonstrided[x])
    return y, x
