from contextlib import contextmanager
import logging
import math
import pathlib
import subprocess
import re
from typing import (
    Any,
    Callable,
    List,
    Optional,
    Tuple,
    TypeAlias,
    Union,
    Dict,
    Set,
)
import numpy as np
import torch
import torch.amp
import torch.nn as nn
import torchinfo
from . import _logging

"""
This file aims to be a project-independent training-loop and associated
scaffolding.
"""

_logger = logging.getLogger(__name__)

"""
Max training time before a new recovery is made.

Standard checkpointing only happens every epoch. But a checkpoint for recovery
purposes will be made every 30 minutes. Only a single recovery is kept.
"""
RECOVERY_CKPT_PERIOD_SEC = 30 * 60

"""
Here we take part in the rite of of passage for a deep learning project by
yet again reinventing the training loop architecture. No one wants their 
project stitched together with the callbacks of some soon to be abandonded or 
rewritten DL framework.
"""


def to_device(x: Union[list, tuple, dict, torch.Tensor], device):
    """
    Recursively move all tensors in x to the given device.

    Supports lists, tuples, dictionaries, and torch.Tensor.
    """
    if isinstance(x, torch.Tensor):
        return x.to(device)
    elif isinstance(x, dict):
        return {k: to_device(v, device) for k, v in x.items()}
    elif isinstance(x, (list, tuple)):
        return [to_device(v, device) for v in x]
    raise ValueError(f"Unsupported type: {type(x)}")


def gpus_ordered_by_mem_used(exclude: Optional[Set[int]] = None):
    """
    Return a list of GPU indices ordered by memory used (increasing).

    You probably want to use the first GPU in the returned list.
    """
    try:
        out_str = subprocess.check_output(
            # -A<X> prints X lines after the match.
            # Full output is like, one line per GPU:
            #  Used        : 11MiB
            #  Used        : 66MiB
            "nvidia-smi -q -d Memory | grep -A4 GPU | grep Used",
            shell=True,
        )
    except subprocess.CalledProcessError as e:
        _logger.error(
            "Failed to parse nvidia-smi output looking for GPU information. "
            "Most likely, nvidia-smi has changed it's output format, and this "
            "code needs a simple tweak."
        )
        raise e
    mems = re.findall(r"Used\s+:\s+(\d+)\s+MiB", out_str.decode("utf-8"))
    if not len(mems):
        raise ValueError(f"Unexpected output: {out_str}")
    res = sorted(range(len(mems)), key=lambda i: int(mems[i]))
    if exclude is not None:
        res = [i for i in res if i not in exclude]
    return res


class ModelException(Exception):
    """Raised when a model causes training to fail.

    This allows callers to catch this exception and move on to the next model.
    """

    pass


class Trainable:
    """Encapsulates a dataset, model input-output and loss function.

    This class is needed in order to be able to train multiple models and
    configurations with the same training function. The training function
    is too general to know about how to route the data into and out of a model,
    evaluate the model or how to take a model output and create a prediction.

    Redesign from function parameters to a class
    --------------------------------------------
    The class began as a dumb grouping of the parameters to the train function:
    train_ds, val_ds, test_ds, model, loss_fn, forward_fn, val_fn, and more—there
    were so many parameters that they were grouped together into a NamedTuple.
    However, functions like forward_fn and val_fn would need to be given
    the model, loss_fn and forward_fn in order to operate. This is the exact
    encapsulation behaviour that classes achieve, so the NamedTuple was made
    into a class. Leaning into the use of classes, forward_fn and val_fn were
    made into methods of the class, while the rest became properties. This
    change is noteworthy as customizing the forward or validation functions
    now requires defining a new class, rather than simply passing in a new
    function. Although, nothing is stopping someone from defining a class that
    simply wraps a function and passes the arguments through.

    Flexibility to vary the data format
    -----------------------------------
    Why things belongs inside or outside this class can be understood by
    realizing that the nature of the datasets are known here. As such,
    any function that needs to extract the individual parts of a dataset
    sample will need to know what is in each sample. Such a function is a
    good candidate to appear in this class.

    While in some cases you can separate the datasets from the models, this
    isn't always easy or a good idea. A model for ImageNet can easily be
    separated from the dataset, as the inputs and outputs are so standard; but
    for the spike prediction, the model output is quite variable. Consider the
    distance array model which outputs an array, whereas a Poisson-distribution
    model will output a single number. Training is done with these outputs, and
    involves the dataset producing sample tuples that have appropriate elements
    (distance fields, for example). The actual inference is an additional
    calculation using these outputs.

    In other words, the procedure of taking the model input and model output
    from a dataset sample and feeding it to the model, then calculating the
    loss and doing the inference—none of these steps can be abstracted to be
    ignorant of either the model or the dataset.

    Handles dataloader creation
    ---------------------------
    train.py handled this responsibility for a number of months; however,
    it became a problem once I needed more control over the evaluation
    function. For evaluation, I wanted to run the slow inference proceedure
    on a subset of the cells and additionally create input-output videos
    for them. This was specific to just one of the trainables. The ideal
    approach would be for the evaluation function to get or create a number
    of extra data loaders (one for each cluster) and then run the more detailed
    evaluation on each. There wasn't a good way to do this without moving
    the full responsibility of dataloader handing into the Trainable class.
    The current approach is to use an intermediate (DatasetManager) that lazily
    creates datasets; this allows trainables to create multiple variations of
    a dataset as needed, without them being created up front.

    Other libraries
    ---------------
    Compared to Keras and FastAI: Trainable encapsulates a lot less than
    Keras's Model or FastAI's Learner.

    At this point, I'm not eager to use the FastAI API, as I don't
    want to discover later that it's too limiting in some certain way. It's
    quite possible that it's already too prescriptive. Reading the docs, it's
    not clear what parts of Learner's internals are exposed for customization.
    If all "_" prefixed methods are not meant to be customized, then it's
    already too restrictive. Notably, there seems to be an expected format for
    the elements of the dataset, which I want to avoid. The reason for this is
    that the distance arrays are intermediate results, and while I want to
    train on them, I would like to evaluate based on quick approximate
    inference and make predictions using much more expensive and accurate
    inference routines. So the data doesn't fall nicely into (X,y) type data,
    and the metrics are not consistent across training and evaluation.

    In addition, at least at the momemt, FastAI's library provides a lot more
    abstraction/generalization than I need, which can make it harder for
    myself (or others) to understand what is going on. This might end up being
    a mistake, as the growing code might reveal itself to provide abstraction
    boundaries that are already handled nicely in FastAI.
    """

    def __init__(self, model: torch.nn.Module, label: str):
        """
        Args:
            model: the PyTorch model to train.
            label: a string label for this trainable.
        """
        self.model = model
        self.label = label

    def train_ds(self):
        raise NotImplementedError("Override")

    def val_ds(self):
        raise NotImplementedError("Override")

    def test_ds(self):
        raise NotImplementedError("Override")

    def forward(self, sample):
        """Run the model forward.

        Args:
            sample: a single draw from the train or validation data loader.

        Returns:
            (output, loss): the model output and the loss, as a tuple.
        """
        raise NotImplementedError("Override")

    """
    Some considerations about the evaluate functions.
       - The evaluation functions should be given the power and responsibility
         to create the datasets. This is because they may want to change the
         nature of a dataset. For example, the spike prediction models want
         to change ds stride and to filter in/out certain clusters.
       - The evaluation functions should not need to care about how to create
         a dataloader from a dataset. Things like worker counts and batch
         sizes should not need to be handled.
       - There should two separate routines: one for the training dataset and
         one for the validation dataset. The reason for the distinction 
         will mostly often be the sizes of the datasets. 
       - It might be desirable to have a third function that will be run
         at the end of training, or outside of training, and is expected to be 
         a long-running. 
    """

    def evaluate_train(self, dl_fn):
        """Run the evaluation procedure on the train dataset.

        Args:
            dl_fn: a function to convert the train dataset into a dataloader.

        Returns:
            metrics: a str:float dictionary containing evaluation metrics. It
                is expected that this dictionary at least contains 'loss' and
                'accuracy' metrics.
        """
        raise NotImplementedError("Override")

    def evaluate_val(self, dl_fn):
        """Run the evaluation procedure on the val dataset.

        Args:
            dl_fn: a function to convert the train dataset into a dataloader.

        Returns:
            metrics: a str:float dictionary containing evaluation metrics. It
                is expected that this dictionary at least contains 'loss' and
                'accuracy' metrics.
        """
        raise NotImplementedError("Override")

    def evaluate_full(self, ds, dl_fn):
        """Run a pontentially long evaluation procedure on the given dataset.

        This isn't implemented anywhere yet. The idea here is to carve out
        some space for running a longer evaluation procedure on a dataset. This
        function is not called during the training routine.

        Args:
            ds: the dataset to evaluate on.
            dl_fn: a function to convert the train dataset into a dataloader.
        """
        raise NotImplementedError("Override")

    def in_device(self):
        """Returns the device on which the model expects input to be located.

        Most likely, the whole model is on a single device, and it is
        sufficient to use `next(self.model.parameters()).device`.
        """
        raise NotImplementedError("Override")

    def __str__(self) -> str:
        return f"Trainable ({self.label})"

    def model_summary(self, batch_size: int) -> str:
        """Returns a detailed description of the model.

        Args:
            batch_size: the batch size to use when creating the model summary.

        At the moment, this is called by train() with the intent of saving
        out a file containing info like torchinfo.summary. The torch module
        input shape isn't known by train(), so the actual summary creation
        must be done somewhere like Trainable.

        Override this to add more features.
        """
        return f"Trainable ({self.label})"


