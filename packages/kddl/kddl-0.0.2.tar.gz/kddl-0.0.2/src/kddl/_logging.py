from collections import defaultdict
import collections.abc
import inspect
import io
import re
import json
import logging
import logging.handlers
import math
from numbers import Number
import pathlib
import shutil
import sys
import time
from typing import Dict, Iterable, Optional, Sequence, Union, Tuple, Callable
import einops
import numpy as np
import polars as pl
import torch
import torch.utils.tensorboard as tb
import importlib
import rich.logging
import rich.text
import rich.highlighter
import tarfile
from contextlib import contextmanager
import queue
import plotext
# Avoiding having these as required dependencies.
# import plotly
# import matplotlib.pyplot as plt

"""
Logging
=======

The logging functionality in this module handles things like:

    - where to log
    - using Python's logging module
    - timing things 
    - measuring things with numbers
        - increasing vs. decreasing
        - accumulated calculation vs. one-off
        - best-so-far tracking *
    - saving Pytorch models *
    - logging training/evaluation data *

The stars are placed next to the categories that are training-loop specific.
If a logging routine needs to know what epoch it is, then it's very much
inseparable from the training-loop. I'm pointing this out, as it's conceivable
that these two categories of logging will be separated into different modules
at some point; the more general logging functions might be used for other
projects.

A lot more can be said about the training-loop logging.

tl;dr 
-----
Trainables return a dictionary like {"metrics": .., "images": ..., "figures": ...,}

Training-loop logging
=====================
Logging for a training-loop is a great source of edge cases, thwarting
attempts to create separation between parts of the training apparatus. 
If you blur your eyes a bit, the concerns of different parts of the training 
aparatus form a top-down gradient. At the top, the mundane but important things
like where to store data is handled. In the middle, we have the training-loop
management which knows how to setup and run the endless loop over the data
to train and periodiacally evaluate a model, yet it doesn't care at all about
what model it is actually training. At the very bottom is the actual Pytorch
model. It has been given quite a simple life thanks to the work of the 
Trainable—the great encapsulator of entropy—that knows how to pull a sample from
the dataset and feed it to the model. If you want to re-use a PyTorch Dataset
for multiple models, you really do need something in the middle than
massages the data into each model. But that is not the only work of the 
Trainable—the Trainable is the only one who has enough context to report on how 
good or bad the training is actually progressing, so it gets the task of
gathering up the data to be logged. And this is where logging comes in to make 
things difficult. The Trainable should be free to log whatever it wants, from
metrics like loss, to images and figures and weight snapshots. But all of
this data cannot be handed back to the training-loop without being specific 
about what each piece of data is, as different types of data need to be 
handled differently. For example, the TensorBoard API requires datatypes to
be separated, as the API calls are different for different types, for example,
SummaryWriter.add_scalar() vs. SummaryWriter.add_histogram(). The W&B API takes
a different approach and accepts data as a dictionary where the values are
object instances of wandb classes, each data type using a different class.

The consequence of Tensorboard's approach is that you need to attach some sort
of metadata to your data that will allow you to create some big if-else block 
that routes data to the suitable Tensorboard function call. Alternatively,
you could call the Tensorboard API directly in the Trainable. This latter 
approach feels like it would be frustrating, as suddenly, your Trainable 
object needs to know about the training-loop (what step etc). What if you
want to run the evaluation outside of a training loop, say at test time? So
many little details to handle. So your choice with tensorboard is to either
log data from very deep in your stack, or pass around some metadata that allows
you to build a big if-else block at some point.

In comparison, if one imagined committing fully to W&B, the Trainable
can create the wandb objects directly and return a data dictionary that doesn't 
need to be inspected at any point before handing off to the wandb API. This
is very seductive. W&B has nicely observed that the decision of what type
of data to be logged is made when you collect the data, and shouldn't need to
be made again when you go to actually call your logging utility. You can
view the set of wandb datatypes here: 

    https://github.com/wandb/wandb/blob/latest/wandb/__init__.py

Another interesting file is the one below, which contains the `WBValue` class
definition. The `WBValue` class is the abstract parent class for anything 
that can be logged with W&B api. It pressages some of the abstractions one 
might end up having to make.

https://github.com/wandb/wandb/blob/d622ee37b232e54addcd48e9f92d9198a3e2790b/wandb/sdk/data_types/base_types/wb_value.py#L56

Another class, `Media` shows how the `WBValue` parent class separates as a tree
into different types of data formats.

https://github.com/wandb/wandb/blob/d622ee37b232e54addcd48e9f92d9198a3e2790b/wandb/sdk/data_types/base_types/media.py#L31

What to actually do
-------------------
I don't want to stop using Tensorboard, I don't want to call tensorboard 
logging calls directly in the Trainable, and I want the option of using 
alternative logging tools like W&B in the future. So it seems like there
will be a if-else block for data routing. What is left is to choose what is the
form of metadata this is switched upon. We could go with classes, like how
wandb seems to do it, or we could go with just strings like "metrics", "images", 
etc. I think this latter approach is nicer; I don't want to have to create 
new classes just for the sake of being distinguished in some if-else chain.
Having said that, classes will probably wrap most of the data types anyway,
for example, numeric data is already wrapped in the Metric class which 
records the increasing or decreasing nature of a metric.

The Tensorboard and wandb API documentation homepages:

    https://pytorch.org/docs/stable/tensorboard.html
    https://docs.wandb.ai/
"""


_logger = logging.getLogger(__name__)


class Highlighter(rich.highlighter.ReprHighlighter):
    def __init__(self):
        super().__init__()
        self.highlights.append(
            # Matches (<path>)       (a path in brackets)
            # The default path regex assumes starting '/'.
            r"\((?P<path>((([-\w._+]+)*)\/[\w._+-]*)*)\)"
        )


_console = rich.console.Console(highlighter=Highlighter())
CONSOLE_EVAL_STYLE = "color(2)"
CONSOLE_TRAIN_STYLE = "color(3)"
CONSOLE_SKIP_PREFIX = "[CONSOLE]"


class KeepFirstRotatingFileHandler(logging.handlers.RotatingFileHandler):
    """Logger that keeps the first log, and then rotate as normal.

    The initial log messages are usually the most important.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._first = True

    def rotation_filename(self, default_name):
        if self._first:
            self._first = False
            return default_name + ".first"
        else:
            return super().rotation_filename(default_name)


def setup_logging(level, use_rich=True, show_time=False):
    """Default logging setup.

    The default setup:
        - makes the root logger use the specified level
        - adds stdout as a handler
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    if use_rich:
        console_handler = rich.logging.RichHandler(
            console=_console,
            show_time=show_time,
            omit_repeated_times=False,
            show_level=True,
            show_path=True,
            rich_tracebacks=True,
        )
    else:
        console_handler = logging.StreamHandler(stream=sys.stdout)

    def should_log_to_console(record):
        hard_coded_msg_start = "[CONSOLE]"
        return not record.msg.startswith(hard_coded_msg_start)

    # The training loop has a very specific console format that is printed
    # manually with a Rich Console object. So don't send training loop updates
    # to the console handler.
    console_handler.addFilter(should_log_to_console)
    root_logger.addHandler(console_handler)


