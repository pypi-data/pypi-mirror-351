import pytest
import numpy as np
import kddl
import kddl.lrfind as lrfind
from pathlib import Path
import json
import polars as pl
import logging

_logger = logging.getLogger(__name__)


def load_json(case_num):
    path = Path(__file__).parent / f"resources/case{case_num}.json"
    with open(path, "r") as f:
        return json.load(f)


def load_parquet(case_num):
    path = Path(__file__).parent / f"resources/case{case_num}.parquet"
    return pl.read_parquet(path)


def test_cut_takeoff1():
    """
    Tests that cut_takeoff cuts off the right-side of the array.

    The array is a 1D array something like:

                                            
                                            *
                                            *
       * * * * * *                         *
                   *                      *
                     *                    *
                       *                 *
                        * * * * * * * * *
    """
    loss_arr = lrfind.to_loss_arr(load_json(1))
    res = lrfind.cut_takeoff(loss_arr)
    very_low = 766
    very_high = 900
    expected = 800
    _len = res.shape[1]
    assert very_low < _len < very_high, "This should definitely not fail."
    assert _len == pytest.approx(expected, abs=20), f"should be ~{expected}."


def test_cut_takeoff2():
    """
    This test was written in response to a bug. The bug was fixed by changing
    the line:

        `above_max = np.flatnonzero(mask_in * loss_arr.mean(axis=0) > ignore_over)`

    to:

        `above_max = np.flatnonzero(mask_in * (loss_arr.mean(axis=0) > ignore_over))`

    The error case occured when mask_in was False, but ignore_over was below
    zero.
    """
    cutoff_case2 = lrfind.to_loss_arr(load_json(3))
    assert len(cutoff_case2[0]) == 1000
    res = lrfind.cut_takeoff(cutoff_case2)
    assert res.shape[1] > 400, "Shouldn't be severely cut off."


def test_cut_takeoff3():
    """
    This test was witten in response to a perceived probable bug associated with
    cutting off the right side too close to the minimum value. This led to an
    issue when the minimum value was due to a large deviation from the loss on
    either side. Cutting off later (further right) will hopefully prevent this
    spurious low loss being identified as the location of best lr.
    """
    cutoff_case3 = lrfind.to_loss_arr(load_json(6))
    assert len(cutoff_case3[0]) == 1000
    res = lrfind.cut_takeoff(cutoff_case3)
    # 680 is the value where it was cut off before. Probabbly at least 750 is
    # a good value.
    # Okay to tweak:
    assert res.shape[1] > 750, "Shouldn't be cut off so early."
    # Most likely a bug if this fails:
    assert res.shape[1] > 680, "Shouldn't be cut off so early."


def test_cut_takeoff4():
    """This test was written when a case was encountered where cut_takeoff
    returned an empty array. The cause was the loss curve was practically flat,
    and the minimum value happened to be at the start of the array. The correct
    behaviour when the loss curve is flat is to return the whole array.
    Currently, this is only done when cut_takeoff would return an empty array;
    however, it should probably be extended to indentify flat losses with a
    statistical test, which would allow us to detect the case even when it's
    not the very first element that is the minimum value."""
    loss_arr = lrfind.to_loss_arr(load_json(9))

    # Test 1.
    # This is what cut_takeoff uses.
    res = lrfind.is_flat(loss_arr)
    assert res, "Should be flat."

    # Test 2.
    # cut_takeoff doesn't cut off anything.
    res = lrfind.cut_takeoff(loss_arr)
    assert res.shape[1] == loss_arr.shape[1], "Souldn't be any cut off."


def test_cut_takeoff5():
    """Insures the instability and flicks at the end are cut off.

    This test uses case 11.
    """
    df = load_parquet(11)

    # Test 1
    # All sequences should have at least 50 steps removed.
    for i, row in enumerate(df.iter_rows(named=True)):
        loss_arr = lrfind.to_loss_arr(row["loss"])
        res = lrfind.cut_takeoff(loss_arr)
        n_cut = loss_arr.shape[1] - res.shape[1]
        assert (
            n_cut >= 50
        ), f"Should have cut at least 50 steps. ({i=})"


def test_cut_takeoff6():
    """The opposite of test_cut_takeoff5: don't cut off too soon."""
    df = load_parquet(12)

    # Test 1
    # All sequences should have at least 750 steps remaining.
    for i, row in enumerate(df.iter_rows(named=True)):
        loss_arr = lrfind.to_loss_arr(row["loss"])
        res = lrfind.cut_takeoff(loss_arr)
        assert res.shape[1] >= 750, f"Should have at least 750 steps. ({i=})"

def test_is_flat():
    """Insure that is_flat() returns true for a flat case.

    is_flat() previously returned true on this case (an omi-const sweep).
    """
    # Setup
    sweep = np.array(load_json(13))
    N, L = sweep.shape
    assert N == 8 and L == 1000, "Sweep had 8 runs of 1000 steps."

    # Test
    # assert lrfind.is_flat(sweep), "Should be flat."
    assert not lrfind.is_flat(sweep), (
        "This is a known broken case (unexpectedly passed!)"
    )




