import pytest
import math
import kddl
import kddl.datasets as ds
import numpy as np


@pytest.fixture
def ratios(np_rng):
    """Generate some ratios."""
    num_trials = 100
    num_splits = np_rng.integers(low=2, high=10, size=num_trials)
    ratios = [
        np_rng.integers(low=1, high=20, size=num_splits[i])
        for i in range(num_trials)
    ]
    return ratios


def _poisson_process_gen(length, rng):
    """k ~ Poisson."""
    res = []
    lo = 0
    mu = rng.integers(low=1, high=10)
    while True:
        k = lo + rng.exponential(mu) * length
        if k > length:
            break
        res.append(k)
        lo = k
    if len(res) == 0:
        res = rng.integers(low=0, high=length, size=1)
    return res


def test_split_borders(ratios, np_rng):
    """
    Tests that:

        1. A basic example works.
        2. The remainder is given to the first split.
        3. The ratios are divided by their gcd.
        4. A few invariants.
    """
    # 1. Length 10 array by ratios [5, 3, 2] goes to [5, 8].
    res = ds.split_borders([5, 3, 2], 10)
    assert res == [5, 8]

    # 2. Remainder is given to 1st split.
    res = ds.split_borders([5, 3, 2], 11)
    assert res == [6, 9]

    # 3. Ratios are first divided by their gcd.
    # This is checked by insuring the remainder is not larger than the ratio
    # sum after dividing by gcd.
    res = ds.split_borders([17, 17, 17], 100)
    n_per_division, rem = divmod(100, 3)  # Specifically not divmod(100, 51)
    assert res == [1 * n_per_division + rem, 1 * 2 * n_per_division + rem]

    # 4. Invariants
    for r in ratios:
        arr_len = np_rng.integers(low=sum(r), high=int(1e5))
        res = ds.split_borders(r, arr_len)
        # a. Sum of difference of borders is equal to length.
        assert np.sum(np.diff([0] + res + [arr_len])) == arr_len
        # b. Result is sorted.
        assert np.all(np.diff(res) > 0)
        # c. All elements are within [1, arr_len - 2].
        assert np.all((np.array(res) > 0) & (np.array(res) < arr_len - 1))
        # d. Data type of elements is int.
        assert all(isinstance(x, int) for x in res)


def test_split(ratios, np_rng):
    """
    Tests that:

        1. A basic example works.
        2. Invariants:
            a. Sum of lengths is equal to the length of the input list.
    """
    # 1. Basic example.
    res = ds.split(np.arange(10), [5, 3, 2])
    expected = [np.arange(5), np.arange(5, 8), np.arange(8, 10)]
    for r, e in zip(res, expected):
        assert np.array_equal(r, e)

    # 2. Invariants.
    # a. Sum of lengths is equal to the length of the input list.
    for rs in ratios:
        l = np_rng.integers(low=np.sum(rs), high=int(1e5))
        arr = np_rng.normal(size=l)
        res = ds.split(arr, rs)
        assert sum(len(r) for r in res) == l


def test_split2(ratios, np_rng):
    """
    Same as above, but for split2.

    Tests that:

        1. A basic example works.
        2. Invariants:
            a. Sum of lengths is equal to the length of the input list.
    """
    # 1. Basic example.
    res = ds.split2(np.arange(10), [5, 3, 2])
    expected = [np.arange(5), np.arange(5, 8), np.arange(8, 10)]
    for r, e in zip(res, expected):
        assert np.array_equal(r, e)

    # 2. Invariants.
    # a. Sum of lengths is equal to the length of the input list.
    for rs in ratios:
        l = np_rng.integers(low=np.sum(rs), high=int(1e5))
        arr = np_rng.normal(size=l)
        res = ds.split2(arr, rs)
        assert sum(len(r) for r in res) == l


def test_split_seq1d(ratios, np_rng):
    """
    Tests that:

        1. A basic example works.
        2. Invariants:
            a. Sum of lengths is equal to the length of the input list.
    """
    # 1. Basic example.
    res = ds.split_seq1d(seq=[2, 6, 7, 9], ratios=[5, 3, 2], interval_len=10)
    expected = [[2], [6, 7], [9]]
    for r, e in zip(res, expected):
        assert np.array_equal(r, e)

    # 2. Invariants.
    # a. All indices are present after splitting.
    for rs in ratios:
        l = np_rng.integers(low=np.sum(rs), high=int(1e5))
        seq = _poisson_process_gen(l, np_rng)
        res = ds.split_seq1d(seq, rs, l)
        assert np.concatenate(res).tolist() == seq