def enable_file_logging(log_path: pathlib.Path | str):
    """Enable logging to a file.

    Rolling logging is used—additional files have ".1", ".2", etc. appended.
    """
    root_logger = logging.getLogger()
    file_handler = KeepFirstRotatingFileHandler(
        log_path, maxBytes=(2 ** (10 * 2) * 5), backupCount=3
    )
    formatter = logging.Formatter(
        "%(asctime)s - %(filename)s:%(lineno)d: [%(levelname)8s] - %(message)s"
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)


def get_patch_versions(
    base_dir: pathlib.Path | str, labels: Optional[Sequence[str]] = None
):
    base_dir = pathlib.Path(base_dir)
    if labels is None:
        labels = []
    base_dir = base_dir.joinpath(*labels)
    if not base_dir.exists():
        raise FileNotFoundError(f"Directory {base_dir=} does not exist.")
    versions = [
        int(p.name)
        for p in base_dir.iterdir()
        if p.is_dir() and p.name.isdigit()
    ]
    return versions


def get_last_outdir(
    base_dir: pathlib.Path | str, labels: Optional[Sequence[str]] = None
):
    base_dir = pathlib.Path(base_dir)
    versions = get_patch_versions(base_dir, labels)
    last_version = max(versions)
    out_dir = base_dir / str(last_version)
    return out_dir


def get_outdir(
    base_dir: pathlib.Path | str, labels: Optional[Sequence[str]] = None
):
    """Creates the directory in which all logging should be stored.

    The directory will have the form:

        /basedir/label1/label2/label3/<num>

    Where <num> is incremented so that a fresh directory is always created,
    unless resume = True, in which the most recent directory (with the largest
    number) is returned.

    Returns:
        A tuple: the path to the new directory, and the version number.
    """
    base_dir = pathlib.Path(base_dir)
    if labels is None:
        labels = []
    base_dir = base_dir.joinpath(*labels)
    if not base_dir.exists():
        base_dir.mkdir(parents=True)
    versions = [
        int(p.name)
        for p in base_dir.iterdir()
        if p.is_dir() and p.name.isdigit()
    ]
    use_version = max(versions, default=-1) + 1
    is_probably_too_many = use_version >= 1000
    if is_probably_too_many:
        _logger.warning(f"Reached outdir version {use_version}.")
    out_dir = base_dir / str(use_version)
    out_dir.mkdir()
    return out_dir


def version_labels_from_script_dir():
    """Get the version labels from a script's directory.

    Example. For a script like `experiments/0/test/0/10/20/1/train.py`,
    return [0, 10, 20, 1]. This is the numeric sequence closest to the script,
    ending at the first non-numeric directory.

    Why can't stack_idx be always set to -1? I think it used to
    be -1, but for a reason I can't remember, it was changed to 1, with the
    assumption that it was always called from the script in question. The
    reason might have been that if the root script was ever debugged or
    profiled, then the root script would change. Therefore, it seemed more
    robust (dispite seemingly less so) to specify manually the depth of the
    script in question.

    To be a bit more robust to things like debugging, profiling, and the use of
    the function within other functions, this function will now search the stack
    from the bottom up and choose the first script that has a path that looks
    like a versioned path: some/dir/structure/0/1/2/3/train.py. Specifically,
    we will make the rule that the script's parent directory must be a number.

    Args:
        caller_depth: if you are calling this function from the script in
            question, then caller_depth=0. If you expect that the script is
            instead calling your function, then caller_depth=2, etc.
    """
    is_num = re.compile(r"^\d+$")
    path = None
    for frame in reversed(inspect.stack()):
        path = pathlib.Path(frame.filename)
        if is_num.match(path.parent.name):
            break
    if path is None:
        raise ValueError("No versioned script found in stack.")
    labels = []
    for p in path.parents:
        if not is_num.match(p.name):
            break
        labels.append(p.name)
    return list(reversed(labels))


def script_output(base_dir: pathlib.Path | str, patch: Optional[int] = None):
    """Get the direction of the latest (or chosen patch version) run."""
    base_dir = pathlib.Path(base_dir)
    ver_parts = version_labels_from_script_dir()
    patch_versions = get_patch_versions(base_dir, ver_parts)
    most_recent = max(patch_versions)
    if patch is None:
        patch = most_recent
    if patch not in patch_versions:
        raise ValueError(f"Patch {patch} not found in {patch_versions=}")
    ver_parts += [str(patch)]
    out_dir = base_dir / pathlib.Path(*ver_parts)
    assert out_dir.exists()
    return out_dir, ver_parts


def script_existing_versions(base_dir) -> Tuple[Sequence[str], Sequence[int]]:
    ver_parts = version_labels_from_script_dir()
    patch_versions = get_patch_versions(base_dir, ver_parts)
    patch_versions.sort()
    return ver_parts, patch_versions


def snapshot_parent_folder(out_dir, python_file):
    parent = pathlib.Path(python_file).parent
    shutil.copytree(
        parent,
        out_dir / "src_snapshot" / parent.name,
        ignore=shutil.ignore_patterns("*pyc", "*__pycache__"),
    )


def snapshot_module(out_dir, module_name):
    """Snapshot a module's source code."""
    module = importlib.import_module(module_name)

    module_dir = pathlib.Path(inspect.getfile(module)).parent
    shutil.copytree(
        module_dir,
        out_dir / "src_snapshot" / module_name,
        ignore=shutil.ignore_patterns("*pyc", "*__pycache__"),
    )


def snapshot_importing_script(out_dir):
    """Snapshot the script that imported your module."""
    # TODO: need to be smarter in order to avoid Typer module.
    # stack[0]: this function
    # stack[1]: where this function is called (e.g. in root experiment file)
    # stack[2]: external caller (importer)
    STACK_IDX = 2
    frame = inspect.stack()[STACK_IDX]
    logging.info(f"Importing file estimated to be: {frame.filename}")
    snapshot_dir = out_dir / "src_snapshot"
    snapshot_dir.mkdir(parents=False)
    shutil.copy2(frame.filename, snapshot_dir / "calling_script.py")