def test_kalman_smooth():
    """
    The lr curve looks something like:


                                                        *           *
                                                      *  *         *
                                                    *     *       *
                                                  *        *     *
        * * * * * *            * * * * * * * * * *          *   *
                    *         *                              * *
                      *      *                                *
                        *   *
                          *

    We want to choose the first dip.
    """
    loss_arr = lrfind.to_loss_arr(load_json(2))
    smooth_dloss = kddl.lrfind.kalman_smooth(loss_arr)
    min_grad_at = np.argmin(smooth_dloss)
    buf = 50
    assert min_grad_at < len(smooth_dloss) - buf


def test_kalman_2_dips():
    """
    The lr curve looks something like:

        * * * * * *        * * * * * * * * * * * * * * *        *
                   *      *                             *       *
                    *    *                               *     *
                     *  *                                 *   *
                      *                                    * *
                                                            *
    We want to choose the second dip.

    On a figure, the first dip looks visually appealing as a choice for the
    best learning rate; however, there isn't really any reason not to choose
    the second dip, as it doesn't have any pathalogical properties.

    This test case is to ensure that the algorithm chooses the second dip.
    If this tests breaks, then maybe you have either:

      - tried to fix a perceived bug that wasn't a bug, or
      - you have identified why the second dip is a bad choice.

    In the second case, the reasoning should be made clear in an updated
    description of the choice function.
    """
    loss_arr = lrfind.to_loss_arr(load_json(4))
    smooth_dloss = kddl.lrfind.kalman_smooth(loss_arr)
    min_grad_at = np.argmin(smooth_dloss)
    # If this fails, please read the test description before updating the
    # target value. It's reasonable for the value to change slightly, but
    # not jump back to a low value.
    assert min_grad_at == pytest.approx(870, abs=10), "should be near 870."
    # This assert; however, should not be tweaked.
    assert min_grad_at > 500, "Should never fail; function is likely broken."


@pytest.mark.skip(reason="Using v1, which chooses the second dip.")
def test_kalman_2_dips_v2():
    """
    On closer inspection of the lr curve (compare to the disabled test above),
    the lr curve is more like:
                                                                      *
                                                               *     *
        * * * * * *        * * * * * * * * * * * * * *         *    *
                   *      *                            *       *   *
                    *    *                              *     * * *
                     *  *                                *    * **
                      *                                    * *  *
                                                            *   *

    And so there is arguably 3 dips. If we reduce the process variance, then
    the first dip is preferred, as the latter two are smoothed out. From other
    tests, the process variance scaled at sqrt(2) seemed to high, and so it was
    reduced. The algorithm now chooses the first dip. The choice of the first
    or second dip will switch based on the value of Q_scale, the parameter to
    kalman_smooth. When Q_scale is low (tested at 1/3), then the process
    variance is pushed lower, and the second dip is not steady enough and is
    smoothed out. When Q_scale is higher (tested at sqrt(2)), the second dip is
    chosen.

    On a figure, the first dip looks visually appealing as a choice for the
    best learning rate; however, there isn't really any reason not to choose
    the second dip, as it doesn't have any pathalogical properties.

    This test case is to ensure that the algorithm chooses the second dip.
    If this tests breaks, then maybe you have either:

      - tried to fix a perceived bug that wasn't a bug, or
      - you have identified why the second dip is a bad choice.

    In the second case, the reasoning should be made clear in an updated
    description of the choice function.
    """
    loss_arr = lrfind.to_loss_arr(load_json(4))
    smooth_dloss = kddl.lrfind.kalman_smooth(loss_arr)
    min_grad_at = np.argmin(smooth_dloss)
    # If this fails, please read the test description before updating the
    # target value. It's reasonable for the value to change slightly, but
    # not jump back to a low value.
    # History: 461, 470
    assert min_grad_at == pytest.approx(470, abs=10), "should be near 470."
    # This assert; however, should not be tweaked.
    assert min_grad_at < 700, "Should never fail; function is likely broken."


def test_kalman_3():
    """
    The lr curve looks something like:

        * * * * * * **
                       **
                         **
                           **
                            **
                               **            **
                                  ** * * * *
              ↑           ↑
            error       expected

    An error case was observed where a very low learning rate was chosen on
    a nice and simple looking lr curve where there seemed to be an obvious
    sleep slope where the learning rate should have be chosen. This case
    is the basis for the test case.
    """
    loss_arr = lrfind.to_loss_arr(load_json(5))
    smooth_dloss = kddl.lrfind.kalman_smooth(loss_arr)
    min_grad_at = np.argmin(smooth_dloss)
    # If this fails, please read the test description before updating the
    # target value. It's reasonable for the value to change slightly, but
    # not jump back to a low value.
    assert min_grad_at == pytest.approx(481, abs=20)


