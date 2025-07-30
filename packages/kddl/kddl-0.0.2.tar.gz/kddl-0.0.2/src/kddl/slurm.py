"""
Some utilities for working with SLURM.

Some of these functions might be more generally useful: for example, maybe most
runs on a remote machine could benefit from being compressed after they finish. 
Or just some outputs are large and should be compressed. If this ends up being 
the case, these functions can move to a more general location like _logging.py.
"""

import os
import shutil
import tarfile
import logging
from pathlib import Path
from typing import Optional, Sequence, Union
import kddl
import kddl._logging

_logger = logging.getLogger(__name__)


def create_out_dir(prefix: Optional[str] = None):
    """Create a directory to write outputs to.

    HPC nodes running jobs are not expected to create the output version
    directory. This should be done by a parent job/script, for a few reasons
    including avoiding race conditions. The nodes still need somewhere to
    write to, and it's probably not going to be a good idea to write to the
    non-local filesystem where everything eventually gets collected. So, this
    function's job is not about versioning, but about creating a scratch
    directory that will evenutally perish. So make sure to copy the results
    to a more permanent location before the job ends. What we do need to be
    mindful of is that many nodes will use this function, and when we copy the
    output to the more permanent location, each node's output should use a
    unique path even though they are all doing work for the same experiment
    run. For this reason, we include the job_id in the name of the leaf.

    Args:
        prefix: Optional string to prepend to the output directory name.
            If you intend to use the back_up context manager, you most likely
            want to use something like "_".join(ver_parts) so that the created
            archive has a meaningful name.
    """
    temp_dir = Path(os.environ["TMPDIR"])
    if not temp_dir.exists():
        raise ValueError(f"Env variable TMPDIR should exist.")
    job_id = os.getenv("SLURM_JOB_ID")
    if job_id is None:
        raise ValueError("Env variable SLURM_JOB_ID should be set.")
    if prefix:
        leaf = f"{prefix}_{job_id}"
    else:
        leaf = str(job_id)
    node_out_dir = temp_dir / leaf
    node_out_dir.mkdir(exist_ok=False, parents=False)
    if not node_out_dir.exists():
        raise ValueError(f"Failed to create {node_out_dir}")
    return node_out_dir



def extract(archive_path, keep_root_dir=False, remove_archive=False):
    """Extract a run's data archive to the current directory.

    The archives have names like '0_112_0_1.tar.gz', and the root directory
    within the archive will also be named '0_112_0_1'. Why? It's very annoying
    when you extract an archive and it litters the current directory with
    files. While we may want to avoid that littering when manually opening an
    archive, when calling this function, we generally do want the contents to be
    extracted without the archive's root directory, as the archive is already
    in the correct location.
    """
    archive_path = Path(archive_path)
    parent_dir = archive_path.parent
    with tarfile.open(archive_path, "r:gz") as tar:
        # First, read the archive's root directory name.
        tar_info = tar.next()
        if tar_info is None:
            raise ValueError(f"{archive_path=} has no contents.")
        assert tar_info is not None
        if not tar_info.isdir():
            raise ValueError(
                f"{archive_path=} should have one root directory, "
                f"but has: {tar.getnames()=}."
            )
        top_level_folder = tar_info.name
        tar.extractall(path=parent_dir)
    if not keep_root_dir:
        _logger.info(f"Removing root directory {top_level_folder}")
        extracted_dir = parent_dir / top_level_folder
        collisions = False
        for f in extracted_dir.iterdir():
            if (parent_dir / f.name).exists():
                collisions = True
            else:
                f.rename(parent_dir / f.name)
        if not collisions:
            shutil.rmtree(extracted_dir)
        else:
            _logger.warning(
                f"Collisions detected moving contents from {extracted_dir} to "
                f" {parent_dir=}. Leaving original {extracted_dir} in place."
            )

    if remove_archive:
        _logger.info(f"Removing archive {archive_path}")
        os.remove(archive_path)
    return top_level_folder


def extract_latest_run(root_out_dir, patch : Optional[int], keep_root_dir: bool, remove_archive: bool):
    root_out_dir = Path(root_out_dir)
    ver_parts, patches = kddl._logging.script_existing_versions(root_out_dir)
    if patch is None:
        patch = patches[-1]
    full_ver_seq = list(ver_parts) + [str(patch)]
    latest_dir = root_out_dir.joinpath(*full_ver_seq)
    expected_archive_prefix = "_".join(full_ver_seq)
    # Loop over all files and extract matching archives.
    for f in latest_dir.iterdir():
        if f.is_file() and f.name.startswith(expected_archive_prefix):
            extract(f, keep_root_dir, remove_archive)