# =============================================================================
# [begin] Functionality to merge experiment runs
# =============================================================================
class _PathNode:
    """A tree that holds overlapping directory structures on top of each other.

    In running and re-running experiments, we often create two or more directory
    trees that partially overlap. We want to create a single tree so that
    the next consumer can easily find things. We don't want to copy, so we will
    make a link tree. This class creates a tree structure that tracks the
    overlapping directory trees. The point is that we want to identify the
    top-most folders that are unique to one of the experiment output
    directories—this allows us to create a link to this whole folder, rather
    than the individual folders within it. Often when we have to re-run a
    small number of failed sub-experiments, a small few branches of the
    original tree must be linked at a finer scale.

    Quick way to understand this class: Imagine a "backbone" tree structure
    over which we will draw multiple data directory trees.

    Note on terminology: directories that are a source of data will be called
    targets, as they will be the targets of symbolic links.
    """

    def __init__(self, dirname, parent):
        self.dirname = dirname
        # New tree root is only node with no roots.
        self.target_roots = []
        self.children = {}
        self.parent = parent

    @staticmethod
    def create_root():
        return _PathNode("", None)

    def add_child(self, dirname, root):
        if dirname not in self.children:
            self.children[dirname] = _PathNode(dirname, self)
        self.children[dirname].target_roots.append(root)
        return self.children[dirname]

    def is_root(self):
        return self.parent is None

    def is_leaf(self):
        return len(self.children) == 0

    def up_path(self):
        if self.is_root():
            return pathlib.Path("./")
        else:
            return self.parent.up_path() / "../"

    def n_targets(self):
        return len(self.target_roots)

    def down_path(self):
        if self.is_root():
            return pathlib.Path(self.dirname)
        else:
            return self.parent.down_path() / self.dirname

    def __repr__(self):
        res = f"Node({self.dirname}, {self.parent})"
        if self.parent is None:
            res += " (root)"
        return res

    def get_link_ends(self, choose_last=False):
        """Get tuples (src, target) for src.symlink_to(target) calls.

        As we create relative links, we need to create a link that surfaces
        up the link directory and then descends down the data directory.

        We only go as far down the tree as we need. If a has been
        created by only 1 experiment run, then the folder itself can be linked
        to. If multiple runs have the same folder, then they have each
        partially completed the sub-experiments held in this folder, and we
        must create more fine grained links.

        TODO: this would be better as a single pass, rather than the down and
        up done here. Then the up_path and down_path can be gotten rid of.

        choose_last: if True, then if there are two matching directories, the
            one in the target root that is later in the target_dirs list will
            be chosen (simple overwrite). If False, then matching directories
            results in an error.
        """
        if self.is_leaf():
            n_targets = self.n_targets()
            if n_targets > 1:
                if not choose_last:
                    raise ValueError(
                        f"Two targets ({self.target_roots}) for same leaf "
                        f"{self.down_path()}. Choose last by setting "
                        "choose_last=True."
                    )
                else:
                    _logger.info(
                        f"Multiple matching targets for {self.down_path()}."
                        f" Choosing the last, ({self.target_roots})"
                    )
            elif n_targets == 0:
                assert self.is_root(), "Only root nodes can have no targets."
            assert len(self.target_roots) > 0, f"{self.down_path()=}"
            res = [
                (
                    self.down_path(),
                    self.up_path() / self.target_roots[-1] / self.down_path(),
                )
            ]
        else:
            # Non leaf. We will choose to link the folder itself, or descend
            # down the tree.
            child_targets = {
                t for c in self.children.values() for t in c.target_roots
            }
            descend = len(child_targets) > 1
            # If this non-leaf node has only a single target, we can link this
            # folder and not the children.
            if descend:
                res = []
                for child in self.children.values():
                    res.extend(child.get_link_ends(choose_last))
            else:
                assert (
                    self.n_targets() == 1
                ), "This could be triggered if a target directory was empty."
                res = [
                    (
                        self.down_path(),
                        self.up_path()
                        / self.target_roots[0]
                        / self.down_path(),
                    )
                ]
        return res


def _overlay_tree(
    src_root: _PathNode,
    target_root_dir: pathlib.Path,
    rel_target: pathlib.Path,
    filter_in: Callable[[pathlib.Path], bool],
):
    """
    Add the target directory structure (where the experiment runs are) to the
    tree held in the root node, `src_root`. The tree structure will get fleshed
    out in all branches that it doesn't yet have.

    We do a BFS through the the target directory and add a node for each
    relevant directory. The "adding" will either create a new node or add to
    the list of target directories connected to the existing node.
    """
    if not src_root.is_root():
        raise ValueError("src_root must be root node.")
    # BFS
    q = queue.Queue()
    for child in target_root_dir.iterdir():
        _logger.debug(f"Adding {child=}")
        q.put((src_root, child))
    while not q.empty():
        parent, path = q.get()
        if not filter_in(path):
            _logger.debug(f"Skipping {path=}")
            continue
        node = parent.add_child(path.name, rel_target)
        # If the path is a directory, add any children
        if path.is_dir():
            for grandchild in path.iterdir():
                q.put((node, grandchild))
    if len(src_root.children) == 0:
        _logger.warning("No children added to the tree. Check your filter.")
    _logger.info(f"Added {target_root_dir} as target for {src_root.dirname=}")


def _common_parent(path, other):
    """Splits a path into common and unique relative to another path.

    We calculate

    This is a messy implementation of what will probably be possible in
    python 3.12 with path.relative_to(other, walk_up=True).

    Edge cases are not really handled seriously, so use with caution.
    """
    ancestors = zip(reversed(other.parents), reversed(path.parents))
    common = None
    unique = pathlib.Path("./")
    other_parents = list(reversed(other.parents))
    parents = list(reversed(path.parents))
    for i, p in enumerate(parents):
        if i < len(other_parents) and other_parents[i].samefile(p):
            common = p
        else:
            unique = pathlib.Path(*[p.name for p in parents[i:]])
            break

    for o, p in ancestors:
        if o.name == p.name:
            assert o.samefile(p)
            common = o
        else:
            unique = o
    return common, unique


def merge_as_links(
    link_root: pathlib.Path,
    target_dirs: Iterable[pathlib.Path],
    filter_in: Callable[[pathlib.Path], bool],
    link_rename: Optional[Callable[[pathlib.Path], pathlib.Path]] = None,
    choose_last: bool = False,
    dry_run: bool = False,
):
    """Create a tree of links into the overlapping target_dirs.

    Used for combining multiple disjoint runs of an experiment when the first
    (or more) runs partially fail.

    Args:
        link_root: the existing (and empty) directory to create the tree.
        target_dirs: 2 or more roots of directories that you want to merge.
        filter_in: a function called on every subdirectory in the target_dirs
            to decide if the directory is to be considered part of the tree.
            Typically, you want to add every directory like 0/1, 0/1/0,
            0/1/0/model-name, 0/1/0/model-name/ds-name, or whether pattern
            you are using until you get to the final directory that contains
            the run data, such as a checkpoint_best_loss.pth.
        choose_last: if True, then if there are two matching directories, the
            one in the target root that is later in the target_dirs list will
            be chosen (simple overwrite). If False, then matching directories
            results in an error.
    """
    if not link_root.exists():
        raise ValueError("The link root must exist.")
    if any(link_root.iterdir()):
        # This could be changed to a warning or removed completely if a use
        # case is encountered. Keeping for now.
        raise ValueError(f"Link dir isn't empty. {list(link_root.iterdir())=}")
    root_node = _PathNode.create_root()
    for t in target_dirs:
        _, unique_ancestor = _common_parent(t, link_root)
        rel_target = unique_ancestor / t.name
        assert rel_target is not None
        _overlay_tree(root_node, t, rel_target, filter_in)
    # Get all the link ends.
    link_ends = root_node.get_link_ends(choose_last)
    # Prepend to src root.
    link_ends = [(link_root / src, target) for src, target in link_ends]

    # Create the links.
    for src, target in link_ends:
        resolved_target = (src / "../" / target).resolve()
        if not resolved_target.exists():
            raise ValueError(f"Target {src/target} does not exist.")
        else:
            # TODO: The renaming should be handled in the overlay tree. It's
            # a little tricky to do this though, as all nodes will need 
            # extra accounting information to track when they overlap due to
            # their new name, but keep their old name for the link target.
            # For the moment, we will just do the work here by renaming the 
            # link src before creating it. This means that the below check
            # for src.exists() will be skipped when link_renaming is used.
            # If the renaming is handled in the overlay_tree, this check can
            # be added back in.
            if link_rename is not None:
                prev = src
                src = link_rename(src)
                _logger.info( f"Renaming link {prev} to {src}")
            _logger.info(f"Link {src} → {resolved_target}")
            if dry_run:
                continue
            if src.exists():
                if link_rename is not None:
                    # TODO: See the above note. tl;dr remove this continue once
                    # link renaming is done in the overlay tree.
                    continue
                raise ValueError(f"Source {src} already exist.")
            src.parent.mkdir(parents=True, exist_ok=True)
            src.symlink_to(target)
    if dry_run:
        _logger.info("Dry run. No links created.")
        return