def test_kalman_4():
    """
    An error was observed where a model with very high loss was having the
    loss overly smoothed, to the point where it want practically a straght
    line, despite the loss having a nice curve and clear good lr region.

    The cause is believed to be due to incorrect choice of process and
    observation variance.
    """
    loss_arr = lrfind.to_loss_arr(load_json(6))
    smooth_dloss = kddl.lrfind.kalman_smooth(loss_arr)
    min_grad_at = np.argmin(smooth_dloss)
    assert min_grad_at == pytest.approx(650, abs=100)


def test_kalman_5():
    """The boundary was pulling the Kalman smoothed loss down.

    Covers two cases, both similar effect.
    """
    # Don't cut off too early.
    loss_arr = lrfind.to_loss_arr(load_json(4))
    res = lrfind.cut_takeoff(loss_arr)
    # 866 is the value where it was cut off before. More would be better.
    # Okay to tweak upwards.
    assert res.shape[1] >= 866, "Shouldn't be cut off so early."

    # Don't be affected by the boundary.
    case = lrfind.to_loss_arr(load_json(8))
    smooth_dloss = kddl.lrfind.kalman_smooth(case)
    min_grad_at = np.argmin(smooth_dloss)
    # Some history
    # This test used to have:
    #
    ## Should be lower than 750, maybe around 600.
    # assert min_grad_at < 700
    ## The cutoff is at 904, so it should definitely be lower than that.
    # assert min_grad_at < 904
    #
    # But on inspecting the lr-curve, it seems this is when we were more keen
    # to avoid placing the best lr in the 2nd dip. The more recent thinking is
    # that the second dip is exactly where we want to place the lr, as we want
    # the just-before-unstable region, and not just target some region of
    # long negative slope. This is based on the updated understanding that the
    # slopes are quite dependent on the dataset, and so we shouldn't pay
    # too much attention to them, or to try and value long negative slopes.
    #
    # I'm not even sure if this test is necessary, or at least its purpose
    # has changed. I'll allow either of the slopes. It's hard to expect one
    # or the other, as they look very similar steepness.
    at_first = 420 < min_grad_at < 550
    at_second = 850 < min_grad_at < 930
    assert at_first or at_second, "Should be in the first or second dip."


def test_kalman_6():
    """Insures the Kalman filter doesn't have a flick at the end.

    This flick has been observed many times. The test data consists of ~50
    cases of the flick that were found in a single experiment.

    The case data is a parquet file, as we need to do two things:
        - make sure we can identify all the flicks in the historic predictions
        - then make sure current predictions don't have the flick.
    """
    df = load_parquet(10)
    # Case 10 also has cases where there is no flick, which we use to ensure
    # the identification of the flick is working.
    df_no_flick = pl.read_parquet(
        Path(__file__).parent / f"resources/case10_noflick.parquet"
    )

    def has_flick(kalman_smoothed):
        TAIL_LEN = min(50, len(kalman_smoothed) // 2)
        tail_slope = (
            abs(kalman_smoothed[-TAIL_LEN - 1] - kalman_smoothed[-1]) / TAIL_LEN
        )
        # Larger q makes it less likely to register a flick.
        # This value is tweaked to reduce false positives and negatives.
        q = 0.60
        slope_threshold = np.quantile(np.abs(np.diff(kalman_smoothed)), q)
        has_flick = tail_slope > slope_threshold
        _logger.info(f"{tail_slope=}, {slope_threshold=}, {has_flick=}")
        return has_flick

    # Test 0: internal test.
    def test_has_flick():
        """Test of the test code, has_flick."""
        for i, row in enumerate(df.iter_rows(named=True)):
            kalman_smoothed = row["ckalman"]
            assert has_flick(kalman_smoothed), (
                "Test is broken. Flicks should be present in this example: "
                f'{i}: {row["ds"]=}, {row["batch_size"]=}, {row["model"]=}'
            )

        for i, row in enumerate(df_no_flick.iter_rows(named=True)):
            kalman_smoothed = row["ckalman"]
            assert not has_flick(kalman_smoothed), (
                "Test is broken. Flicks should be absent in this example: "
                f'{i}: {row["ds"]=}, {row["batch_size"]=}, {row["model"]=}'
            )

    test_has_flick()

    # Test 1: current code produces no flicks.
    df = pl.concat([df, df_no_flick])
    for i, row in enumerate(df.iter_rows(named=True)):
        loss_arr = lrfind.to_loss_arr(row["loss"])
        kalman_smoothed = lrfind.kalman_smooth(loss_arr).tolist()
        has_fl = has_flick(kalman_smoothed)
        if i in {2,4, 39, 46}:
            assert has_fl, (
                "This is a known broken test, and now unexpectedly passed!"
            )
            continue
        assert not has_fl, (
            "Flicks should be absent. "
            f'{i=}: {row["ds"]=}, {row["batch_size"]=}, {row["model"]=}'
        )
