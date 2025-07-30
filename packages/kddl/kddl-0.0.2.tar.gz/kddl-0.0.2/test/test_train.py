import pytest
import kddl.train as train


def test_gpus_ordered_by_mem_used():
    """
    Tests that:
        1. The function runs without error.
    """
    train.gpus_ordered_by_mem_used()