# =============================================================================
# [end] Functionality to merge experiment runs
# =============================================================================


@contextmanager
def back_up(
    path, copy_to: pathlib.Path | str, compress=True, remove_original=False
):
    """Back up a file or directory on exit."""
    copy_to = pathlib.Path(copy_to)
    if not copy_to.exists():
        raise ValueError(f"Output directory {copy_to} should exist.")
    try:
        yield
    finally:
        if compress:
            folder_name = path.name
            tar_path = copy_to / f"{folder_name}.tar.gz"
            with tarfile.open(tar_path, "w:gz") as tar:
                # I'm not sure if leaving out the arcname will cause the
                # path's parent to be included in the hierarchy.
                tar.add(path, arcname=folder_name)
            _logger.info(f"Compressed {path} to {tar_path}")
        else:
            shutil.copytree(path, copy_to)
            _logger.info(f"Copied {path} to {copy_to}")
        if remove_original:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            _logger.info(f"Removed {path}")


def load_model(
    model, checkpoint_path: Union[str, pathlib.Path], map_location=None
):
    checkpoint_path = pathlib.Path(checkpoint_path)
    if not checkpoint_path.exists():
        raise FileNotFoundError(
            f"Checkpoint file/folder ({checkpoint_path}) not found."
        )
    if checkpoint_path.is_dir():
        checkpoint_path = list(checkpoint_path.glob("*.pth"))[-1]

    _logger.info(f"Loading model from ({checkpoint_path}).")
    checkpoint_state = torch.load(
        # Specify weights_only=True, as it becomes the default in a later
        # Pytorch version (>2.4), and until then, there is a verbose warning
        # that can be silenced by specifying weights_only=True.
        checkpoint_path,
        map_location,
        weights_only=True,
    )
    model_state = checkpoint_state["model"]
    # Deal with "_orig_mod"
    # state = {}
    # for k, v in model_state.items():
    #     if k.startswith("_orig_mod."):
    #         k = k[10:]
    #     state[k] = v
    # model_state = state
    model.load_state_dict(model_state)


def load_model_and_optimizer(
    model,
    checkpoint_path: Union[str, pathlib.Path],
    optimizer: Optional[torch.optim.Optimizer] = None,
    scheduler: Optional[torch.optim.lr_scheduler._LRScheduler] = None,
):
    checkpoint_path = pathlib.Path(checkpoint_path)
    if not checkpoint_path.exists():
        raise FileNotFoundError(
            f"Checkpoint file/folder ({checkpoint_path}) not found."
        )
    if checkpoint_path.is_dir():
        checkpoint_path = list(checkpoint_path.glob("*.pth"))[-1]

    _logger.info(f"Loading model from ({checkpoint_path}).")
    checkpoint_state = torch.load(checkpoint_path)
    model_state = checkpoint_state["model"]
    model.load_state_dict(model_state)
    if optimizer:
        optimizer.load_state_dict(checkpoint_state["optimizer"])
    if scheduler:
        scheduler.load_state_dict(checkpoint_state["scheduler"])


def save_model(model, path: pathlib.Path, optimizer=None, scheduler=None):
    # Should work with compiled models:
    # https://pytorch.org/get-started/pytorch-2.0/#serialization
    _logger.info(f"Saving model to ({path})")
    if not path.parent.exists():
        path.parent.mkdir(parents=True)
    state = {
        "model": model.state_dict(),
    }
    if optimizer:
        state.update({"optimizer": optimizer.state_dict()})
    if scheduler:
        state.update({"scheduler": scheduler.state_dict()})
    torch.save(state, path)


# A quick hack to allow infinite values to be ignored for the purposes of
# the 2D project image being computed without infinite values.
IGNORE_INF = False
class Meter:
    """An online sum and avarage meter."""

    def __init__(self, name=None):
        self.reset()
        self.name = name

    @property
    def avg(self):
        if self.count == 0:
            res = float("nan")
        else:
            res = self.sum / self.count
        return res

    def reset(self):
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        if isinstance(val, torch.Tensor):
            _logger.warning(
                "Meter.update() called with a tensor. Maybe you forgot to call"
                "item()?"
            )
        if IGNORE_INF and math.isinf(val):
            _logger.warning(
                "Meter.update() called with inf. Ignoring this value."
            )
            return
        self.sum += val * n
        self.count += n

    def __str__(self):
        res = f"{self.name} " if self.name else "Meter"
        res += f"(average -- total) : {self.avg:.4f} -- ({self.sum:.4f})"
        return res


class MovingAverageMeter:
    def __init__(self, beta: float, name=None):
        """
        beta: the weighting given to the new value.
        """
        self.reset()
        self.beta = beta
        self.name = name
        self._avg = None

    def reset(self):
        self._avg = None
        self.count = 0
        self.sum = 0

    @property
    def avg(self) -> float:
        return self._avg if self._avg is not None else 0

    def update(self, val, n=1):
        self.sum += val * n
        self.count += n
        if self._avg is None:
            self._avg = val
        else:
            b = self.beta**n
            self._avg = (1 - b) * self._avg + b * val

    def __str__(self):
        res = f"{self.name} " if self.name else "Meter"
        res += f"(smoothed -- total) : {self.avg:.4f} -- ({self.sum:.4f})"
        return res


