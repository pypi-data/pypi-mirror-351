"""
Gather outputs from training and evaluation runs into dataframes.

Functions like `get_outdir` and `version_labels_from_script_dir` are somewhat
related, and maybe they could be removed from _logging.py and combined with
the functions here to make an `exp.py` experiments related logging+collection
module.
"""

from pathlib import Path
import re
import polars as pl
import logging
import tbparse
from tqdm import tqdm
import multiprocessing as mp

_logger = logging.getLogger(__name__)

_is_num = re.compile(r"^\d+$")


def labels_from_dir(d):
    """
    Converts a path into strings from root to leaf, stopping at numbers.

    path/like/this/0/1/2 -> ["path", "like", "this"]
    """
    labels = []
    # add labels until you hit a number
    for p in [d] + list(d.parents):
        if _is_num.match(p.name):
            break
        labels.append(p.name)
    return list(reversed(labels))


_num_unit_ptr = re.compile(r"(\d+)([kM])")


def str_to_num(s):
    m = _num_unit_ptr.search(s)
    assert m is not None, s
    n = int(m.group(1))
    if m.group(2) == "k":
        n *= int(1e3)
    elif m.group(2) == "M":
        n *= int(1e6)
    return n


def check_skip(p, skip_dirs):
    for s in skip_dirs:
        if s in str(p):
            return True, s
    return False, None


def metrics(root_dir, skip_dirs=None):
    """Combines all metrics.csv files into a single dataframe.

    Args:
        root_dir: The root directory to search for metrics.csv files.
            Possibly the directory for a single experiment run, or a directory
            containing multiple experiments.
        skip_dirs: A list of directory names to skip.
            This was added for when metrics() is run on a directory containing
            multiple experiments, and you want to skip some of them.
    """
    skip_dirs = skip_dirs or []
    root_dir = Path(root_dir)
    dfs = []
    n_skips = 0
    for p in root_dir.rglob("metrics.csv"):
        skip, ptrn = check_skip(p, skip_dirs)
        if skip:
            n_skips += 1
            _logger.info(f"Skipping ({p}) by rule ({ptrn})")
            continue
        labels = labels_from_dir(p.parent)
        # Interpret "null" as None.
        df = pl.read_csv(p, null_values="null")
        for i, label in enumerate(labels):
            df = df.with_columns(pl.lit(label).alias(f"label_{i}"))
        dfs.append(df)
    df = pl.concat(dfs)
    if n_skips < len(skip_dirs):
        _logger.warning(
            f"Skipped {n_skips} dirs, for {len(skip_dirs)} skip dirs."
        )
    return df


def files(root_dir, filename, skip_dirs=None):
    """Create a dataframe describing files in the root_dir."""
    skip_dirs = skip_dirs or []
    root_dir = Path(root_dir)
    rows = []
    n_skips = 0
    n_labels = None
    for p in root_dir.rglob(filename):
        skip, ptrn = check_skip(p, skip_dirs)
        if skip:
            n_skips += 1
            _logger.info(f"Skipping ({p}) by rule ({ptrn})")
            continue
        labels = labels_from_dir(p.parent)
        if n_labels is None:
            n_labels = len(labels)
        assert n_labels == len(
            labels
        ), f"Expected {n_labels} labels, got {len(labels)}"
        ckpt_path = str(p)
        rows.append([ckpt_path] + labels)
    df = pl.DataFrame(
        rows, schema=["ckpt_path"] + [f"label_{i}" for i in range(n_labels)],
        orient="row"
    )
    if n_skips < len(skip_dirs):
        _logger.warning(
            f"Skipped {n_skips} dirs, for {len(skip_dirs)} skip dirs."
        )
    return df


def _to_df(events_path):
    reader = tbparse.SummaryReader(str(events_path), pivot=True)
    labels = labels_from_dir(events_path.parent)
    assert (
        labels[-1] == "tensorboard"
    ), f"Last must be tensorboard ({labels[-1]})"
    df = pl.from_pandas(reader.scalars)
    for i, label in enumerate(labels):
        df = df.with_columns(pl.lit(label).alias(f"label_{i}"))
    return df