def test_split_seq(ratios, np_rng):
    """
    Tests that:

        1. A basic example works.
        2. Invariants:
            a. Sum of lengths is equal to the length of the input list.
    """
    # 1. Basic example.
    res = ds.split_seq(seq=[2, 6, 7, 9], ratios=[5, 3, 2], interval_len=10)
    expected = [[2], [6, 7], [9]]
    for r, e in zip(res, expected):
        assert np.array_equal(r, e)

    # 2. Invariants.
    # a. All indices are present after splitting.
    # b. For 1D, behaviour should be same as 1D case. (leaking test)
    for rs in ratios:
        l = np_rng.integers(low=np.sum(rs), high=int(1e5))
        seq = _poisson_process_gen(l, np_rng)
        res = ds.split_seq(seq, rs, l)
        res2 = ds.split_seq1d(seq, rs, l)
        assert np.concatenate(res).tolist() == seq
        assert np.concatenate(res2).tolist() == seq
    # c. Same as a., but with a key function.
    for rs in ratios:
        l = np_rng.integers(low=np.sum(rs), high=int(1e5))
        idxs = _poisson_process_gen(l, np_rng)
        seq = [(i, idxs[i]) for i in range(len(idxs))]
        res = ds.split_seq(seq, rs, l, key=lambda x: x[1])
        res_idxs = [r[1] for seq in res for r in seq]
        assert res_idxs == idxs


def test_decompress_seq():
    # Setup
    downsample_by = 9
    T = 123
    # fmt: off
    times1 = np.array([8, 9, 30, 40, 50, 70, 80, 90, 100, 110])
    times2 = np.array([0, 1, 8, 9, 10, 27, 30, 40, 50, 70, 80, 90, 100, 110])

    ans1 = np.array([1, 1,  0,  1,  1,  1,  0,  1,  1,  0,  1,  1,  1,  0])
    ans2 = np.array([3, 2,  0,  2,  1,  1,  0,  1,  1,  0,  1,  1,  1,  0])
    # fmt: on
    expected_output_len = math.ceil(T / downsample_by)
    assert len(ans1) == len(ans2) == expected_output_len

    # Test 1
    event_arr = ds.decompress_seq(times1, T, downsample_by)
    assert np.array_equal(event_arr, ans1)

    # Test 2
    # Test the case where two spikes land in the same bucket.
    # There should *not* be an error thrown, even though two samples land in
    # the same bucket.
    event_arr = ds.decompress_seq(times2, T, downsample_by)
    assert np.array_equal(event_arr, ans2)


def test_num_windows(np_rng):
    """Tests that:

    1. Some basic examples work.
    2. Some invariants hold.
    """

    def basic_examples():
        """1. Basic examples."""
        # fmt: off
        args_ans = (
                # seq_len, win_len, stride
                ((1, 1, 1), 1),
                ((2, 1, 1), 2),
                # Window is too big to fit even once:
                ((1, 2, 1), 0), 
                # +1 to win_len ⇒ -1 to num_windows
                ((5, 1, 1), 5),
                ((5, 2, 1), 4),
                ((5, 3, 1), 3),
                ((5, 4, 1), 2),
                ((5, 5, 1), 1),
                # +1 to stride
                ((5, 1, 2), 3),
                ((5, 1, 3), 2),
                ((5, 1, 4), 2),
                ((5, 1, 5), 1),
                # Even if stride is > win_len, we can still fit a window at 0.
                ((5, 1, 6), 1),
                # Some cases where there are common factors.
                ((12, 2, 2), 6),
                ((12, 3, 2), 5),
                ((12, 4, 2), 5),
                ((12, 5, 2), 4),
                ((12, 2, 3), 4),
                ((12, 2, 4), 3),
                ((12, 2, 5), 3),
                ((12, 2, 6), 2),
                ((12, 2, 12), 1),
                ((12, 2, 13), 1))
        # fmt: on
        for (seq_len, win_len, stride), ans in args_ans:
            assert ds.num_windows(seq_len, win_len, stride) == ans

    basic_examples()

    # 2. Invariants.
    def invariants():
        """2. Invariants."""
        invs = [
            lambda seq_len, win_len, stride, n_w: n_w <= seq_len,
            lambda seq_len, win_len, stride, n_w: (seq_len - win_len) / stride
            <= n_w,
        ]
        N = int(1e4)
        MAX_SEQ_LEN = int(1e6)
        MAX_WIN_LEN = int(1e6) + 100
        MAX_STRIDE = int(1e6) + 100
        seq_lens = np_rng.integers(low=1, high=MAX_SEQ_LEN, size=N)
        win_lens = np_rng.integers(low=1, high=MAX_WIN_LEN, size=N)
        strides = np_rng.integers(low=1, high=MAX_STRIDE, size=N)
        for seq_len, win_len, stride in zip(seq_lens, win_lens, strides):
            n_w = ds.num_windows(seq_len, win_len, stride)
            for i, inv in enumerate(invs):
                assert inv(seq_len, win_len, stride, n_w), (
                    f"Failed invariant {i} for seq_len={seq_len}, "
                    f"win_len={win_len}, stride={stride}, n_w={n_w}"
                )

    invariants()


