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


def lr_sched(lr_min, lr_max, n_lr_steps):
    sched = lr_min * (lr_max / lr_min) ** np.linspace(0, 1, n_lr_steps)
    return sched


def lr_early_stopper(n_steps):
    return train.EarlyStopper(
        min_steps=n_steps // 2,
        step_patience=5,
        best_factor=10,
    )


class TroublesomeLrCurve(Exception):
    """The LR curve is problematic. This is a case worth investigating."""

    def __init__(self, message):
        super().__init__(message)
        self.message = message


def sweep(
    trainable,
    lr_min,
    lr_max,
    n_lr_steps,
    n_runs,
    early_stopper=None,
    init_weights=None,
    log_space=True,
    **train_kwargs,
) -> Tuple[List[List[float]], List[float]]:
    """Run an LR sweep `n_runs` times, each time starting from `init_weights`.

    As the sweep can terminate early, the losses are returned as a list of
    lists, potentially of different lengths.
    """
    _logger.info(
        f"{n_runs} LR sweeps from {lr_min:.1e} to {lr_max:.1e} in "
        f"{n_lr_steps} steps."
    )
    _logger.info(f"Train kwargs: {train_kwargs}")
    if init_weights is None:
        init_weights = trainable.model.state_dict()
    if log_space:
        lr_sched = (
            lr_min * (lr_max / lr_min) ** np.linspace(0, 1, n_lr_steps)
        ).tolist()
    else:
        lr_sched = np.linspace(lr_min, lr_max, n_lr_steps).tolist()
    all_losses = []
    for run in range(n_runs):
        if early_stopper is not None:
            # Don't reuse the same early stopper each run!
            early_stopper.reset()
        trainable.model.load_state_dict(init_weights)
        _, losses = train._lr_sweep(
            trainable, lr_sched, early_stopper=early_stopper, **train_kwargs
        )
        all_losses.append(losses)
        best_idx = np.argmin(losses)
        best_lr = lr_sched[best_idx]
        best_loss = losses[best_idx]
        _logger.info(
            f"Run {run} [finished]\tBest (step, lr, loss) "
            f"= ({best_idx}, {best_lr:.1e}, {best_loss:.3g})"
        )
    return all_losses, lr_sched