class Timer:
    """A little timer to track repetitive things.

    Rates/durations are monitored with exponential moving averages.

    All times are in seconds (fractional).

    There is two main use cases:

    The timer supports the context manager protocol, so you can use it like:

        timer = Timer()
        with timer:
            # Do something
        print(f"Duration: {timer.elapsed()}")

    The original motivation for this feature was to track how long it took to
    run validation, while keeping a rolling average of the validation time.
    """

    def __init__(self):
        self.w = 0.1
        self._loop_start = None
        self._rolling_duration = None
        self._first_start = None
        self._prev_elapsed = None

    @staticmethod
    def create_and_start() -> "Timer":
        timer = Timer()
        timer.restart()
        return timer

    def restart(self) -> Optional[float]:
        """Start or restart the timer.

        Returns the duration of the previous loop, or None on the first call.
        """
        t_now = time.monotonic()
        # First call?
        if self._first_start is None:
            self._first_start = t_now
            self._loop_start = t_now
        else:
            # Has the timer been stopped? If so, start it again.
            if self._loop_start is None:
                self._loop_start = t_now
                assert self._prev_elapsed is not None
            else:
                # From second call, we have a new elasped time.
                self._prev_elapsed = t_now - self._loop_start
            self._increment_rolling(self._prev_elapsed)
            self._loop_start = t_now
            return self._prev_elapsed

    def _increment_rolling(self, elapsed):
        if self._rolling_duration is None:
            self._rolling_duration = elapsed
        else:
            assert self._rolling_duration is not None
            self._rolling_duration = (
                self.w * elapsed + (1 - self.w) * self._rolling_duration
            )

    def stop(self) -> Optional[float]:
        """Stop the timer.

        It's fine to stop a timer that hasn't been started.
        """
        if self._loop_start is None:
            return
        self._prev_elapsed = time.monotonic() - self._loop_start
        self._increment_rolling(self._prev_elapsed)
        self._loop_start = None
        return self._prev_elapsed

    def elapsed(self) -> float:
        """
        The current elapsed time, or previous if the timer is stopped.

        If the timer has never been started, an error will be raised.
        """
        if self._loop_start is None:
            if self._prev_elapsed is None:
                raise ValueError("Not yet started.")
            return self._prev_elapsed
        return time.monotonic() - self._loop_start

    def total_elapsed(self) -> float:
        if self._first_start is None:
            raise ValueError("Not yet started")
        return time.monotonic() - self._first_start

    def rolling_duration(self) -> float:
        if self._rolling_duration is None:
            return self.elapsed()
        else:
            return self._rolling_duration

    def __enter__(self):
        self.restart()

    def __exit__(self, *args):
        self.stop()


###############################################################################
# Training-loop specific
# Below, the logging utilities are specific to model training.
###############################################################################



def log_scheduler(lr_min, lr_max, lr_last, scheduler_name, lrs, fig_path=None):
    """
        Args:
            file_path: if provided, the figure will be saved to this path.
                The extension of the file is interpreted by plotext—an .html
                extension will result in html output.

    """
    info = (
        f"Learning rate schedule:\n"
        f"\tscheduler: {scheduler_name}\n"
        f"\tmin lr: {lr_min:.4e}\n"
        f"\tmax lr: {lr_max:.4e}"
        f"\tlast lr: {lr_last:.4e}"
    )
    _logger.info(info)
    _console.print(
        info,
        highlight=False,
        style=CONSOLE_TRAIN_STYLE,
    )
    # Plot lrs
    plotext.plot(np.arange(len(lrs)), lrs, label="lr")
    # For console, just use plotext's output.
    plotext.show()
    # For logging, use text.
    as_text = plotext.build()
    _logger.info(
        f"Learning rate schedule:\n"
        f"{as_text}"
    )
    # Save to file also.
    if fig_path is not None:
        plotext.save_fig(fig_path)


def log_step(
    epoch: int,
    total_epochs: int,
    batch: int,
    total_batches: int,
    epoch_timer: Timer,
    batch_timer: Timer,
    loss: float,
    lr: float,
    model_mean: float,
    model_sd: float,
    grad_norm: Optional[float] = None,
):
    """
    Prints to console, and logs to default logger, but skips stream logger.
    """
    elapsed_min, elapsed_sec = divmod(round(epoch_timer.elapsed()), 60)
    # Floor total minutes to align with batch minutes.
    total_hrs, total_min = divmod(int(epoch_timer.total_elapsed() / 60), 60)
    # +1 as we are counting how many are done, not listing those done.
    if batch > total_batches:
        _logger.warning(
            f"Batch number ({batch}) exceeds total batches ({total_batches})"
        )
    n_epochs = epoch + 1
    n_batches = batch + 1
    loss_val = f"{loss:.3f} " if loss > 1e-3 else f"{loss:.3e} "
    _console.print(
        f"ep {n_epochs}/{total_epochs} | "
        f"🪜 {n_batches:>4}/{total_batches} "
        f"({n_batches/total_batches:>4.0%}) "
        f"{round(1/batch_timer.rolling_duration()):>2}/s | "
        f"⏲  {elapsed_min:>1}m{elapsed_sec:02d}s "
        f"Σ{total_hrs:>1}h{total_min:02d}m | "
        f"ℒ {loss_val} | "
        + (f"‖∇‖ {grad_norm:.3f} | " if grad_norm is not None else "")
        + f"lr {lr:.2e} | "
        f"出 μ {model_mean:>3.2f} σ {model_sd:>3.2f}".replace("e-0", "e-"),
        highlight=False,
        style=CONSOLE_TRAIN_STYLE,
    )
    # For the logger, be more verbose (no emojis).
    _logger.info(
        f"[CONSOLE] epoch: {n_epochs}/{total_epochs} "
        f"step:{n_batches:>4}/{total_batches} "
        f"({n_batches/total_batches:>3.0%}) "
        f"{round(1/batch_timer.rolling_duration()):>2}/s | "
        f"elapsed: {elapsed_min:>1}m:{elapsed_sec:02d}s "
        f"({total_hrs:>1}h:{total_min:02d}m) | "
        f"loss: {loss_val} | "
        f"learning-rate: {lr:.3e} | "
        f"out mean (sd): {model_mean:>3.2f} ({model_sd:>3.2f})"
    )


def log_metric_improvement(
    metric, prev_best, epoch, prev_best_epoch, step=None, prev_best_step=None
):
    before = f"epoch {prev_best_epoch}"
    now = f"epoch {epoch}"
    if step is not None:
        if prev_best_step is None:
            raise ValueError("prev_best_step must be provided if step is.")
        before = f"epoch {prev_best_epoch} step {prev_best_step}"
        now = f"epoch {epoch} step {step}"

    gt_lt = ">" if metric.increasing else "<"
    # Console get's a custom message.
    _console.print(
        f"Improved metric ({metric.name}): ".ljust(40)
        + f"{metric.value:.5f} {gt_lt} {prev_best:.5f} "
        f"({now} {gt_lt} {before})",
        highlight=False,
        style=CONSOLE_EVAL_STYLE,
    )
    _logger.info(
        f"[CONSOLE] Improved metric ({metric.name}): "
        + f"{metric.value:.5f} {gt_lt} {prev_best:.5f} "
        f"({now} {gt_lt} {before})"
    )


def loss_metric(loss):
    """
    A convenience function for creating a loss metric.

    The "convenience" being avoiding mistakenly creating a broken loss metric
    by giving it the wrong name (other functionality depends on "loss" being
    the label) or the wrong increasing/decreasing nature, or not checkpointing
    on loss.

    Loss metric is always a good-increasing metric that is checkpointed.
    """
    return Metric("loss", loss, increasing=False, checkpointed=True)


