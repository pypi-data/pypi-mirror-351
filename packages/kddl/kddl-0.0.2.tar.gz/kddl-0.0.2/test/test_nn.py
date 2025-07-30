"""
Test for test code.

These tests cover the reference implementation used in the pytest code.

The reference implementations are expected to not be modified, and their failure
means there is possibly something wrong with the training infrastructure, or
an accidental change in the reference implementation.

Baseline 1
==========
A CNN for MNIST classification.
"""

import pytest
import torch
import kddl.train
import kddl._logging

# Note on importing nn.py. pytest will add kddl/test to the sys.path, and so,
# any modules in the kddl/test directory can be imported directly.
import kddl.testing as test_nn


def _val_dl_fn(ds):
    val_dl = torch.utils.data.DataLoader(
        ds,
        batch_size=256,
        shuffle=False,
        num_workers=4,
        drop_last=False,
    )
    return val_dl


_default_train_args = {
    "n_epochs": 14,
    "batch_size": 64,
    "lr": 0.001,
    "weight_decay": 0.01,
    "save_checkpoints": False,
}


def test_cnn1(out_root, mnist_ds_mgr, seed_random):
    """Make sure our baseline CNN performs as expected on MNIST.

    TODO: use the best-loss checkpoint for the evaluation.
    TODO: this model isn't actually that reliable! Need to have a reliable
    base model.
    """
    model = test_nn.Cnn1()
    trainable = test_nn.ClassifyTrainable(mnist_ds_mgr, model, "cnn1_mnist")
    out_dir = kddl._logging.get_outdir(out_root, ["train"])
    kddl.train.train(
        trainable,
        out_dir=out_dir,
        **_default_train_args,
    )

    trainable.model.eval()
    metrics = trainable.evaluate_val(_val_dl_fn)
    loss, acc = metrics["metrics"]
    assert acc.value > 0.70, "This should really not fail"
    assert acc.value == pytest.approx(0.850, abs=0.10)


def test_fastai_cnn1(out_root, fashion_mnist_ds_mgr, seed_random):
    model = test_nn.FastaiCnn1()
    trainable = test_nn.ClassifyTrainable(
        fashion_mnist_ds_mgr, model, "fastai_cnn1_fashion_mnist"
    )
    out_dir = kddl._logging.get_outdir(out_root, ["train"])
    kddl.train.train(
        trainable,
        out_dir=out_dir,
        **_default_train_args,
    )
    trainable.model.eval()
    metrics = trainable.evaluate_val(_val_dl_fn)
    loss, acc = metrics["metrics"]
    # assert acc.value > 0.70, "This should really not fail"
    # assert acc.value == pytest.approx(0.850, abs=0.10)