class DatasetManager:
    """
    Create train, val & test Pytorch Datasets.

    The train, val & test datasets must be created almost identically, except
    for small changes to options like shuffle.

    The reason for choosing factory functions to be passed around instead of
    the actual datasets is that there are cases where we need to create
    more, and the initial train, val, test datasets are not sufficient.
    Alternatively, we want access to dataloaders and not datasets or vise-versa
    The case that initiated this refactor was the need to split a validation
    set into multiple 1-cluster datasets for the purpose of evaluating
    autoregressive inference.

    Another benefit is that the datasets aren't created eagerly, which can
    save memory if they aren't needed, which is typically the case for the
    test dataset while training.

    train.py will construct the DatasetManager and give it to the Trainable.
    The DatasetManager will be held by the Trainable, and so train.py will
    no longer need to construct and pass around dataloaders.
    """

    def train_ds(self) -> torch.utils.data.Dataset:
        raise NotImplementedError()

    def val_ds(self) -> torch.utils.data.Dataset:
        raise NotImplementedError()

    def test_ds(self) -> torch.utils.data.Dataset:
        raise NotImplementedError()


class BasicDatasetManager(DatasetManager):
    """Store and return the datasets as-is.

    Useful for simple cases. To handle stastistics of the training set, like the
    mean and standard deviation, or whatever else is needed, use the
    train_ds_attrs, which will convert the key-value entries to class
    properties. just make sure to use valid python identifiers for the keys.

    Improvement: we could allow train_ds, val_ds and test_ds to optionally be
    functions, which would allow the datasets to be created lazily and fresh
    each time.
    """

    def __init__(self, train_ds, val_ds, test_ds, train_ds_attrs=None):
        """
        Args:
            train_ds: the training dataset.
            val_ds: the validation dataset.
            test_ds: the test dataset.
            train_ds_attrs: a dictionary of attributes to store with the
                training dataset. These attributes can be accessed as properties
                of the DatasetManager. Use this for values like mean, std and
                so on—values used for things like normalization.

        """
        self._train_ds = train_ds
        self._val_ds = val_ds
        self._test_ds = test_ds
        # Store the attributes dictionary
        self._train_ds_attrs = train_ds_attrs or {}
        # Dynamically create properties for each attribute
        for attr_name in self._train_ds_attrs.keys():
            if not attr_name.isidentifier():
                raise ValueError(f"Invalid attribute name: {attr_name}")

            # Create a property getter for this attribute
            # The following will reference the final value of the loop variable
            # attr_name, which would be a bug.
            # def getter(self):
            #     return self._train_ds_attrs[attr_name]
            # Instead we do:
            def getter(self, attr_name=attr_name):
                return self._train_ds_attrs[attr_name]

            setattr(self.__class__, attr_name, property(getter))

    def train_ds(self) -> torch.utils.data.Dataset:
        return self._train_ds

    def val_ds(self) -> torch.utils.data.Dataset:
        return self._val_ds

    def test_ds(self) -> torch.utils.data.Dataset:
        return self._test_ds