class Metric:
    """A quantity like like loss or accuracy is tracked as a Metric.

    In addition to the value itself, functions that consume metrics typically
    need to know:
        - a name for the metric
        - whether a higher value is better or lower is better

    Class vs. tuples
    ----------------
    Tuples could be used to pass around these values. However, a Metric class
    makes the implicit explicit, and hopefully makes things easier to both
    understand and use. A further benefit of a class is that there is an
    option to make the Meter class be a metric (either duck typing or via
    sub-classing) in order to avoid the very mild annoyance of having to
    meter.avg every time you want to make a metric from a meter.
    """

    def __init__(
        self,
        name: str,
        value: Number,
        increasing: bool = True,
        checkpointed: bool = False,
    ):
        """
        Args:
            checkpointed: Whether we should record checkpoints for the best
                values of this metric.
        """
        self.name = name
        self.value = value
        self.increasing = increasing
        self.checkpointed = checkpointed

    def __str__(self):
        return f"{self.name}={self.value:.5f}"

    def is_better(self, other):
        """Whether the current metric is better than the other metric.

        Args:
            than (Metric or Number): The metric to compare to.

        Returns:
            True if this metric is better than the other metric.
        """
        if isinstance(other, Metric):
            if self.increasing != other.increasing:
                raise ValueError(
                    "Cannot compare an increasing metric to a decreasing one:"
                    f" ({str(self)}, {str(other)})"
                )
            other_val = other.value
        else:
            other_val = other
        if self.increasing:
            return self.value > other_val
        else:
            return self.value < other_val


"""
Previously, the generic class was used for logging data. However, to use this
the evaluate() would return a map whose keys were used to interpret the type
of data. For example, "plotly" meant the value of the dict contained plotly
figures. This was fine until in addition to the input/output figures, a
latent space figure was also to be recorded. So either the structure of the
dict values needed another level, or the keys didn't have to one-to-one with
a data type. Going with the latter option, we could add a "dtype" string
parameter to the LogData object, or we could use separate classes. Both seem
fine. It seems likely that different datatypes might need different or extra
fields, so lets go with classes for now. As the results dict keys are now
freed up to be used as labels, the data objects themselves don't need a label.

class LogData:
    def __init__(self, label: str, content: Any):
        self.label = label
        self.content = content
"""


class PlotlyFigureList:
    """Wrap one or more Plotly figures for logging (e.g. via Tensorboard)."""

    def __init__(self, figs):
        self.figs = figs


class MplFigureList:
    """Wrap one or more MPL figures for logging (e.g. via Tensorboard)."""

    def __init__(self, figs):
        self.figs = figs


class PlotlyVideo:
    """Wrap a list of Plotly figures for logging as a video (e.g. via Tensorboard)."""

    def __init__(self, figs):
        self.figs = figs


class Images:
    """Wrap a list of images for logging (e.g. via Tensorboard)."""

    def __init__(self, images):
        """
        Args:
            images: (B, 3, H, W) tensor of images.
        """
        self.images = images


class Embeddings:
    """Wrap an embedding matrix for logging (e.g. via Tensorboard)."""

    def __init__(self, embeddings: torch.Tensor, labels: Iterable[str]):
        """Args:
        embedding: A 2D tensor of shape (num_embeddings, embedding_dim).
        """
        self.embeddings = embeddings
        self.labels = labels
        # Not yet connected.
        self.label_img = None


class MetricTracker:
    """Monitors metrics and the epochs they were seen in.

    It's common to write a conditional like:

        if new_metric.is_better(existing_best):
            do_something()
            existing_best = new_metric

    This class does that here, so other classes like checkpointers don't have
    to. This class originally came about by gutting the functionality from
    the ModelCheckpointer when it was needed elsewhere.
    """

    # Class variables
    HISTORY_FILENAME = "metrics.csv"
    BEST_FILENAME = "best_metrics.json"
    EpochStep = Tuple[int, Optional[int]]

    # Instance variables
    best_metrics: Dict[str, Number]
    best_metric_at: Dict[str, EpochStep]
    _best_this_epoch: Sequence[Metric]
    history: Dict[EpochStep, Dict[str, Number]]

    def __init__(self, out_dir):
        self.out_dir = pathlib.Path(out_dir)
        # Some recording keeping here. Could probably just use a single
        # authorative dataframe, and have functions query it. But for now,
        # I'll stick with this.
        self.best_metrics = dict()
        self.best_metric_at = dict()
        self._new_best = []
        # To allow new metrics to be added at any time, we won't use any
        # fixed table structure. Instead, just a dicts of dicts, one entry
        # for each epoch recorded. It's a dict of dicts rather than a list
        # of dicts, as we don't want to enforce that the tracker be updated
        # on every epoch. Another detail: we don't store Metric objects, but
        # just the values. The benefit of this is an easy conversion to
        # dataframes.
        self.history = defaultdict(dict)

    def history_path(self) -> pathlib.Path:
        return self.out_dir / self.HISTORY_FILENAME

    def best_path(self) -> pathlib.Path:
        return self.out_dir / self.BEST_FILENAME

    def on_epoch_end(self, metrics: Sequence[Metric], epoch: int):
        return self.new_metrics(metrics, epoch)

    def new_metrics(self, metrics: Sequence[Metric], epoch: int, step=None):
        """Record this latest epoch's metrics.

        The function name hints that I'm coming around to the idea that
        having training callbacks is eventually going to happen.
        """
        self._new_best = []
        for metric in metrics:
            # Add to history
            self.history[(epoch, step)][metric.name] = metric.value
            if math.isnan(metric.value):
                _logger.warning(f"Metric ({metric.name}) is NaN.")
                continue
            if not metric.checkpointed:
                continue
            current_best = self.best_metrics.get(metric.name, None)
            # If new or better metric encountered, hardlink to epoch checkpoint.
            if current_best is None or metric.is_better(current_best):
                # Log a message if a new metric is encountered.
                if current_best is None:
                    _logger.info(
                        "New metric encountered "
                        f"({metric.name} = {metric.value:.5f}) "
                    )
                else:
                    assert metric.is_better(current_best)
                    prev_epoch, prev_step = self.best_metric_at[metric.name]
                    log_metric_improvement(
                        metric, current_best, epoch, prev_epoch, step, prev_step
                    )
                self.best_metrics[metric.name] = metric.value
                self.best_metric_at[metric.name] = (epoch, step)
                self._new_best.append(metric)
        self._write_history()
        self._write_best()
        self._log_best()
        return self._new_best

    def _write_history(self):
        """Write the metric history as a CSV file."""
        self.history_as_dataframe().write_csv(self.history_path())

    def _write_best(self):
        with open(self.best_path(), "w") as f:
            json.dump(self.best_metrics, f, indent=2)

    def _log_best(self):
        """Print the best metrics to the console."""
        _console.print("Best metrics:")
        _console.print(
            json.dumps(self.best_metrics, indent=2, ensure_ascii=False)
        )
        _logger.info("[CONSOLE] Best metrics: " + json.dumps(self.best_metrics))

    def improved_metrics(self) -> Sequence[Metric]:
        """
        Returns a list of metrics that have improved since the last update.
        """
        return self._new_best

    def history_as_dataframe(self):
        """Return the history of metrics as a dataframe.

        ┌─────────┬────────┬───────────────┬─────────┐
        |  epoch  |  step  |  metric_name  |  value  |

        """

        def to_row(k, v):
            epoch, step = k
            return {"epoch": epoch, "step": step, **v}

        return pl.DataFrame(
            [to_row(k, v) for k, v in self.history.items()],
            orient="row",
            schema=pl.Schema(
                {
                    "epoch": pl.UInt32,
                    "step": pl.UInt64,
                }
                | {
                    metric_name: pl.Float64
                    for metric_name in self.best_metrics.keys()
                }
            ),
        )


