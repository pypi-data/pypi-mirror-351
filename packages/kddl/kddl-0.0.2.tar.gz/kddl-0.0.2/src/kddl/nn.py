import logging
import math
from typing import Callable, Optional, Union
from numpy.typing import ArrayLike
import einops
import torch
import torch.nn as nn
from torch.nn import functional as F


_logger = logging.getLogger(__name__)


def get_optim_param_groups(module):
        """Return parameters with and without decay, in separate groups.

        This function signature is designated by train.py.
        """
        with_grad = {
            n: p for n, p in module.named_parameters() if p.requires_grad
        }
        # Collect set of all embedding parameters.
        embedding_params = set()
        for module in module.modules():
            if isinstance(module, nn.Embedding):
                for param in module.parameters(recurse=False):
                    embedding_params.add(id(param))

        def with_decay_fn(param):
            single_dim = param.dim() == 1
            is_embedding = id(param) in embedding_params
            with_decay = not (single_dim or is_embedding)
            return with_decay

        with_decay_params = []
        without_decay_params = []
        with_decay_names = []
        without_decay_names = []
        for n, p in with_grad.items():
            if with_decay_fn(p):
                with_decay_params.append(p)
                with_decay_names.append(n)
            else:
                without_decay_params.append(p)
                without_decay_names.append(n)
        _logger.info(f"Params with decay: {', '.join(with_decay_names)}")
        _logger.info(f"Params without decay: {', '.join(without_decay_names)}")
        return [with_decay_params, without_decay_params]


class NormMask(nn.Module):
    """Normalize, but set masked values to 0.

    Sequences can contain padding, which uses some padding value (e.g. 0, -1).
    We want to normalize these sequences, which will send padded values to
    some arbitrary value. To handle this, we set the masked values to 0 after
    normalization. We have lost the original distinction between padding and
    real values—this is the cost of normalization.

    Given that the mask will be needed (otherwise one would just use 
    Normalize), we will go ahead and concatenate the mask to the input. This
    implementation assumes a channel-last format.

    We could alternatively take in the pad value and construct and return the
    mask here. So for this hasn't been needed as a mask has been available as
    it is used by Trainables.
    """
    def __init__(self):
        super().__init__()
        self.register_buffer("mean", torch.zeros(size=[]))
        self.register_buffer("sd", torch.ones(size=[]))

    def set_mean_sd(self, m: ArrayLike, sd: ArrayLike):
        self.mean = torch.tensor(m)
        self.sd = torch.tensor(sd)
        if self.mean.ndim != 0:
            raise ValueError(
                f"Expected mean to be a scalar; got ({self.mean.ndim}) dims."
            )
        if self.sd.ndim != 0:
            raise ValueError(
                f"Expected sd to be a scalar; got ({self.sd.ndim}) dims."
            )

    def forward(self, x, mask):
        """
        Args:
            x [batch, seq_len, n_features]
            mask [batch, seq_len]:  1s for valid, 0s for invalid.
        Returns:
            x [batch, seq_len, n_features+1]
        """
        x = self.norm(x)
        mask = einops.rearrange(mask, "b s -> b s 1")
        x = x * mask
        x = torch.cat([x, mask], dim=-1)
        return x

    def norm(self, x):
        return (x - self.mean) / self.sd

    def denorm(self, x):
        return x * self.sd + self.mean


class Normalize(nn.Module):
    def __init__(self):
        super().__init__()
        self.register_buffer("mean", torch.zeros(size=[]))
        self.register_buffer("sd", torch.ones(size=[]))

    def set_mean_sd(self, m: ArrayLike, sd: ArrayLike):
        self.mean = torch.tensor(m)
        self.sd = torch.tensor(sd)
        if self.mean.ndim != 0:
            raise ValueError(
                f"Expected mean to be a scalar; got ({self.mean.ndim}) dims."
            )
        if self.sd.ndim != 0:
            raise ValueError(
                f"Expected sd to be a scalar; got ({self.sd.ndim}) dims."
            )

    def forward(self, x, shift=True, scale=True):
        shift = self.mean if shift else 0
        scale = self.sd if scale else 1
        return (x - shift) / self.sd

    def denorm(self, x):
        return x * self.sd + self.mean


class IdxEmbed(nn.Module):
    def __init__(self, length, n_embd):
        super().__init__()
        self.n_embd = n_embd
        self.length = length
        self.pos_embd = nn.Embedding(self.length, self.n_embd)
        self.register_buffer(
            "range_cache",
            einops.rearrange(torch.arange(self.length), "L -> 1 L"),
            persistent=False,
        )

    def forward(self):
        return self.pos_embd(self.range_cache)