def train_events(root_dir):
    """Uses tbparse to extract training events from tensorboard files.

    For tbparse, pivot is set to True.

    The dataframe returned from tbparse (with pivot=True) looks like:

        ┌───────┬─────────────┬──────────────────┬─────────────────┬───┬─────────────────────┬──────────────────────────┬─────────────────┬─────────────────┐
        │ step  ┆ epoch/train ┆ eval-time/val-ds ┆ grad_norm/train ┆ … ┆ mean_abs_err/val-ds ┆ mean_abs_err_mode/val-ds ┆ mean_nll/val-ds ┆ pred_nll/val-ds │
        │ ---   ┆ ---         ┆ ---              ┆ ---             ┆   ┆ ---                 ┆ ---                      ┆ ---             ┆ ---             │
        │ i64   ┆ f64         ┆ f64              ┆ f64             ┆   ┆ f64                 ┆ f64                      ┆ f64             ┆ f64             │
        ╞═══════╪═════════════╪══════════════════╪═════════════════╪═══╪═════════════════════╪══════════════════════════╪═════════════════╪═════════════════╡
        │ 0     ┆ 0.0         ┆ 11.285624        ┆ 1.295787        ┆ … ┆ 53.148785           ┆ 20.056328                ┆ 5.162835        ┆ 4.833945        │
        │ 1     ┆ 0.0         ┆ null             ┆ 1.284831        ┆ … ┆ null                ┆ null                     ┆ null            ┆ null            │

    And when pivot=False, it looks like:

        ┌───────┬─────────────────┬──────────┐
        │ step  ┆ tag             ┆ value    │
        │ ---   ┆ ---             ┆ ---      │
        │ i64   ┆ str             ┆ f64      │
        ╞═══════╪═════════════════╪══════════╡
        │ 0     ┆ epoch/train     ┆ 0.0      │
        │ 1     ┆ epoch/train     ┆ 0.0      │
        │ 2     ┆ epoch/train     ┆ 0.0      │
        │ 3     ┆ epoch/train     ┆ 0.0      │
        │ 4     ┆ epoch/train     ┆ 0.0      │
        │ …     ┆ …               ┆ …        │
        │ 61440 ┆ pred_nll/val-ds ┆ 2.517969 │
        │ 62464 ┆ pred_nll/val-ds ┆ 2.516451 │
        │ 63488 ┆ pred_nll/val-ds ┆ 2.518783 │
        │ 64512 ┆ pred_nll/val-ds ┆ 2.517922 │
        │ 65536 ┆ pred_nll/val-ds ┆ 2.518552 │
        └───────┴─────────────────┴──────────┘

    """
    root_dir = Path(root_dir)
    dfs = []
    with mp.Pool() as pool:
        # dfs = p.map(_to_df, list(root_dir.rglob("events.out.tfevents.*")))
        results = []
        for event_path in root_dir.rglob("events.out.tfevents.*"):
            results.append(pool.apply_async(_to_df, (event_path,)))
        for r in tqdm(results):
            dfs.append(r.get())
    return pl.concat(dfs)

    # for p in tqdm(list(root_dir.rglob("events.out.tfevents.*"))):
    #     # With pivot=False, the dataframe flattens all scalars into a single
    #     # column, and an additional "tag" column describes each individual row.
    #     # With pivot=True, each scalr gets its own column.
    #     reader = tbparse.SummaryReader(str(p), pivot=True)
    #     labels = labels_from_dir(p.parent)
    #     assert (
    #         labels[-1] == "tensorboard"
    #     ), f"Last must be tensorboard ({labels[-1]})"
    #     df = pl.from_pandas(reader.scalars)
    #     for i, label in enumerate(labels):
    #         df = df.with_columns(pl.lit(label).alias(f"label_{i}"))
    #     dfs.append(df)
    return pl.concat(dfs)