class BaseTrainable(Trainable):
    """
    Covers basic Trainable functionality.
    """

    def __init__(
        self,
        ds_mgr: DatasetManager,
        model: torch.nn.Module,
        label: str,
        # For speed, you probably want to cache.
        cache_dl: bool = True,
    ):
        super().__init__(model, label)
        self.ds_mgr = ds_mgr
        self._train_ds = None
        self._val_ds = None
        self._test_ds = None
        self.collate_fn = None
        self.cache_dl = cache_dl
        # For evaluation only:
        self._train_dl = None
        self._val_dl = None

    def train_ds(self) -> torch.utils.data.Dataset:
        if self._train_ds is None:
            self._train_ds = self.ds_mgr.train_ds()
        return self._train_ds

    def val_ds(self) -> torch.utils.data.Dataset:
        if self._val_ds is None:
            self._val_ds = self.ds_mgr.val_ds()
        return self._val_ds

    def test_ds(self) -> torch.utils.data.Dataset:
        if self._test_ds is None:
            self._test_ds = self.ds_mgr.test_ds()
        return self._test_ds

    def train_dl(self, dl_fn):
        if self._train_dl is None or not self.cache_dl:
            self._train_dl = dl_fn(self.train_ds(), collate_fn=self.collate_fn)
        return self._train_dl

    def val_dl(self, dl_fn):
        if self._val_dl is None or not self.cache_dl:
            self._val_dl = dl_fn(self.val_ds(), collate_fn=self.collate_fn)
        return self._val_dl

    def in_device(self):
        return next(self.model.parameters()).device

    def __str__(self) -> str:
        return f"Trainable ({self.label})"

    def model_summary(self, batch_size: int) -> str:
        dl = torch.utils.data.DataLoader(self.train_ds(), batch_size=batch_size)
        sample = next(iter(dl))
        X, mask, y = sample
        X = X.to(self.in_device())
        mask = mask.to(self.in_device())
        res = torchinfo.summary(
            self.model,
            input_data=(X, mask),
            col_names=["input_size", "output_size", "mult_adds", "num_params"],
            device=self.in_device(),
            depth=4,
        )
        return res

    # Commented out so that sub classes are free to override evaluate_train and
    # evaluate_val and change signature of evaluate().
    # def evaluate(self, dl):
    #     raise NotImplementedError("Override")

    def evaluate_train(self, dl_fn):
        return self.evaluate(self.train_dl(dl_fn))

    def evaluate_val(self, dl_fn):
        # We don't manage the model train/val state here, as it could be a
        #
        if self.model.training:
            _logger.warning("Model should be in eval mode")
        return self.evaluate(self.val_dl(dl_fn))


def _create_dataloaders(
    batch_size,
    eval_batch_size,
    n_workers,
    pin_memory,
    persistent_workers,
    samples_per_epoch=None,
):
    """
    Create dataloaders for train & val datasets.

    What is returned is a pair of factory functions λ.ds → dl.

    The test dataset is not included because it is not used during training.
    So far, the test_ds has never been needed during training, so it has
    not been included here.

    History note: it use to be the case that the dataloaders were created
    here and returned. However, this was changed for a number of reasons.
    Firstly, having dataset creation be lazy saves memory, and so dataloader
    creation should also be lazy. Secondly, we want to give more control to
    the Trainable, and instead of passing in a dataloader, we want to just
    say "please evaluate using the train dataset". We don't need to give in
    the dataset, as the Trainable is where train.py got access to it anyway.
    This might suggest a function like `trainable.evaluate_train(self)`;
    however, one missing piece is that the Trainable doesn't know how to
    create a dataloader. A few options remain:
        1. We give this responsibility to the DatasetManager. The downside of
        this is that the DatasetManager starts becoming a bit omniscient, and
        creating one becomes a bit of an unnecessary pain when we don't intend
        to train and may only want to run some inference.
        2. We could do 1. above, but leave a lot of default initialized
        options that we would expect train.py to set, such as batch_size.
        3. Pass a factory function λ.ds → dl to the Trainable when we call
        `trainable.evaluate_train(self)`. This is the approach taken here. We
        leave train.py with the responsibility of creating the dataloaders,
        and we keep the DatasetManager as a simple factory for datasets.
        A huge issue with 3 is that we can't reuse dataloaders! Adds massive
        time to evaluation. I'm starting to think the DatasetManager should
        do this.
        4. We could pass both a dataset and a dataloader or a dataset and a
        factory function λ.ds → d. This wont work, as in many cases the creation
        of the dataset must be done by the evaluate() function. For example,
        setting the stride of the dataset.
    """
    if persistent_workers:
        raise NotImplementedError(
            "persistent_workers is not yet supported due"
            "to segfault issue and dataloader exceeding dataset limits."
        )

    # Setting pin_memory=True. This is generally recommended when training on
    # Nvidia GPUs. See:
    #   - https://discuss.pytorch.org/t/when-to-set-pin-memory-to-true/19723
    #   - https://developer.nvidia.com/blog/how-optimize-data-transfers-cuda-cc/
    def sampler_fn(ds):
        if samples_per_epoch is None:
            return None
        # The comments suggest that replacement=False and num_samples can't be
        # set at the same time; however, inspecting the code suggests it's fine.
        # https://pytorch.org/docs/stable/_modules/torch/utils/data/sampler.html#Sampler
        sampler = torch.utils.data.RandomSampler(
            ds, replacement=False, num_samples=samples_per_epoch
        )
        return sampler

    def train_dl_fn(ds, collate_fn=None):
        res = torch.utils.data.DataLoader(
            ds,
            batch_size=batch_size,
            # shuffle must be False if a custom sampler is used.
            shuffle=False if samples_per_epoch is not None else True,
            drop_last=False,
            num_workers=n_workers,
            pin_memory=pin_memory,
            # Possible segfault issues when enabled. Also, possible issue with
            # dataloader passing beyond the epoch limit.
            # Disabled until fixed
            persistent_workers=persistent_workers,
            sampler=sampler_fn(ds),
            collate_fn=collate_fn,
        )
        return res

    def val_dl_fn(ds, collate_fn=None):
        res = torch.utils.data.DataLoader(
            ds,
            batch_size=eval_batch_size,
            # For debugging, it's nice to see a variety:
            shuffle=True,
            drop_last=False,
            num_workers=n_workers,
            pin_memory=pin_memory,
            # Temp disabled until seg fault is fixed.
            persistent_workers=persistent_workers,
            collate_fn=collate_fn,
        )
        return res

    return train_dl_fn, val_dl_fn