def print_metrics(metrics):
    _logger.info(" | ".join([f"{m.name}: {m.value:.5f}" for m in metrics]))


def mpl_fig_to_array(fig) -> np.ndarray:
    """Convert MPL figure to numpy array.

    From: https://github.com/Zulko/moviepy/blob/master/moviepy/video/io/bindings.py
    """
    #  only the Agg backend now supports the tostring_argb function
    from matplotlib.backends.backend_agg import FigureCanvasAgg

    canvas = FigureCanvasAgg(fig)
    canvas.draw()  # update/draw the elements

    # get the width and the height to resize the matrix
    l, b, w, h = canvas.figure.bbox.bounds
    w, h = int(w), int(h)

    #  exports the canvas to a string buffer and then to a numpy nd.array
    buf = canvas.tostring_argb()
    image = np.frombuffer(buf, dtype=np.uint8)
    return image.reshape(h, w, 4)[..., 1:]


def plotly_fig_to_array(fig) -> np.ndarray:
    """Convert plotly figure to numpy array.

    From:
        https://community.plotly.com/t/converting-byte-object-to-numpy-array/40189/3
    """
    fig_bytes = fig.to_image(format="png")
    buf = io.BytesIO(fig_bytes)
    try:
        import PIL
        import PIL.Image
    except ImportError:
        raise ImportError(
            "PIL is required to convert plotly figures to numpy arrays.")
    img = PIL.Image.open(buf)
    array_rgba = np.asarray(img)
    array_rgb = array_rgba[:, :, 0:3]
    return array_rgb


class TbLogger(object):
    """Manages logging to TensorBoard."""

    def __init__(self, tensorboard_dir: Union[str, pathlib.Path]):
        self.writer = tb.SummaryWriter(str(tensorboard_dir))

    @staticmethod
    def tag(label: str, log_group: str):
        res = f"{label}/{log_group}"
        return res

    def log(self, n_iter: int, data, log_group: str):
        """Log a mixture of different types of data."""
        for k, v in data.items():
            # The infamous if-else
            if k == "metrics":
                self.log_metrics(n_iter, v, log_group)
            elif isinstance(v, MplFigureList):
                self.log_mpl(k, n_iter, v, log_group)
            elif isinstance(v, PlotlyFigureList):
                self.log_plotly(k, n_iter, v, log_group)
            elif isinstance(v, Embeddings):
                self.log_embeddings(k, n_iter, v, log_group)
            elif isinstance(v, PlotlyVideo):
                self.log_plotly_video(k, n_iter, v, log_group)
            elif isinstance(v, Images):
                self.log_images(n_iter, v, log_group)
            else:
                raise ValueError(
                    "Logging the given data is unsupported " f"({data})."
                )

    def log_metrics(self, n_iter: int, metrics, log_group: str):
        for metric in metrics:
            self.writer.add_scalar(
                self.tag(metric.name, log_group), metric.value, n_iter
            )

    def log_scalar(self, n_iter: int, name: str, val, log_group: str):
        self.writer.add_scalar(self.tag(name, log_group), val, n_iter)

    def log_images(self, n_iter: int, images: Images, log_group: str):
        self.writer.add_images(
            self.tag("images", log_group),
            images.images,
            n_iter,
            dataformats="NCHW",
        )

    def log_mpl(
        self,
        label: str,
        n_iter: int,
        figs: Union[MplFigureList, Iterable],
        log_group: str,
    ):
        if isinstance(figs, MplFigureList):
            figs = figs.figs
        if not isinstance(figs, collections.abc.Iterable):
            raise ValueError("Expected a iterable of plots.")
        else:
            figs = figs
        plots_as_arrays = [mpl_fig_to_array(p) for p in figs]
        plots_as_array = np.stack(plots_as_arrays)
        self.writer.add_images(
            self.tag(label, log_group),
            plots_as_array,
            n_iter,
            dataformats="NHWC",
        )

    def log_plotly(
        self,
        label: str,
        n_iter: int,
        figs: Union[PlotlyFigureList, Iterable],
        log_group: str,
    ):
        if isinstance(figs, PlotlyFigureList):
            figs = figs.figs
        if not isinstance(figs, collections.abc.Iterable):
            raise ValueError("Expected a iterable of plots.")
        else:
            figs = figs
        plots_as_arrays = [plotly_fig_to_array(p) for p in figs]
        plots_as_array = np.stack(plots_as_arrays)
        self.writer.add_images(
            self.tag(label, log_group),
            plots_as_array,
            n_iter,
            dataformats="NHWC",
        )

    def log_plotly_video(
        self,
        label: str,
        n_iter: int,
        fig_list: PlotlyVideo,
        log_group: str,
    ):
        if not isinstance(fig_list.figs, collections.abc.Iterable):
            raise ValueError("Expected a iterable of plots.")
        plots_as_array = np.array(
            [plotly_fig_to_array(p) for p in fig_list.figs]
        )
        plots_as_tensor = torch.from_numpy(plots_as_array)
        plots_as_5d_tensor = einops.rearrange(
            plots_as_tensor, "(N F) H W C -> N F C H W", N=1
        )
        self.writer.add_video(
            self.tag(label, log_group), plots_as_5d_tensor, n_iter, fps=10
        )

    def log_embeddings(
        self, label: str, n_iter: int, embedding: Embeddings, log_group: str
    ):
        self.writer.add_embedding(
            embedding.embeddings,
            metadata=embedding.labels,
            label_img=embedding.label_img,
            global_step=n_iter,
            tag=self.tag(label, log_group),
        )