class ValueEmbed(nn.Module):
    """Convert scalars to a fixed sized vector.

    Can be used for timestamps or single dimension data.
    """

    def __init__(self, n_embd):
        super().__init__()
        self.n_embd = n_embd
        self.register_buffer("slope", torch.zeros(self.n_embd // 2))

    @torch.no_grad()
    def init_weights(self, max_range, epsilon):
        # Use up most of the range [0, 2π] by landing on 3/4 * 2π.
        min_scale = (3 / 2 * math.pi) / max_range
        max_scale = (3 / 2 * math.pi) / epsilon
        self.slope.data = torch.exp(
            torch.linspace(
                math.log(min_scale),
                math.log(max_scale),
                self.n_embd // 2,
                dtype=torch.float32,
                requires_grad=False,
            )
        )

    def forward(self, t):
        t = self.slope * t#.unsqueeze(-1)
        t = torch.cat([t.sin(), t.cos()], dim=-1).to(dtype=torch.float32)
        return t


def create_batch_norm(n: int) -> nn.Module:
    """
    Following Davis and Frank's recommendation in "Revisiting Batch
    Normalization", we would initialize batch norm weights to less than 1
    (they suggested to use 0.1). They also recommended using a lower learning
    rate for the γ parameter.

    For comparison, fastai initialize β to 0.001 and γ to 1.

    I tried both, and found better results with fastai's defaults.
    """
    bn = nn.BatchNorm1d(n)
    # fastai
    # bn.weight.data.fill_(1.0)
    # bn.bias.data.fill_(1e-3)
    # Davis and Frank
    bn.weight.data.fill_(0.1)
    bn.bias.data.fill_(0)
    return bn


def create_shortcut(in_n, out_n, stride, num_dim=1):
    """Residual connection.

    The identify path is one of those finicky bits of ResNet type networks.

    Depending on whether the input and output match in terms of channel
    count and dimension, we have the following behaviour:

    Match?
    ------

        | Channel count | Dimensions | Bevaviour                  |
        |---------------|------------|----------------------------|
        |      ✓        |     ✓      | identity                   |
        |      ✓        |     ✘      | pool or conv               |
        |      ✘        |     ✓      | 1x1 conv                   |
        |      ✘        |     ✘      | pool or conv and 1x1 conv  |


    The most interesting choice is whether to use a strided pool or a
    strided convolution to achieve the downsampling effect. It's
    interesting as implementations are split on which one to use. There
    are further choices too, such as whether to use dilation in addition
    to strides, and whether to downsample before or after the 1x1 conv.

    Some implementations for reference:
        - fastai: https://github.com/fastai/fastai/blob/aa58b1316ad8e7a5fa2e434e15e5fe6df4f4db56/nbs/01_layers.ipynb
        - lightning: https://github.com/Lightning-AI/lightning-bolts/blob/master/pl_bolts/models/self_supervised/resnets.py
        - pytorch image models: https://github.com/rwightman/pytorch-image-models/blob/master/timm/models/resnet.py
             - there are two functions, downsample_conv() and
               downsample_avg() that are used to create the downsampling for
               the shortcut connection.
             - uses ceil_mode=True, so a dimension n=7 would be reduced to
               n=4, not n=3.

    My gut instinct is that swapping out pooling for convolution to achieve
    the downsample will naively achieve better results; however, the
    convolution is intrinsically more powerful (actual has parameters) and
    so, if you care about parameter counts, then a fair comparison would
    involve reducing parameters elsewhere. Given that the whole point of
    the residual layer is to short circuit a layer and allow gradients to
    flow easily, I think that pooling gets more theory points for staying
    true to this idea. Ironically, I think the original ResNet
    implementation might have used convolution."""
    # 1. Identity
    # In the simplest case, we can just return the input. For this to work,
    # both the channel count and channel dimensions of the input and output
    # must match. The output channel dimension is determined by the stride.
    if num_dim == 1:
        poolXdClass = nn.AvgPool1d
        convXdClass = nn.Conv1d
    elif num_dim == 2:
        poolXdClass = nn.AvgPool2d
        convXdClass = nn.Conv2d
    else:
        raise ValueError(f"Only 1d and 2d supported; got ({num_dim}).")
    channels_match = in_n == out_n
    downsample = stride > 1
    if channels_match and not downsample:
        return nn.Identity()

    skip_layers = []
    # 2. Downsample
    if downsample:
        # The following (1, 7) input:
        # |  1  |  2  |  3  |  4  |  5  |  6  |  7  |
        # when pooled with stride=kernel=2 becomes (1, 4):
        # |    1.5    |    3.5    |    5.5   | 7 |
        pool = poolXdClass(
            kernel_size=stride,
            stride=stride,
            count_include_pad=False,
            ceil_mode=True,
        )
        skip_layers.append(pool)
    # 3. 1x1 conv
    if not channels_match:
        # There isn't a consensus on whether:
        #   - to use batch norm or a bias or neither.
        conv = convXdClass(in_n, out_n, kernel_size=1, bias=False)
        # TODO: how is best to initialize this connection?
        skip_layers.append(conv)
    res = nn.Sequential(*skip_layers)
    return res


@torch.no_grad()
def sinusoidal_embedding(length: int, n_ch: int) -> torch.Tensor:
    """
    Create a tensor of shape [time_steps, n_channels//2] and fill all rows with
    the sequence: [0, 1, 2, ..., length-1]. Then, scale each row by a different
    value. The list of scaling values are chosen to span from 1 to 1/10000.
    The 0th channel is scaled by 1, then gradually the scale is reduced
    until the last channel, (n_ch//2 -1), is scaled by 1/10000. The steps are
    exponentially spaced, so the scaling will initially rapidly decrease, then
    slow down as the minimum is approached.
    This resulting array is used as input to two functions: sine and cos, and
    the two results are concatenated in order to get a tensor of shape
    [time_steps, n_channels].
    """
    half_nch = n_ch // 2
    # From 1 to 1/10000, exponentially in half_nch steps.
    slope = (
        torch.arange(half_nch, dtype=torch.float)
        * -math.log(10000)
        / (half_nch - 1)
    ).exp()
    t = slope[:, None] * torch.arange(length, dtype=torch.float)[None, :]
    res = torch.cat([t.sin(), t.cos()], dim=0).to(dtype=torch.float32)
    return res


class Attention(nn.Module):
    def __init__(
        self, n_embd, heads=4, dropout=0.0, project_out=True, is_causal=False
    ):
        super().__init__()
        self.project_out = project_out
        self.dim_head = int(n_embd / heads)
        if self.dim_head != n_embd / heads:
            raise ValueError(
                f"n_embd ({n_embd}) must be divisible by heads ({heads})"
            )
        self.heads = heads
        self.is_causal = is_causal

        self.to_qkv = nn.Linear(n_embd, n_embd * 3, bias=False)
        self.to_out = (
            nn.Sequential(
                nn.Linear(n_embd, n_embd),
                nn.Dropout(dropout),
            )
            if self.project_out
            else nn.Identity()
        )
        self.norm = nn.LayerNorm(n_embd)
        self.dropout_rate = dropout

    def forward(self, x, mask=None):
        x = self.norm(x)
        qkv = self.to_qkv(x).chunk(3, dim=-1)
        q, k, v = map(
            lambda t: einops.rearrange(t, "b t (h c) -> b h t c", h=self.heads),
            qkv,
        )

        # q = q * self.scale
        # raw_attn = torch.einsum("b h i d, b h j d -> b h i j", q, k)
        # attn = raw_attn.softmax(dim=-1)
        # attn = self.dropout(attn)
        # out = torch.einsum("b h i j, b h j d -> b h i d", attn, v)
        dropout_rate = self.dropout_rate if self.training else 0.0
        # Note: can't set both attN_mask and is_causal, so do our own masking.
        out = F.scaled_dot_product_attention(
            q, k, v, dropout_p=dropout_rate, is_causal=self.is_causal
        )
        out = einops.rearrange(out, "b h t d -> b t (h d)")
        out = self.to_out(out)
        if mask is not None:
            out = out * mask
        return out


class FeedForward(nn.Module):
    def __init__(self, n_embd, hidden_dim, dropout=0.0):
        super().__init__()
        self.input_norm = nn.LayerNorm(n_embd)
        self.linear1 = nn.Linear(n_embd, hidden_dim)
        self.dropout = nn.Dropout(dropout)
        self.linear2 = nn.Linear(hidden_dim, n_embd)

    def forward(self, x):
        x = self.input_norm(x)
        x = self.linear1(x)
        x = self.dropout(F.gelu(x))
        x = self.linear2(x)
        x = self.dropout(x)
        return x


class Transformer(nn.Module):
    def __init__(
        self, dim, depth, heads, mlp_dim, dropout=0.0, is_causal=False
    ):
        super().__init__()
        self.layers = nn.ModuleList([])
        for _ in range(depth):
            self.layers.append(
                nn.ModuleList(
                    [
                        Attention(
                            dim,
                            heads,
                            dropout,
                            project_out=True,
                            is_causal=is_causal,
                        ),
                        FeedForward(dim, mlp_dim, dropout=dropout),
                    ]
                )
            )

    def forward(self, x, attn_mask=None):
        # TODO: rework mask handling, as it's not really the classic attn mask.
        if attn_mask is not None:
            attn_mask = einops.rearrange(attn_mask, "b s -> b s 1")
        for attn, ff in self.layers:
            x = attn(x, attn_mask) + x
            x = ff(x) + x
        return x


class SEModule(nn.Module):
    def __init__(self, n_channels, reduction=1):
        super().__init__()
        n_mid = n_channels // reduction
        self.fc1 = nn.Conv1d(n_channels, n_mid, kernel_size=1)
        self.relu = nn.ReLU(inplace=True)
        self.fc2 = nn.Conv1d(n_mid, n_channels, kernel_size=1)
        self.sigmoid = nn.Sigmoid()

    def init_weights(self):
        nn.init.kaiming_normal_(self.fc1.weight, mode="fan_in")
        nn.init.xavier_uniform_(self.fc2.weight)

    def forward(self, x):
        module_input = x
        x = x.mean((2,), keepdim=True)
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        x = self.sigmoid(x)
        return module_input * x

class ResBlock1d(nn.Module):
    """A residual block with 1d convolutions.

    This is a pretty inflexible implementation. No need to make it any
    more general yet.
    """

    def __init__(
        self,
        in_n,
        mid_n,
        out_n,
        kernel_size=3,
        downsample=False,
        dropout: float = 0,
        act_fn: Optional[Callable[[torch.Tensor], torch.Tensor]] = F.relu,
        norm_factory: Optional[
            Callable[[int], torch.nn.Module]
        ] = create_batch_norm,
    ):
        """
        Args:
            act_fn: A function like F.relu.
            norm_factory: a function that returns a Pytorch module. Other
                libraries take a class, and call Class(...) making the __init__
                effectively a factory. However, if you want to do any parameter
                initialization or anything, the interface must be a standard
                function.
        """
        super(ResBlock1d, self).__init__()
        self.downsample = downsample
        self.dropout_rate = dropout
        self.act_fn = identity_fn if act_fn is None else act_fn
        self.norm_factory = (
            create_identity if norm_factory is None else norm_factory
        )
        stride = 2 if self.downsample else 1
        self.shortcut = create_shortcut(in_n, out_n, stride=stride)
        # Note: bias is False for the conv layers, as they will be followed
        # by batch norm.
        self.conv1 = nn.Conv1d(
            in_n,
            mid_n,
            kernel_size=1,
            stride=1,
            padding=0,
            dilation=1,
            bias=False,
        )
        padding = (kernel_size - 1) // 2
        self.conv2 = nn.Conv1d(
            mid_n,
            mid_n,
            kernel_size=kernel_size,
            stride=stride,
            padding=padding,
            dilation=1,
            bias=False,
        )
        self.conv3 = nn.Conv1d(
            mid_n,
            out_n,
            kernel_size=1,
            stride=1,
            padding=0,
            dilation=1,
            bias=False,
        )
        self.dropout = (
            nn.Dropout(p=self.dropout_rate)
            if self.dropout_rate > 0
            else nn.Identity()
        )
        # To use batch norm or group norm?
        self.bn1 = self.norm_factory(mid_n)
        self.bn2 = self.norm_factory(mid_n)
        self.bn3 = self.norm_factory(out_n)

        self.se = SEModule(out_n)

    def init_weights(self):
        nn.init.kaiming_normal_(
            self.conv1.weight, mode="fan_in", nonlinearity="relu"
        )
        nn.init.kaiming_normal_(
            self.conv2.weight, mode="fan_in", nonlinearity="relu"
        )
        if self.act_fn == F.relu:
            nn.init.kaiming_normal_(
                self.conv3.weight, mode="fan_in", nonlinearity="relu"
            )
        else:
            _logger.info(
                "conv3 has no activation function; no attempt is made "
                "to guess a good normalization."
            )

    def forward(self, x):
        shortcut = self.shortcut(x)
        x = self.act_fn(self.bn1(self.conv1(x)))
        x = self.act_fn(self.bn2(self.conv2(x)))
        x = self.dropout(x)
        x = self.act_fn(self.bn3(self.conv3(x)))
        # todo: old or new?
        # old:
        #x = self.se(x) + shortcut
        #x = self.act_fn(x)
        # new:
        x = x + shortcut
        x = self.se(x)
        return x