@contextmanager
def evaluating(model):
    """
    Context manager to set the model to eval mode and then back to train mode.

    Used this to prevent an exception leading to unexpected training state.
    """
    original_mode = model.training
    model.eval()
    try:
        model.eval()
        # TODO: torch compile forces model.training => True.
        # assert not model.training
        yield
    finally:
        # Switch back to the original training mode.
        model.train(original_mode)
        assert model.training == original_mode


class TrainCallbackList:
    """
    Document the available training callbacks.
    """

    def on_batch_start(self, step: int):
        pass

    def on_batch_end(self, step: int):
        pass

    def on_eval_start(self, step: int):
        pass

    def on_eval_end(self, step: int):
        pass


class Callback:
    """
    Currently, training is done in a stateless manner in train().

    An alternative is to have a stateful training setup, by creating a
    class Trainer that keeps data such as step and optimizer as properties.
    The benefit of a stateful approach is that callbacks can have a reference
    to the trainer and all callbacks can have an empty signature. The downside
    is that the callbacks are now coupled to the trainer, and so it's harder
    to reuse them in other contexts. It's clearly far more powerful to have
    access to a Trainer, and I'm leaning towards this approach. For now,
    we will be satisfied with a very basic callback interface without access
    to a stateful trainer.

    Another reason for a stateful approach is to allow "Control" callbacks:
    callbacks that can change the training state. Useful training state changes
    include changing the current learning rate, increasing/decreasing the
    number of epochs, early stopping, perturbing the model. A callback could
    hold a Queue of Actions which is populated by another thread, such as
    a gui.

    A compromise is no not have a Trainer, but have a TrainState object that can
    be edited by callbacks and is used by the train() function.
    """

    def before_train(self, trainable: Trainable, step: int):
        """
        Called after train() has completed setup, but before the first batch.

        Setup includes things like creating any loggers and configuring
        the optimizer.

        Step is 0 unless training is being resumed. Although, there currently
        isn't any support for resuming with an initialized step.
        """
        pass

    def before_batch(self, trainable: Trainable, step: int):
        pass

    def after_batch(self, trainable: Trainable, step: int):
        pass

    def after_train(self, trainable: Trainable, step: int):
        pass

    def before_eval(self, trainable: Trainable, step: int):
        pass

    def after_eval(self, trainable: Trainable, step: int):
        pass


class TensorTag(torch.nn.Module):
    """Use this module to log tensors.

    The trainer can add hooks to this module to log the tensors.

    It's more general than logging, but so far only used for logging.

    The forward's label argument will be used as the key in the log. If there
    is no label, then the module's label will be used.
    """

    def __init__(self, label: Optional[str] = None):
        super().__init__()
        self.label = label

    def forward(self, x, label: Optional[str] = None):
        return x


class MonitoringBase(nn.Module):
    """Example model that enables monitoring."""

    def modules_to_inspect(self) -> Dict[str, nn.Module]:
        """If this method is present, and train() is run with activations or
        weight monitoring enabled, then the modules in this list will have
        hooks attached for monitoring purposed."""
        return {}


class TensorLogger(Callback):
    "TODO: add options for switching between means and histograms." ""

    tag_class = TensorTag

    def __init__(self, tb_logger, steps_til_log=50):
        self.model = None
        self.step = 0
        self._is_enabled = False
        self.tb_logger = tb_logger
        self.last_log = -math.inf
        self.steps_til_log = steps_til_log
        self._hooks = []

    def before_train(self, trainable: Trainable, step: int):
        self.model = trainable.model
        self._add_hook(self.model)

    def before_batch(self, trainable: Trainable, step: int):
        self.step = step
        self._is_enabled = self.step - self.last_log > self.steps_til_log

    def after_batch(self, trainable: Trainable, step: int):
        self.step = step
        if self._is_enabled:
            self.last_log = self.step
        self._is_enabled = False

    def before_eval(self, trainable: Trainable, step: int):
        self._is_enabled = False

    def after_eval(self, trainable: Trainable, step: int):
        self._is_enabled = True

    def _log_hist(self, value, label):
        self.tb_logger.add_histogram(label, value, self.step)

    def _log_mean_sd(self, value, label):
        self.tb_logger.add_scalar(f"{label}_mean", value.mean(), self.step)
        self.tb_logger.add_scalar(f"{label}_std", value.std(), self.step)
        if self.step == 0:
            # The first step is very special, as we are eager for the mean and
            # sd of activations to be 0 and 1.
            warning_tol = 0.2
            m, v = value.mean(), value.var()
            log_as_warn = abs(m) > warning_tol or abs(v - 1) > warning_tol
            if log_as_warn:
                _logger.warning(
                    f"Model initialization. {label}. " f"Mean: {m}, Var: {v}"
                )
            else:
                _logger.info(
                    f"Model initialization. {label}. "
                    f"Mean: {value.mean()}, Var: {value.var()}"
                )

    def _log(self, value, label):
        if self._is_enabled:
            self._log_hist(value, label)

    @torch.no_grad()
    def _on_forward(self, module, args, kwargs, output) -> None:
        """
        Return None when the output is not modified
        """
        # args[0] is the passthrough tensor, x (same as output).
        label = kwargs.get("label", args[1]) if len(args) > 1 else None
        no_label_arg = label is None or label == ""
        if no_label_arg:
            assert hasattr(module, "label"), "TensorTag must have a label."
            label = module.label
        self._log(output, label)

    def _add_hook(self, model):
        def _add_hook(submodule):
            if isinstance(submodule, self.tag_class):
                self._hooks.append(
                    submodule.register_forward_hook(
                        self._on_forward, with_kwargs=True
                    )
                )

        model.apply(_add_hook)

    def _remove_hooks(self):
        for hook in self._hooks:
            hook.remove()

    def __del__(self):
        self._remove_hooks()