class ModelSaver:
    """Saves and loads model checkpoints.

    Keeps a history of checkpoints, including the checkpoints where the best
    metrics were observed.

    Inspired by both pytorch-image-models:
      https://github.com/rwightman/pytorch-image-models/blob/fa8c84eede55b36861460cc8ee6ac201c068df4d/timm/utils/checkpoint_saver.py#L21
    and PyTorch lightning:
      https://pytorch-lightning.readthedocs.io/en/stable/_modules/pytorch_lightning/callbacks/model_checkpoint.html#ModelCheckpoint

    A number of differences:

        - We support multiple "best" metrics. This is important
          as when the model can get high accuracy (e.g. 99.9%) in the presence
          of unbalanced data, other metrics such as correlation measures can
          be very low. When analysing the results, it can be useful to have
          the models that are best at each metric.
        - Non-linear checkpoint history. One of the very annoying things about
          the pytorch-image-model checkpointing is that it only keeps recent
          checkpoints. I'm not sure what Pytorch lightning does.
    """

    EPOCH_FILENAME_FORMAT = "checkpoint_epoch-{epoch}.pth"
    STEP_FILENAME_FORMAT = "checkpoint_step-{step}.pth"
    LAST_CKPT_FILENAME = "checkpoint_last.pth"
    BEST_CKPT_FILENAME_FORMAT = "checkpoint_best_{metric_name}.pth"
    RECOVERY_CKPT_FILENAME = "recovery.pth"

    def __init__(
        self,
        save_dir: Union[str, pathlib.Path],
        model,
        optimizer=None,
        scheduler=None,
        max_history: int = 10,
    ):
        if max_history < 1:
            raise ValueError(
                f"max_history must be greater than zero. Got ({max_history})"
            )
        self.save_dir = pathlib.Path(save_dir)
        self.model = model
        self.optimizer = optimizer
        self.scheduler = scheduler
        self.checkpoints_by_epoch = dict()
        self.checkpoints_by_step = dict()
        self.max_history = max_history
        # At some point, make this a parameter instead.
        self.max_step_history = max(1, max_history // 4)

    @property
    def last_path(self):
        res = self.save_dir / self.LAST_CKPT_FILENAME
        return res

    @property
    def recovery_path(self):
        res = self.save_dir / self.RECOVERY_CKPT_FILENAME
        return res

    def epoch_path(self, epoch: int):
        res = self.save_dir / self.EPOCH_FILENAME_FORMAT.format(epoch=epoch)
        return res

    def step_path(self, step: int):
        res = self.save_dir / self.STEP_FILENAME_FORMAT.format(step=step)
        return res

    def metric_path(self, metric_name: str):
        res = self.save_dir / self.BEST_CKPT_FILENAME_FORMAT.format(
            metric_name=metric_name
        )
        return res

    def _save_epoch_checkpoint(self, epoch: int):
        # Save the checkpoint as an epoch checkpoint.
        epoch_path = self.epoch_path(epoch)
        save_model(self.model, epoch_path, self.optimizer, self.scheduler)
        self.checkpoints_by_epoch[epoch] = epoch_path
        # Link to "last" checkpoint.
        _logger.debug(f"Updating symlink ({str(self.last_path)})")
        self.last_path.unlink(missing_ok=True)
        # Note: a tricky aspect of path_A.symlink_to(path_B) is that path_A
        # will be assigned to point to path_A / path_B. And so, we usually
        # will want to call path_A.symlink_to(path_B.name).
        self.last_path.symlink_to(epoch_path.name)
        assert self.last_path.exists()
        return epoch_path

    def _save_step_checkpoint(self, step: int):
        step_path = self.step_path(step)
        save_model(self.model, step_path, self.optimizer, self.scheduler)
        self.checkpoints_by_step[step] = step_path
        # Link to "last" checkpoint.
        _logger.debug(f"Updating symlink ({str(self.last_path)})")
        self.last_path.unlink(missing_ok=True)
        self.last_path.symlink_to(step_path.name)
        assert self.last_path.exists()
        return step_path

    def _save_metrics_checkpoint(
        self, improved_metrics: Sequence[Metric], latest_path
    ):
        for metric in improved_metrics:
            assert not math.isnan(metric.value)
            best_path = self.metric_path(metric.name)
            best_path.unlink(missing_ok=True)
            _logger.debug(
                f"Updating (best {metric.name}) checkpoint, ({best_path})"
            )
            # Hard link to the epoch checkpoint.
            latest_path.link_to(best_path)
            # TODO: move to "hardlink_to" when we upgrade to Python 3.10.
            #   best_path.hardlink_to(self.epoch_path(epoch)

    def save_epoch_checkpoint(
        self, epoch: int, improved_metrics: Sequence[Metric]
    ):
        ckpt_path = self._save_epoch_checkpoint(epoch)
        self._save_metrics_checkpoint(improved_metrics, ckpt_path)
        # Clean up history, if necessary.
        self._remove_epoch_checkpoints()

    def save_step_checkpoint(
        self, step: int, improved_metrics: Sequence[Metric]
    ):
        ckpt_path = self._save_step_checkpoint(step)
        self._save_metrics_checkpoint(improved_metrics, ckpt_path)
        # Clean up history, if necessary.
        self._remove_step_checkpoints()

    @staticmethod
    def inverse_cumulative_exp(area: float, half_life: float = 0.5):
        """This is the inverse of the cumulative exponential function (base 2).

        f(t) = 2 ** (t / half_life)
        F(t) = int_{0}^{t} f(x) dx
        InvCumExp(x) = F^{-1}(x)   <--- this is what we want.
        """
        # L is used to normalize the area under the curve to 1.
        L = 1 / (2 ** (1 / half_life) - 1)
        # Inv function.
        t = half_life * math.log(area / L + 1, 2)
        return t

    @classmethod
    def _remove_checkpoints(cls, checkpoints_map, max_history: int):
        """
        Remove old checkpoints if we have hit the checkpoint history limit.

        Removal tries to be "smart" by spreading out the removal. Why? Because
        if we keep the N-most recent checkpoints, we can't go back further
        than N epochs prior. This is definitely a problem, as often, when we
        notice an issue with training, such as NaN values, we want to go back
        more than N epochs prior.

        The solution taken here is to break up the checkpoint history into
        weighted areas, and to remove checkpoints if two fall into the same
        region. The areas are weighted exponentially, so that we keep a larger
        number of more recent checkpoints, and fewer older checkpoints.
        """
        assert max_history > 0
        if len(checkpoints_map) <= max_history:
            # We haven't reached the max number of checkpoints yet.
            return
        # Remove the newest checkpoint that doesn't fit under the easing curve.
        saved_idx = sorted(checkpoints_map.keys())
        max_so_far = saved_idx[-1]
        to_remove = None
        prev_zone = -1
        to_remove = saved_idx[0]
        for e in saved_idx:
            zone = cls.inverse_cumulative_exp(e / max_so_far)
            zone_int = math.floor(zone * max_history)
            if zone_int == prev_zone:
                to_remove = e
                break
            prev_zone = zone_int

        assert to_remove is not None, "There must be checkpoints already saved."
        # Remove the identified checkpoint.
        file_to_remove = checkpoints_map.pop(to_remove)
        # Unlink old checkpoint. Note that it might still be linked as the best
        # checkpoint, and thus the file might not be deleted.
        file_to_remove.unlink()
        _logger.debug(f"Unlinked old checkpoint: ({str(file_to_remove)})")

    def _remove_epoch_checkpoints(self):
        self._remove_checkpoints(self.checkpoints_by_epoch, self.max_history)

    def _remove_step_checkpoints(self):
        self._remove_checkpoints(
            self.checkpoints_by_step, self.max_step_history
        )

    def save_recovery(self):
        """Trigger the saving of a checkpoint to the recovery path.

        The recovery checkpoint is the only checkpoint taken mid-epoch. It is
        created periodically to allow training to restart in the event of an
        error.
        """
        _logger.info(
            "Creating recovery checkpoint: " f"({str(self.recovery_path)})"
        )
        save_model(
            self.model, self.recovery_path, self.optimizer, self.scheduler
        )

    def delete_recovery(self):
        """Delete the recovery checkpoint.

        This can be manually whenever the recovery checkpoint becomes unneeded,
        typically once training is finished.
        """
        if self.recovery_path.exists():
            if not self.recovery_path.is_file():
                raise Warning(
                    "Recovery path exists but is not a file "
                    f"({str(self.recovery_path)})"
                )
            self.recovery_path.unlink()