def steepest_loss(losses, run_lens, lr_sched, k_smooth):
    if k_smooth % 2 == 0:
        raise ValueError("k_smooth must be odd.")
    mask = (
        np.stack([np.arange(len(lr_sched)) for i in range(len(run_lens))])
        < run_lens[:, None]
    )
    losses = losses * mask
    # Shift right by 1 then re-mask, as otherwise we diff to first mask zero.
    # We want 0 to be the first value too.
    dloss = np.where(mask, np.pad(np.diff(losses), ((0, 0), (1, 0))), 0)
    mask_sum = np.sum(mask, axis=0)
    ave_dloss = np.divide(np.sum(dloss, axis=0), mask_sum, where=mask_sum > 0)
    # TODO: the lrs are evenly spaced in log-space, so the equal weighting
    # by smoothing could be improved. The end goal would be to use Kalman
    # filtering+smoothing to estimate the dloss. For now, smoothing.
    smooth_dloss = np.convolve(
        ave_dloss, np.ones(k_smooth) / k_smooth, mode="valid"
    )
    smooth_dloss = np.pad(smooth_dloss, (k_smooth // 2, k_smooth // 2))
    # TODO: need a better way to cut of the possibly noisy end.
    # Don't go past the max run length, or 75% of the full length.
    max_idx = min(np.min(run_lens), math.floor(len(lr_sched) * 0.75))
    steepest_idx = np.argmin(smooth_dloss[0:max_idx])
    steepest_lr = lr_sched[steepest_idx]
    if np.any(steepest_idx >= run_lens):
        _logger.error(
            f"Steepest loss at {steepest_idx} is beyond the run length {run_lens}"
        )
        # Fix is to better cut the noisy end.
    # assert all(steepest_idx < run_lens)
    return steepest_lr, steepest_idx, ave_dloss, smooth_dloss


def pad_over_inf(w: List[float], to_len: int) -> np.ndarray:
    w = np.array(w)
    nonfinite = np.flatnonzero(~np.isfinite(w))
    if len(nonfinite) == 0:
        return w
    first_invalid = nonfinite[0]
    if first_invalid == 0:
        return np.full(to_len, fill_value=0)
    w = np.array(w)[:first_invalid]
    max_val = np.max(w)
    assert np.isfinite(max_val)
    return np.pad(
        w,
        (0, to_len - first_invalid),
        mode="constant",
        constant_values=max_val,
    )


def is_flat_entropy_test(loss_arr, min_tol=1.3):
    """
    Args:
        loss_arr: 2D array of losses, with shape (n_runs, n_steps)
        min_tol: entropy_all - entropy_init < np.log(min_tol) => flat
            The lower the value, the harder it is to be considered flat.
    """
    if min_tol <= 1:
        raise ValueError("min_tol must be > 1.")
    INIT_LEN = 50
    at_start = loss_arr[:, :INIT_LEN].flatten()
    mu = np.mean(at_start)
    # A recent change, doubling the variance. Would have been good to have
    # more test cases to ensure this heuristic is still okay.
    var = np.var(at_start) #* 2
    entropy_init = -np.mean(scipy.stats.norm.logpdf(at_start, mu, var))
    entropy_all = -np.mean(scipy.stats.norm.logpdf(loss_arr, mu, var))
    is_flat = entropy_all - entropy_init < np.log(min_tol)
    return is_flat


def is_flat(loss_arr, min_tol=1.3):
    by_entropy = is_flat_entropy_test(loss_arr, min_tol)
    # Any other tests?
    return by_entropy


def clip_to_finite(w: Sequence[float]):
    for i, v in enumerate(w):
        if not np.isfinite(v):
            return w[:i]
    return w


def to_loss_arr(losses: Sequence[Sequence[float]]) -> Optional[np.ndarray]:
    loss_arr = [clip_to_finite(loss) for loss in losses]
    max_len = min(len(l) for l in loss_arr)
    loss_arr = np.stack([np.array(l)[0:max_len] for l in loss_arr])
    assert np.all(np.isfinite(loss_arr)), "Should be no infs/nans"
    if loss_arr.size == 0:
        return None
    # loss_arr[np.isnan(loss_arr)] = np.inf
    return loss_arr


def cut_takeoff(loss_arr):
    """Cut the right-side if the losses are very large.

    The losses can grow massively towards the end of the lr-find. This
    interferes with the kalman smoothing. We cut off the right-side if the
    losses are above the starting loss.

    Two options here:
      1. Take until the last point that is below the limit.
         An issue with this option is that the loss can spike and then come
         back down again, and this criteria can cause the spike to be
         included.
      2. Take until the first point that is above the limit.
         This is more agressive, but avoids the above issue. To balance the
         aggressiveness, we can increase the quantile used in the above_limit.
    """
    n_runs, n_steps = loss_arr.shape
    assert n_runs < n_steps, "The axis are wrong."

    def is_too_high(quantile):
        """Choose a good representative low value, and get it's index."""
        # The amount of smoothing will effect the choice of quantile.
        k = 15
        long_enough_to_ave = n_steps > k * 5
        if long_enough_to_ave:
            smoothed_loss = np.convolve(
                loss_arr.mean(axis=0), np.ones(k) / k, mode="valid"
            )
            smoothed_loss = np.pad(smoothed_loss, (k // 2, k // 2), mode="edge")
            assert len(smoothed_loss) == loss_arr.shape[1]
            low_val = smoothed_loss.min()
            low_at = np.flatnonzero(smoothed_loss <= low_val)
        else:
            _logger.warning("loss array too short to smooth.")
            smoothed_loss = loss_arr.mean(axis=0)
            low_val = smoothed_loss.min()
            low_at = np.flatnonzero(smoothed_loss <= low_val)
        low_at = n_steps if len(low_at) == 0 else low_at[0]
        assert 0 <= low_at < n_steps
        # Attempts to give a little padding seem to generally fail. There can
        # be sudden jumps, which negatively affect Kalman smoothing results.
        if not low_at > 0:
            _logger.error("Expected +ve. is_flat() should have caught this.")
            raise TroublesomeLrCurve(
                "Curve doesn't descend, yet isn't detected as flat."
            )
        # ignore_over = np.quantile(smoothed_loss[0:low_at], quantile)
        # Switch to band, as long initial slopes can allow large swings to be
        # included.
        band_len = 100
        band_around_min = loss_arr[:, max(0, low_at - band_len) : low_at]
        ignore_over = np.quantile(band_around_min, quantile)
        _logger.debug(f"{ignore_over=:.3f}")
        # ignore_over = low_val
        above_limit = smoothed_loss > ignore_over
        return low_at, low_val, above_limit

    if is_flat(loss_arr):
        return loss_arr

    low_at, low_val, above_limit = is_too_high(quantile=0.95)
    is_after_min = np.zeros(n_steps, dtype=bool)
    # Don't cut off before min is reached.
    # Attempts to give a little padding seem to generally fail. The min can be
    # very late, and very close to sudden jumps, which negatively affect Kalman
    # smoothing results, so be careful doing this.
    buff = 0
    is_after_min[low_at + buff + 1 :] = True
    above_max = np.flatnonzero(is_after_min & above_limit)
    max_t = loss_arr.shape[1] if len(above_max) == 0 else above_max[0]
    _logger.debug(f"Cutting off at {max_t} steps. ({low_val=:.3f})")
    assert np.all(
        np.isfinite(loss_arr[:, 0 : max_t + 1])
    ), "Should be no infs/nans"
    loss_arr = loss_arr[:, 0 : max_t + 1]
    return loss_arr


def mean_smooth(losses: Sequence[Sequence[float]], k: int = 21):
    losses = cut_takeoff(losses)
    dloss = np.pad(np.diff(losses), ((0, 0), (1, 0)))
    mean_dloss = dloss.mean(axis=0)
    k = 21
    smoothed_dloss = np.convolve(mean_dloss, np.ones(k) / k, mode="valid")
    # Pad with the edge values. Don't convolve as "same", as we want to
    # reduce flick towards 0.
    smoothed_dloss = np.pad(smoothed_dloss, (k // 2, k // 2), mode="edge")
    return mean_dloss, smoothed_dloss


def kalman_smooth(loss_arr, Q_scale: float = 1):
    # Q_scale: float = math.sqrt(2)):
    # Q_scale = math.sqrt(2)
    Q_scale = 1 / 3
    _logger.debug("[start] Kalman smoothing")
    losses = cut_takeoff(loss_arr)
    dloss = np.pad(np.diff(losses), ((0, 0), (1, 0)))

    # First, we will estimate good values for the process and observation noise
    # variance. The transition between min and max of the smoothed dloss should
    # be obtained gradually by the changing state, so (max-min) acts as an
    # upper bound on the process noise variance, Q.
    # k = 15
    # long_enough_to_ave = dloss.shape[1] > k * 5
    # if long_enough_to_ave:
    #     ave_smoothed_loss = np.convolve(
    #         losses.mean(axis=0), np.ones(k) / k, mode="valid"
    #     )
    #     est_Q = np.var(np.diff(ave_smoothed_loss)) * Q_scale
    #     # est_Q = np.var(ave_smoothed_dloss)
    #     if not np.isfinite(dloss.mean()):
    #         import pdb
    #
    #         pdb.set_trace()
    #     _logger.info(f"{est_Q=:.3e}")
    #     _logger.info(f"{dloss.mean()=:.3e}")
    # else:
    #     est_Q = 1e-4

    obs = dloss.T
    n_steps, n_obs = obs.shape
    # R_k is estimated by a sliding window variance of the observations.
    # This allows it to change over time, which is what we expect.
    window_len = min(31, ((n_steps + 1) // 2) * 2 - 1)
    vars = np.pad(
        sliding_window_view(obs, (window_len, n_obs)).var(axis=(1, 2, 3)),
        (window_len // 2, window_len // 2),
        mode="edge",
    )
    assert vars.shape == (n_steps,), f"{vars.shape=}, {n_steps=}"
    R_to_Q = 8000
    R_k = [R_to_Q / (1 + R_to_Q) * r * np.eye(n_obs) for r in vars]
    assert R_k[0].shape == (n_obs, n_obs)
    Q = [max(1e-7, 1 / (1 + R_to_Q)) * r for r in vars]
    _logger.debug(f"Q: {np.mean(Q):.3e}, {np.min(Q):.3e}, {np.max(Q):.3e}")
    # Q = [est_Q for r in vars]

    # Kalman filter parameters
    F = 1  # State transition matrix (scalar)
    H = np.ones((n_obs, 1))  # Observation matrix

    # Initial estimates
    x_hat = np.zeros(n_steps)
    # x_hat[0] = obs[0:20].mean()  # Initial estimate of delta-loss
    # x_hat = np.mean(obs, axis=1)  # Filtered estimates of delta-loss
    # x_hat = np.full(
    #     n_steps, fill_value=obs[0].mean()
    # )  # Filtered estimates of delta-loss
    P = np.zeros(n_steps)  # Filtered estimate covariance
    P[0] = 10 * Q[0]  # Initial estimate covariance
    x_hat_minus = np.zeros(n_steps)  # Predicted state estimates
    P_minus = np.zeros(n_steps)  # Predicted estimate covariance

    # Kalman filter forward pass
    for k in range(1, n_steps):
        # Prediction step
        x_hat_minus[k] = F * x_hat[k - 1]
        P_minus[k] = F * P[k - 1] * F + Q[k]

        # Update step
        z_k = obs[k].reshape(-1, 1)  # Observation vector at time k
        y_k = z_k - H * x_hat_minus[k]  # Innovation vector

        S_k = H * P_minus[k] * H.T + R_k[k]  # Innovation covariance matrix
        # S_k = S_k + 1e-8 * np.eye(S_k.shape[0])  # Add small noise to avoid singularity
        K_k = P_minus[k] * H.T @ np.linalg.inv(S_k)  # Kalman gain vector

        x_hat[k] = x_hat_minus[k] + (K_k @ y_k).item()  # Updated state estimate
        P[k] = (
            P_minus[k] - (K_k @ S_k @ K_k.T).item()
        )  # Updated estimate covariance

    # Kalman smoother backward pass
    x_hat_smooth = np.zeros(n_steps)  # Smoothed state estimates

    # Initialize with the last filtered estimates
    x_hat_smooth[-1] = x_hat[-1]
    for k in range(n_steps - 2, -1, -1):
        # Compute the smoothing gain
        # Warn if expecting numerical issues.
        A_k = P[k] * F / P_minus[k + 1]
        if abs(A_k) > 1e3:
            _logger.warning(f"{A_k=:.3e} at {k}. Possible numerical issues.")

        # Smoothed state estimate
        DAMPING = 0.95
        x_hat_smooth[k] = x_hat[k] + DAMPING * A_k * (
            x_hat_smooth[k + 1]
            - x_hat_minus[k + 1]
            # x_hat_smooth[k + 1] - x_hat[k + 1]
        )
    assert x_hat_smooth[-1] == x_hat[-1]
    return x_hat_smooth


def mean_lr_choose(lrs, loss_arr):
    mean_dloss, smoothed_dloss = mean_smooth(loss_arr)
    suggested_lr_idx_mloss = np.argmin(smoothed_dloss)
    assert suggested_lr_idx_mloss < len(lrs), suggested_lr_idx_mloss
    suggested_lr_mloss = lrs[suggested_lr_idx_mloss]
    return (
        mean_dloss,
        smoothed_dloss,
        suggested_lr_idx_mloss,
        suggested_lr_mloss,
    )


def critical_points(kalman_dloss) -> Tuple[int, int, int]:
    # Some preliminary arrays and points used in the below calculations.
    ddloss = np.concatenate([[0], np.diff(kalman_dloss)])
    cum_dloss = np.cumsum(kalman_dloss)
    min_idx = np.argmin(cum_dloss)
    if min_idx == 0:
        raise TroublesomeLrCurve("Minimum is at the start.")
        # return 0, 0, 0

    # 1. Steepest slope, not after the minimum.
    # We limit to the lhs of the minimum so as to avoid choosing points that
    # follow a regression in the loss back up.
    min_grad_idx = np.argmin(kalman_dloss[:min_idx])

    # 2. Maximum double-derivative. Acts as right bound where there can be a
    # flick up. Only consider after the min_grad_idx.
    ddloss = np.concatenate([[0], np.diff(kalman_dloss)])

    # Max ggrad
    # Order by acceleration (highest first), and take the first point that isn't
    # thrown out by the the creteria:
    #   a) it must be after the min_grad_idx
    #   b) it must be after the min_idx
    #   c) it must have a positive gradient/velocity.
    max_ggrad_idx = next(
        itertools.chain(
            itertools.dropwhile(
                lambda x: x[0] <= min_grad_idx
                or x[0] <= min_idx
                or kalman_dloss[x[0]] <= 0,
                sorted(enumerate(ddloss), key=lambda x: x[1], reverse=True),
            ),
            [(len(kalman_dloss) - 1, None)],
        )  # if no point matches above criteria.
    )[0]

    # 3. Minimum double-derivative. Acts as left bound. Only consider before
    # the min_grad_idx.
    min_ggrad_idx = np.argmin(ddloss[:min_grad_idx])

    return min_ggrad_idx, min_grad_idx, max_ggrad_idx


def kalman_lr_choose_old(lrs, loss_arr, end_margin=50):
    kalman_dloss = kalman_smooth(loss_arr)
    # suggested_lr_idx_kalman = np.argmin(kalman_dloss)
    # If end_margin is too large, clip to 1/3 of the length.
    end_margin = min(end_margin, len(kalman_dloss) // 3)
    suggested_lr_idx = next(
        itertools.dropwhile(
            lambda x: x[0] >= len(kalman_dloss) - end_margin,
            sorted(enumerate(kalman_dloss), key=lambda x: x[1]),
        )
    )[0]
    suggested_lr = lrs[suggested_lr_idx]
    assert suggested_lr_idx < len(kalman_dloss) - end_margin, suggested_lr_idx
    return kalman_dloss, suggested_lr_idx, suggested_lr


def kalman_lr_choose(lrs, loss_arr, end_margin=50):
    kalman_dloss = kalman_smooth(loss_arr)
    _, max_grad_idx, rhs = critical_points(kalman_dloss)
    # suggested_lr_idx_kalman = np.argmin(kalman_dloss)
    # If end_margin is too large, clip to 1/3 of the length.
    end_margin = min(end_margin, len(kalman_dloss) // 3)
    q = 0.5
    # Geometric weighting
    suggested_lr_idx = int(max_grad_idx**q * rhs ** (1 - q))
    # suggested_lr_idx = int((q - 1) * max_grad_idx + q * rhs)
    suggested_lr_idx = min(suggested_lr_idx, len(kalman_dloss) - end_margin)
    suggested_lr = lrs[suggested_lr_idx]
    return kalman_dloss, suggested_lr_idx, suggested_lr