class TrainingTimers:
    """Collect timers here for convenience."""

    def __init__(self):
        self.batch = _logging.Timer()
        self.epoch = _logging.Timer()
        self.validation = _logging.Timer()
        self.recovery = _logging.Timer()

    @staticmethod
    def create_and_start():
        timer = TrainingTimers()
        timer.batch.restart()
        timer.epoch.restart()
        timer.recovery.restart()
        return timer


class EarlyStopper:
    """
    Your default choice should be to not use early stopping, especially when
    using cyclic learning rates. In lr upswings, it is normal to see the loss
    increase. Having said that, when doing experiments, early stopping can help
    drastically decreate compute requirements.

    When using early stopping for investigations, the best to customize it to
    your specific situation by make educated guesses about specific loss
    patterns and how they relate to whatever your end outputs are, such as
    matplotlib plots with vmin and vmax at some known levels.

    For example, when trying to make statements about dataset sizes, the tiny
    datasets are expected to overfit very quickly, and so we can use that
    information to de-risk a very agressive early stopping.
    """

    def __init__(
        self,
        min_epochs=0,
        min_steps=0,
        epoch_patience=0,
        step_patience=0,
        eval_patience=0,
        best_factor=1.0,
        w=0.8,
    ):
        self.min_epochs = min_epochs
        self.min_steps = min_steps
        self.epoch_patience = epoch_patience
        self.step_patience = step_patience
        self.eval_patience = eval_patience
        self.best_factor = best_factor
        self.w = w
        self.reset()

    def __str__(self):
        s = f"{self.__class__.__name__}("
        s += f"min_epochs={self.min_epochs}, "
        s += f"min_steps={self.min_steps}, "
        s += f"epoch_patience={self.epoch_patience}, "
        s += f"step_patience={self.step_patience}, "
        s += f"eval_patience={self.eval_patience}, "
        s += f"best_factor={self.best_factor}, "
        s += f"w={self.w})"
        return s

    def reset(self):
        """Allow a single EarlyStopper object to be reused."""
        self.best_sloss = None
        self.best_epoch = 0
        self.best_step = 0
        self.best_eval = 0
        self.current_eval = -1
        self.smooth_loss = None
        self.continuous_infs = 0
        self.infs_threshold = 4

    def _w(self):
        # Don't let w go below 1/n_evals. This makes faster updates at the
        # beginning. current_eval is the idx, and can be 0.
        n_evals = self.current_eval + 1
        w = max(1 / n_evals, self.w)
        return w

    def update(self, loss, epoch, step):
        def _update():
            self.current_eval += 1
            if self.smooth_loss is None:
                self.smooth_loss = loss
                self.best_sloss = loss
                self.best_epoch = epoch
                self.best_step = step
            else:
                w = self._w()
                self.smooth_loss = w * self.smooth_loss + (1 - w) * loss
            if math.isinf(loss):
                self.continuous_infs += 1

        _update()

        assert self.smooth_loss is not None
        # If found a new best, reset the markers. Don't stop early.
        if self.smooth_loss < self.best_sloss:
            _logger.info(
                f"[EarlyStopper] New best loss. {self.smooth_loss:.3e} < "
                f"{self.best_sloss:.3e}. Don't stop."
            )
            self.best_sloss = self.smooth_loss
            self.best_epoch = epoch
            self.best_step = step
            self.best_eval = self.current_eval
            do_early_stop = False
        # If we have too many infs, stop early.
        elif self.continuous_infs > self.infs_threshold:
            _logger.info(
                f"[EarlyStopper] {self.infs_threshold} sequential infs. Stop."
            )
            do_early_stop = True
        # Otherwise, check if we haven't seen improvement in a while.
        elif self.smooth_loss > self.best_sloss * self.best_factor:
            is_warmup = (epoch < self.min_epochs) or (step < self.min_steps)
            # epoch patience = 0 means just 1 epoch of no improvement causes
            # early stopping. Hence the >
            n_epochs_since_best = epoch - self.best_epoch
            n_steps_since_best = step - self.best_step
            n_evals_since_best = self.current_eval - self.best_eval
            epoch_stop = n_epochs_since_best > self.epoch_patience
            step_stop = n_steps_since_best > self.step_patience
            eval_stop = n_evals_since_best > self.eval_patience
            do_early_stop = (not is_warmup) and (
                epoch_stop and step_stop and eval_stop
            )
            if do_early_stop:
                _logger.info(
                    f"[EarlyStopper] No improvement for "
                    f"{n_epochs_since_best} epochs, "
                    f"{n_steps_since_best} steps, "
                    f"{n_evals_since_best} evals. Stop."
                )
        else:
            do_early_stop = False
        return do_early_stop


def configure_cuda():
    # Enable Cuda convolution auto-tuning. For more details, see:
    #   https://pytorch.org/tutorials/recipes/recipes/tuning_guide.html
    torch.backends.cudnn.benchmark = True

    # Create a GradScalar. For more details, see:
    #   https://pytorch.org/docs/stable/notes/amp_examples.html#amp-examples
    grad_scaler = torch.amp.GradScaler("cuda")
    return grad_scaler


def create_optimizer(model_params, lr, weight_decay):
    """
    No need to abstract the optimizer creation into the interface yet; however,
    it's used in two places now (train & lr_find), so at least deduplicate it
    to avoid insidious bugs.
    """
    res = torch.optim.AdamW(
        # Why use lr with AdamW, if we use a scheduler?
        # Because the scheduler isn't used for the first epoch? So start
        # slow, lr=lr/25.
        model_params,
        lr=lr,
        # Default eps is 1e-8, which can give us gradients in excess of 1e8.
        # Setting it lower, inspired by Jeremy Howard, to say 1e-5 can
        # prevent this.
        # eps=1e-5,
        weight_decay=weight_decay,
        # Beta default is (0.9, 0.999). Here, we instead follow Jeremy Howard
        # into the dark world of hyperparameter tuning and use (0.9, 0.99).
        # See: https://www.fast.ai/posts/2018-07-02-adam-weight-decay.html
        betas=(0.9, 0.99),
    )
    return res