def test_decode_strided_ragged_wrap(np_rng):
    """
    Tests that:

        1. A basic example works.
        2. Some exceptions are raised when expected. 

    """

    def basic_1d_examples():
        # fmt: off
        args_ans = (
            # idx, seq_lens, win_len, stride, shuffle=False
            # 1 sequence, win_len=1, stride=1
            ((0, [5], 1, 1), [0, 0]),
            ((1, [5], 1, 1), [1, 0]),
            ((2, [5], 1, 1), [2, 0]),
            ((3, [5], 1, 1), [3, 0]),
            ((4, [5], 1, 1), [4, 0]),
            # 1 sequence, win_len=2, stride=1
            ((0, [5], 2, 1), [0, 0]),
            ((1, [5], 2, 1), [1, 0]),
            ((2, [5], 2, 1), [2, 0]),
            ((3, [5], 2, 1), [3, 0]),
            # 1 sequence, win_len=1, stride=2
            ((0, [5], 1, 2), [0, 0]),
            ((1, [5], 1, 2), [2, 0]),
            ((2, [5], 1, 2), [4, 0]),
            # stride > seq_len
            ((0, [5], 1, 6), [0, 0]),
        )
        # fmt: on
        for args, ans in args_ans:
            idx, seq_lens, win_len, stride = args
            res = ds.decode_strided_ragged_wrap(
                idx, seq_lens, win_len, stride, shuffle=False
            )
            np.testing.assert_array_equal(res, ans)

    basic_1d_examples()

    def basic_2d_examples():
        # fmt: off
        args_ans = (
            ((0, [5, 6], 1, 1), [0, 0]),
            ((4, [5, 6], 1, 1), [4, 0]),
            ((5, [5, 6], 1, 1), [0, 1]),
            ((6, [5, 6], 1, 1), [2, 1]),
            ((7, [5, 6], 1, 1), [3, 1]),
            ((10, [5, 6], 1, 1), [5, 1]),
            ((0, [1,1,1,1,1,1], 1, 1), [0, 0]),
            ((1, [1,1,1,1,1,1], 1, 1), [0, 1]),
            ((5, [1,1,1,1,1,1], 1, 1), [0, 5]),
        )
        # fmt: on
        for idx, (args, ans) in enumerate(args_ans):
            idx, seq_lens, win_len, stride = args
            res = ds.decode_strided_ragged_wrap(
                idx=idx,
                seq_lens=seq_lens,
                win_len=win_len,
                stride=stride,
                shuffle=False,
            )
            np.testing.assert_array_equal(res, ans, 
                err_msg=f"Failed for idx={idx}, seq_lens={seq_lens}, "
                f"win_len={win_len}, stride={stride}"
            )
    basic_2d_examples()


    def idx_too_high_1d():
        # Length 5 array, doesn't have index 5 element.
        with pytest.raises(ValueError):
            ds.decode_strided_ragged_wrap(
                idx=5, seq_lens=[5], win_len=1, stride=1, shuffle=False
            )
        with pytest.raises(ValueError):
            ds.decode_strided_ragged_wrap(
                idx=4, seq_lens=[5], win_len=2, stride=1, shuffle=False
            )
        with pytest.raises(ValueError):
            ds.decode_strided_ragged_wrap(
                idx=3, seq_lens=[5], win_len=1, stride=2, shuffle=False
            )
        # win_len > seq_len
        with pytest.raises(ValueError):
            ds.decode_strided_ragged_wrap(
                idx=3, seq_lens=[5], win_len=6, stride=1, shuffle=False
            )
    idx_too_high_1d()

    def idx_too_high_2d():
        # Length 5 array, doesn't have index 5 element.
        # idx >= 5+6
        with pytest.raises(ValueError):
            ds.decode_strided_ragged_wrap(
                idx=11, seq_lens=[5, 6], win_len=1, stride=1, shuffle=False
            )
        # idx >= 5+6
        with pytest.raises(ValueError):
            ds.decode_strided_ragged_wrap(
                idx=12, seq_lens=[5, 6], win_len=1, stride=1, shuffle=False
            )
        with pytest.raises(ValueError):
            ds.decode_strided_ragged_wrap(
                idx=5, seq_lens=[1, 1, 1, 1, 1], win_len=1, stride=1, shuffle=False
            )
        with pytest.raises(ValueError):
            ds.decode_strided_ragged_wrap(
                idx=6, seq_lens=[1, 1, 1, 1, 1], win_len=1, stride=1, shuffle=False
            )
    idx_too_high_2d()
