import logging
import torch
import kddl.train
import kddl._logging
import torch.nn as nn
import torch.nn.functional as F
from tqdm import tqdm
import torchvision as tv

_logger = logging.getLogger(__name__)


def fashion_mnist_ds(tmp_dir=None):
    img_transform = tv.transforms.Compose(
        [
            tv.transforms.ToTensor(),
        ]
    )
    train_ds = tv.datasets.FashionMNIST(
        root=tmp_dir, train=True, download=True, transform=img_transform
    )
    test_ds = tv.datasets.FashionMNIST(
        root=tmp_dir, train=False, download=True, transform=img_transform
    )
    assert len(train_ds) == 60000 and len(test_ds) == 10000

    # Split off a validation set
    train_size, val_size = 50000, 10000
    train_ds, val_ds = torch.utils.data.random_split(
        train_ds,
        [train_size, val_size],
        generator=torch.Generator().manual_seed(123),
    )
    assert len(train_ds) == train_size and len(val_ds) == val_size

    # Check a few images
    for i in range(10):
        img, label = train_ds[i]
        assert img.shape == (1, 28, 28)
        assert 0 <= label < 10
        assert torch.all(img >= 0) and torch.all(img <= 255)
    return train_ds, val_ds, test_ds


def fashion_mnist_ds_mgr(fashion_mnist_ds):
    train_ds, val_ds, test_ds = fashion_mnist_ds
    # Extract underlying data for normalization statistics
    orig_train_ds = train_ds.dataset
    train_ds_indices = train_ds.indices
    train_imgs = orig_train_ds.data[train_ds_indices].float()
    assert train_imgs.shape == (50000, 28, 28)
    mean = torch.mean(train_imgs)
    sd = torch.std(train_imgs)
    min = torch.min(train_imgs)
    max = torch.max(train_imgs)
    res = kddl.train.BasicDatasetManager(
        train_ds,
        val_ds,
        test_ds,
        train_ds_attrs={"mean": mean, "sd": sd, "min": min, "max": max},
    )
    return res


@torch.no_grad()
def mean_0_var_1(
    forward_fn,
    input_fn,
    n_samples=int(1e2),
    mean_tol=0.1,
    var_tol=0.1,
    generator=None,
):
    """Send random data in and check the output has near mean 0 and variance 1."""
    if generator is None:
        generator = torch.Generator().manual_seed(123)
    m_out = []
    for _ in tqdm(range(n_samples)):
        inputs = input_fn()
        inputs = [i.normal_(generator=generator).cuda() for i in inputs]
        y = forward_fn(*inputs)
        m_out.append(y)
    out_shape = m_out[0].shape
    m_out = torch.stack(m_out)
    passed = True
    res = {}

    def within_tol(m, v):
        return torch.allclose(
            m, torch.zeros_like(m), atol=mean_tol
        ) and torch.allclose(v, torch.ones_like(v), atol=var_tol)

    mean = torch.mean(m_out)
    var = torch.var(m_out)
    if not within_tol(mean, var):
        passed = False

    details = (
        f"Requirement: {-mean_tol} < mean < {mean_tol}, 1 - {var_tol} < var < 1 + {var_tol}\n"
        f"Actual: mean={mean:.3e}, var={var:.3e}"
    )

    return passed, details