def inspect_scheduler(
    scheduler_fn: Callable[
        [torch.optim.Optimizer], torch.optim.lr_scheduler.LRScheduler
    ],
    n_steps: int,
) -> Tuple[float, float, float, plotly.graph_objects.Figure]:
    dummy_parameters = torch.nn.Parameter(torch.zeros(1))
    dummy_optm = torch.optim.AdamW([dummy_parameters], lr=1e-3)
    scheduler = scheduler_fn(dummy_optm)
    lrs = []
    # Some schedulers complain if optimizer.step() is not called before the
    # scheduler step.
    dummy_optm.step()
    for i in range(n_steps):
        scheduler.step()
        lr = dummy_optm.param_groups[0]["lr"]
        lr2 = scheduler.get_last_lr()[0]
        assert lr == lr2
        lrs.append(lr)
    min_lr = min(lrs)
    max_lr = max(lrs)
    last_lr = lrs[-1]
    return min_lr, max_lr, last_lr, lrs


SchedulerFn: TypeAlias = Callable[
    [torch.optim.Optimizer], torch.optim.lr_scheduler.LRScheduler
]


def train(
    trainable: Trainable,
    n_epochs: int,
    batch_size: int,
    lr: float,
    weight_decay: float,
    out_dir: Union[str, pathlib.Path],
    save_checkpoints: bool = True,
    steps_til_log: int = 1000,
    steps_til_eval: Optional[int] = None,
    evals_til_eval_train_ds: Optional[int] = None,
    early_stopper: Optional[EarlyStopper] = None,
    initial_checkpoint: Optional[Union[str, pathlib.Path]] = None,
    logger: Optional[Any] = None,
    n_workers: int = 4,
    pin_memory: bool = False,
    log_activations: bool = False,
    scheduler_fn: Optional[SchedulerFn] = None,
    callbacks: Optional[List[Callback]] = None,
    eval_batch_size: Optional[int] = None,
    max_n_checkpoints: int = 1,
    fuse_adam: bool = True,
    samples_per_epoch: Optional[int] = None,
):
    """
    Train a model.

    This is a training loop that works with any Trainable object.

    It encapsulates basic functionality like logging, checkpointing and
    choosing when to run an evalutaion. Users might be just as well off
    by copying the code to use as a baseline and modifying it to their needs.
    """
    logging.info(f"Training {trainable.label}")
    torch.set_float32_matmul_precision("high")
    out_dir = pathlib.Path(out_dir)
    # Setup output (logging & checkpoints).
    if not logger:
        tensorboard_dir = out_dir / "tensorboard"
        logger = _logging.TbLogger(tensorboard_dir)

    eval_batch_size = eval_batch_size or batch_size

    if callbacks is None:
        callbacks = []
    if log_activations:
        callbacks.append(TensorLogger(logger.writer))

    # Load the model & loss fn.
    # The order here is important when resuming from checkpoints. We must:
    # 1. Create model & log structure
    #     - logging the model summary has a secondary function of testing the
    #       model integrity: it will fail if the model cannot be constructed.
    #       We want to do this test before the time consuming step of loading
    #       the dataset.
    # 2. Send model to target device
    # 3. Load datasets
    # 4. Create optimizer & scheduler
    #     - these can be present in checkpoints.
    #     - the dataset length must be known to construct the initial scheduler.
    # 5. Initialize from checkpoint
    #     - last, after we have the model, optimizer and scheduler created.
    #
    # Further details:
    # Another reason the order is crucial is that the optimizer must be on the
    # gpu before having it's parameters populated, as there is no optimizer.gpu()
    # method (possibly coming: https://github.com/pytorch/pytorch/issues/41839).
    # An alternative would be to use the map_location argument. See the
    # discussion: https://github.com/pytorch/pytorch/issues/2830.
    model = trainable.model
    model.cuda()
    grad_scaler = configure_cuda()
    # Allow models to specify parameters with and without weight decay.
    if hasattr(model, "optim_param_groups"):
        with_decay, without_decay = model.optim_param_groups()
        params = [
            {"params": with_decay, "weight_decay": weight_decay},
            {"params": without_decay, "weight_decay": 0.0},
        ]
    else:
        params = model.parameters()
    optimizer = torch.optim.AdamW(
        # Why use lr with AdamW, if we use a scheduler?
        # Because the scheduler isn't used for the first epoch? So start
        # slow, lr=lr/25.
        params,
        lr=lr / 25,
        weight_decay=weight_decay,
        # Beta default is (0.9, 0.999). Here, we instead follow Jeremy Howard
        # into the dark world of hyperparameter tuning and use (0.9, 0.99).
        # See: https://www.fast.ai/posts/2018-07-02-adam-weight-decay.html
        betas=(0.9, 0.99),
        fused=fuse_adam,
    )

    model.train()
    # Before going any further, log model structure.
    out_file = out_dir / "model_summary.txt"
    with open(out_file, "w", encoding="utf-8") as f:
        # This is allowed to fail, as if the model has issues, we want to
        # get the errors from the actual training forward pass.
        summary = None
        try:
            summary = trainable.model_summary(batch_size=batch_size)
        except Exception as e:
            msg = (
                "Failed to generate model summary. Exception raised:\n"
                f"{str(e)}"
            )
            _logger.error(msg)
            summary = msg
        f.write(str(summary))

    metric_tracker = _logging.MetricTracker(out_dir)

    # Load the data.
    train_dl_fn, val_dl_fn = _create_dataloaders(
        batch_size=batch_size,
        eval_batch_size=eval_batch_size,
        n_workers=n_workers,
        pin_memory=pin_memory,
        persistent_workers=False,
        samples_per_epoch=samples_per_epoch,
    )
    # Go ahead and create the train_dl.
    # old: train_dl = train_dl_fn(trainable.train_ds())
    # This is part of BaseTrainable, and I guess it should be in all.
    if hasattr(trainable, "train_dl"):
        train_dl = trainable.train_dl(train_dl_fn)
    else:
        train_dl = train_dl_fn(trainable.train_ds())
    if samples_per_epoch is not None:
        assert len(train_dl) == 1 + (samples_per_epoch - 1) // batch_size
    total_n_steps = n_epochs * len(train_dl)

    # Scheduler is down here, after the dataset is loaded (to check size).
    split_percent = np.array(
        [
            len(trainable.train_ds()),
            len(trainable.val_ds()),
            len(trainable.test_ds()),
        ]
    )
    split_percent = np.round(100 * split_percent / split_percent.sum(), 1)
    # Log dataset details.
    _logger.info(
        "Dataset lengths:\n"
        f"\t{'train:':<6} {len(trainable.train_ds()):,}\n"
        f"\t{'val:':<6} {len(trainable.val_ds()):,}\n"
        f"\t{'test:':<6} {len(trainable.test_ds()):,}\n"
        f"Split ratio: {split_percent}"
    )
    # Log train loop details.
    _logger.info(
        "Train loop:\n"
        f"\tbatch size: {batch_size}\n"
        f"\teval batch size: {eval_batch_size}\n"
        f"\tepochs: {n_epochs}\n"
        f"\tsteps per epoch: {len(train_dl):,}\n"
        f"\ttotal steps: {total_n_steps:,}"
    )

    def _scheduler_fn(_optimizer):
        return torch.optim.lr_scheduler.OneCycleLR(
            _optimizer,
            max_lr=lr,
            # Either specify steps & epochs, or specify total steps manually.
            # steps_per_epoch=len(train_dl),
            # epochs=n_epochs,
            total_steps=total_n_steps,
            # Testing
            three_phase=True,
        )

    scheduler_fn = _scheduler_fn if scheduler_fn is None else scheduler_fn
    scheduler = scheduler_fn(optimizer)
    lr_min, lr_max, lr_last, lrs = inspect_scheduler(
        scheduler_fn, total_n_steps
    )
    _logging.log_scheduler(
                lr_min, lr_max, lr_last, scheduler.__class__.__name__, lrs,
        "lr_schedule.html"
    )
    # Record how many times schedule step is skipped due to grad scalar backoff.
    # We want to track this as too many steps will cause the resulting lr
    # schedule clipping to be significant.
    n_lr_steps_skipped = 0
    step = 0
    # Defined here as it is shared between both epoch and batch loops.
    stop_early = False

    model_saver = _logging.ModelSaver(
        out_dir,
        trainable.model,
        optimizer,
        scheduler,
        max_history=max_n_checkpoints,
    )

    if initial_checkpoint is not None:
        _logging.load_model_and_optimizer(
            model, initial_checkpoint, optimizer, scheduler
        )

    def _eval(use_train_ds: bool = False):
        for cb in callbacks:
            cb.before_eval(trainable, step)
        label = "train-ds" if use_train_ds else "val-ds"
        _logger.info(f"Running evaluation {label}")
        with evaluating(model), torch.no_grad(), timers.validation:
            if use_train_ds:
                eval_results = trainable.evaluate_train(train_dl_fn)
            else:
                eval_results = trainable.evaluate_val(val_dl_fn)
        logger.log(step, eval_results, label)
        if "metrics" not in eval_results:
            raise ValueError("Trainable.evaluate() must return metrics.")
        metrics = eval_results["metrics"]
        assert (
            metrics[0].name == "loss"
        ), "Currently, by convention, the first metric must be loss."
        _logging.print_metrics(metrics)
        logger.log_scalar(step, "eval-time", timers.validation.elapsed(), label)
        _logger.info(
            f"Finished evaluation in {round(timers.validation.elapsed())} sec "
            f"(rolling ave: {round(timers.validation.rolling_duration())} sec)"
        )
        for cb in callbacks:
            cb.after_eval(trainable, step)
        return metrics

    n_evals = 0

    def _eval_and_checkpoint():
        stop_early = False
        metrics = _eval()
        nonlocal n_evals  # yes, another sign that a class would give benefits.
        n_evals += 1
        if evals_til_eval_train_ds and n_evals % evals_til_eval_train_ds == 0:
            _eval(use_train_ds=True)

        assert (
            metrics[0].name == "loss"
        ), "By convention, the first metric must be loss."
        # If this on_metric_end type of behaviour grows, consider switching
        # to callbacks.
        # Using step (not batch_step).
        improved_metrics = metric_tracker.new_metrics(
            metrics,
            epoch,
            step,  # batch_step
        )
        if save_checkpoints:
            model_saver.save_step_checkpoint(step, improved_metrics)
            timers.recovery.restart()
        if early_stopper:
            should_stop = early_stopper.update(metrics[0].value, epoch, step)
            if should_stop:
                _logger.info(f"Early stopping triggered. {str(early_stopper)}")
                stop_early = True
        return stop_early

    _logger.info("Starting training loop.")
    timers = TrainingTimers.create_and_start()
    for cb in callbacks:
        cb.before_train(trainable, step)
    # Do an initial eval.
    _eval()
    # The length of the epoch inner loop is now clearly too long to be able
    # to understand it at a glance.
    # Meters to calculate smooth values for terminal logging.
    beta = max(1e-3, 1 / steps_til_log)
    loss_meter = _logging.MovingAverageMeter(beta, name="loss")
    lr_meter = _logging.MovingAverageMeter(beta, name="lr")
    model_mean, model_sd, grad_norm = (0, 0, 0)  # predefine for logging.
    for epoch in range(n_epochs):
        _logger.info(f"Starting epoch {epoch+1}/{n_epochs}\t({out_dir})")
        timers.epoch.restart()
        # fmt: off
        _logging.log_step(epoch, n_epochs, -1, len(train_dl), timers.epoch, timers.batch, loss_meter.avg, lr_meter.avg, model_mean, model_sd, grad_norm)
        # fmt: on
        for batch_step, sample in enumerate(train_dl):
            if batch_step > len(train_dl):
                import pdb

                pdb.set_trace()
                raise ValueError("Batch step exceeds length of train_dl.")
            for cb in callbacks:
                cb.before_batch(trainable, step)
            timers.batch.restart()
            # set_to_none=True is suggested to improve performance, according to:
            #   https://pytorch.org/tutorials/recipes/recipes/tuning_guide.html
            # A recipe for autocast, grad scaling and set_to_none:
            #   https://pytorch.org/tutorials/recipes/recipes/amp_recipe.html
            optimizer.zero_grad(set_to_none=True)
            with torch.autocast("cuda"):
                model_out, total_loss = trainable.forward(sample)
            grad_scaler.scale(total_loss).backward()
            ## Optional clipping.
            grad_scaler.unscale_(optimizer)
            MAX_NORM = 10000  # pretty much disabled. Kept around for logging.
            grad_norm = torch.nn.utils.clip_grad_norm_(
                model.parameters(), MAX_NORM
            )
            # Don't bother warning if infs are found, as the grad scaler
            # will skip the optimizer step anyway.
            grad_has_infs = grad_norm == float("inf")
            if not grad_has_infs:
                if grad_norm > MAX_NORM:
                    _logger.warning(
                        f"Gradients clipped. Norm: {grad_norm:.1e} > {MAX_NORM}"
                    )
            ## \Optional
            # dbg = {pn:(p, p.stride(), p.grad.stride() if p.grad is not None else 0) for pn, p in model.named_parameters() if p.grad is not None and p.grad.stride() != p.stride()}
            grad_scaler.step(optimizer)
            # Recording the before and after scale. Why? The grad scaler can
            # create NaN gradients in the first few iterations, and when it
            # does, it skips the updating of the optimizer. We want to
            # know when this happens so that we can also skip the learning
            # rate scheduler update.
            # ref: https://discuss.pytorch.org/t/optimizer-step-before-lr-scheduler-step-error-using-gradscaler/92930/10
            scale_before = grad_scaler.get_scale()
            grad_scaler.update()
            assert grad_scaler.get_backoff_factor() < 1.0, (
                "The logic for skipping the learning rate scheduler "
                "relies on the backoff factor being less than 1.0, which "
                "it is the default (0.5)."
            )
            scale_has_decreased = scale_before > grad_scaler.get_scale()
            skip_lr_sched = scale_has_decreased
            # get_last_lr() returns a list, but we only have one param group.
            last_lr = scheduler.get_last_lr()[0]
            lr_meter.update(last_lr)

            metrics = [
                _logging.Metric("loss", total_loss.item()),
            ]
            logger.log_metrics(step, metrics, log_group="train")
            logger.log_scalar(step, "epoch", epoch, log_group="train")
            logger.log_scalar(step, "lr", last_lr, log_group="train")
            logger.log_scalar(step, "grad_norm", grad_norm, log_group="train")

            # We log total_loss directly to logging framework, but log a
            # smoothed loss to the console.
            loss_meter.update(total_loss.item())
            # Log step. Periodically, and at the end of the epoch.
            is_last = batch_step + 1 == len(train_dl)
            # step + 1, as steps are displaed 1-indexed (so ahead).
            if (step > 0 and (step + 1) % steps_til_log == 0) or is_last:
                model_mean = torch.mean(model_out).item()
                model_sd = torch.std(model_out).item()
                _logging.log_step(
                    epoch,
                    n_epochs,
                    batch_step,
                    len(train_dl),
                    timers.epoch,
                    timers.batch,
                    loss_meter.avg,
                    lr_meter.avg,
                    model_mean,
                    model_sd,
                    grad_norm,
                )

            # Evaluate.
            # batch_step + 1, as steps are displayed 1-indexed (so ahead).
            # If switching back to (batch_step), make sure to skip 0.
            if steps_til_eval and (batch_step + 1) % steps_til_eval == 0:
                is_near_epoch_end = batch_step + steps_til_eval >= len(train_dl)
                if not is_near_epoch_end:
                    stop_early = _eval_and_checkpoint()
                    if stop_early:
                        break
            step_matches = (
                step == epoch * len(train_dl) + batch_step - n_lr_steps_skipped
            )
            if not step_matches:
                import pdb

                pdb.set_trace()

            # assert (
            #     step == epoch * len(train_dl) + batch_step - n_lr_steps_skipped
            # ), f"step: {step}, epoch: {epoch}, batch_step: {batch_step}"
            if not skip_lr_sched:
                if grad_has_infs:
                    raise ModelException(
                        "If infs found, step should be skipped. Might be in a "
                        "GradScaler death spiral (probably caused by your model "
                        "producing infs/NaNs)."
                    )
                if not torch.isfinite(total_loss):
                    raise ModelException(
                        "Loss is not finite. This is likely a model error."
                    )
                scheduler.step()
                # Option: do or [don't] increment step if grad scaler skipped.
                step += 1
            else:
                n_lr_steps_skipped += 1
                _logger.info(
                    f"GradScaler didn't step (step {step}). "
                    f"Total skipped: {n_lr_steps_skipped} "
                    f"({round(float(n_lr_steps_skipped)/(step+1)):>3.0%}). "
                    f"New scale: {grad_scaler.get_scale():.3f}"
                )
            # Recovery.
            # Don't allow training to proceed too long without checkpointing.
            if timers.recovery.elapsed() > RECOVERY_CKPT_PERIOD_SEC:
                model_saver.save_recovery()
                timers.recovery.restart()
            for cb in callbacks:
                cb.after_batch(trainable, step)
            # One more batch to dust!

        _logger.info(
            f"Finished epoch in {round(timers.epoch.elapsed())} secs "
            f"(rolling ave (train + eval): "
            f"{round(timers.epoch.rolling_duration())} s/epoch)"
        )
        # Evaluate and save at end of epoch. We may have already evaluated 
        # and decided to stop early, so check that first.
        stop_early = stop_early or _eval_and_checkpoint()
        if stop_early:
            break
    for cb in callbacks:
        cb.after_train(trainable, step)
    _logger.info(
        f"Finished training. {round(timers.epoch.total_elapsed())} "
        "secs elsapsed."
    )
    _logger.info(f"out_dir: {out_dir}")
    # If persistent workers is enabled, then when a dataloader is consumed,
    # it does not clean up it's workers, as they may be reused. I think this
    # leaves th deletion trigger to be delayed until Python's garbage
    # collection runs. This may happen some time later. If you are running
    # train() in a loop, then the deletion of workers might be delayed until
    # after the next dataloader is created. This could also happen if you hang
    # on to a reference to the dataloader after training. The BaseTrainable
    # caches dataloaders, so this could indeed be a problem!
    # A fix (https://github.com/pytorch/pytorch/pull/39869) that was made to
    # Pytorch to deal with hangning workers (why they might hang seems to be a
    # mystery), which checks all workers to see if they are alive. The source
    # for is_alive() is at:
    # https://github.com/python/cpython/blob/6fc643674983e27ec5cc312f2e83468050d1d364/Lib/multiprocessing/process.py#L153
    # The assert that we sometimes see fails because the process calling
    # worker.is_alive() is not the process that created the worker.