class Cnn1(nn.Module):
    """
    Copied from PyTorch's MNIST example: https://github.com/pytorch/examples/blob/1bef748fab064e2fc3beddcbda60fd51cb9612d2/mnist/main.py

    We did tweak the normalization.
    """

    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, 1)
        self.conv2 = nn.Conv2d(32, 64, 3, 1)
        self.dropout1 = nn.Dropout(0.25)
        self.dropout2 = nn.Dropout(0.5)
        self.fc1 = nn.Linear(9216, 128)
        self.fc2 = nn.Linear(128, 10)
        self.register_buffer("mean", torch.tensor(0.0))
        self.register_buffer("sd", torch.tensor(1.0))

    def set_mean_sd(self, mean, sd):
        self.mean = mean
        self.sd = sd

    def input_norm(self, x):
        return (x - self.mean) / self.sd

    def forward(self, x):
        x = self.input_norm(x)
        x = self.conv1(x)
        x = F.relu(x)
        x = self.conv2(x)
        x = F.relu(x)
        x = F.max_pool2d(x, 2)
        x = self.dropout1(x)
        x = torch.flatten(x, 1)
        x = self.fc1(x)
        x = F.relu(x)
        x = self.dropout2(x)
        x = self.fc2(x)
        output = F.log_softmax(x, dim=1)
        return output


class FastaiCnn1(nn.Module):
    """
    Copied from Fastai's MNIST example: https://github.com/fastai/course22p2/blob/master/nbs/10_activations.ipynb
    """

    def __init__(self):
        super().__init__()
        self.register_buffer("mean", torch.tensor(0.0))
        self.register_buffer("sd", torch.tensor(1.0))
        self.layers = nn.Sequential(*self.cnn_layers())

    @staticmethod
    def conv(ni, nf, ks=3, act=True):
        res = nn.Conv2d(ni, nf, kernel_size=ks, stride=2, padding=ks // 2)
        if act:
            res = nn.Sequential(res, nn.ReLU())
        return res

    @classmethod
    def cnn_layers(cls):
        res = [
            cls.conv(1, 8, ks=5),  # 14x14
            cls.conv(8, 16),  # 7x7
            cls.conv(16, 32),  # 4x4
            cls.conv(32, 64),  # 2x2
            cls.conv(64, 10, act=False),  # 1x1
            nn.Flatten(),
        ]
        return res

    def set_mean_sd(self, mean, sd):
        self.mean = mean
        self.sd = sd

    def input_norm(self, x):
        return (x - self.mean) / self.sd

    def forward(self, x):
        x = self.input_norm(x)
        for layer in self.layers:
            x = layer(x)
        x = F.log_softmax(x, dim=1)
        return x


class ClassifyTrainable(kddl.train.Trainable):
    def __init__(self, ds_mgr, model, label):
        super().__init__(model, label)
        self.ds_mgr = ds_mgr
        self.model.set_mean_sd(ds_mgr.mean, ds_mgr.sd)

    def loss_fn(self, m_out, y):
        loss = F.nll_loss(m_out, y, reduction="mean")
        return loss

    def train_ds(self):
        return self.ds_mgr.train_ds()

    def val_ds(self):
        return self.ds_mgr.val_ds()

    def test_ds(self):
        return self.ds_mgr.test_ds()

    def forward(self, sample):
        x, y = sample
        x = x.cuda()
        y = y.cuda()
        m_out = self.model(x)
        loss = self.loss_fn(m_out, y)
        return m_out, loss

    @torch.no_grad()
    def evaluate(self, dl):
        if self.model.training:
            _logger.warning("Model should be in eval mode")
        loss_meter = kddl._logging.Meter("loss")
        acc_meter = kddl._logging.Meter("accuracy")
        for sample in dl:
            x, y = sample
            y = y.cuda()
            N = x.shape[0]
            output, loss = self.forward(sample)
            pred = output.argmax(dim=1, keepdim=True)
            n_correct = pred.eq(y.view_as(pred)).sum().item()
            acc_meter.update(n_correct / N, N)
            loss_meter.update(loss.item(), N)
        return {
            "metrics": [
                kddl._logging.loss_metric(loss_meter.avg),
                kddl._logging.Metric(
                    "accuracy", acc_meter.avg, increasing=True
                ),
            ]
        }

    def evaluate_train(self, dl_fn):
        return self.evaluate(dl_fn(self.train_ds()))

    def evaluate_val(self, dl_fn):
        return self.evaluate(dl_fn(self.val_ds()))
