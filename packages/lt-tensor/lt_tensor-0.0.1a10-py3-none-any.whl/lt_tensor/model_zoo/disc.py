from ..torch_commons import *
import torch.nn.functional as F
from lt_tensor.model_base import Model
from lt_utils.common import *


class PeriodDiscriminator(Model):
    def __init__(
        self,
        period: int,
        use_spectral_norm=False,
        kernel_size: int = 5,
        stride: int = 3,
    ):
        super().__init__()
        self.period = period
        self.stride = stride
        self.kernel_size = kernel_size
        self.norm_f = weight_norm if use_spectral_norm == False else spectral_norm

        self.channels = [32, 128, 512, 1024, 1024]
        self.first_pass = nn.Sequential(
            self.norm_f(
                nn.Conv2d(
                    1, self.channels[0], (kernel_size, 1), (stride, 1), padding=(2, 0)
                )
            ),
            nn.LeakyReLU(0.1),
        )

        self.convs = nn.ModuleList(
            [
                self._get_next(self.channels[i + 1], self.channels[i], i == 3)
                for i in range(4)
            ]
        )

        self.post_conv = nn.Conv2d(1024, 1, (stride, 1), 1, padding=(1, 0))

    def _get_next(self, out_dim: int, last_in: int, is_last: bool = False):
        stride = (self.stride, 1) if not is_last else 1

        return nn.Sequential(
            self.norm_f(
                nn.Conv2d(
                    last_in,
                    out_dim,
                    (self.kernel_size, 1),
                    stride,
                    padding=(2, 0),
                )
            ),
            nn.LeakyReLU(0.1),
        )

    def forward(self, x: torch.Tensor):
        """
        x: (B, T)
        """
        b, t = x.shape
        if t % self.period != 0:
            pad_len = self.period - (t % self.period)
            x = F.pad(x, (0, pad_len), mode="reflect")
            t = t + pad_len

        x = x.view(b, 1, t // self.period, self.period)  # (B, 1, T//P, P)

        f_map = []
        x = self.first_pass(x)
        f_map.append(x)
        for conv in self.convs:
            x = conv(x)
            f_map.append(x)
        x = self.post_conv(x)
        f_map.append(x)
        return x.flatten(1, -1), f_map


class MultiPeriodDiscriminator(Model):
    def __init__(self, periods=[2, 3, 5, 7, 11]):
        super().__init__()

        self.discriminators = nn.ModuleList([PeriodDiscriminator(p) for p in periods])

    def forward(self, x: torch.Tensor):
        """
        x: (B, T)
        Returns: list of tuples of outputs from each period discriminator and the f_map.
        """
        return [d(x) for d in self.discriminators]


class ScaleDiscriminator(nn.Module):
    def __init__(self, use_spectral_norm=False):
        super().__init__()
        norm_f = weight_norm if use_spectral_norm == False else spectral_norm
        self.activation = nn.LeakyReLU(0.1)
        self.convs = nn.ModuleList(
            [
                norm_f(nn.Conv1d(1, 128, 15, 1, padding=7)),
                norm_f(nn.Conv1d(128, 128, 41, 2, groups=4, padding=20)),
                norm_f(nn.Conv1d(128, 256, 41, 2, groups=16, padding=20)),
                norm_f(nn.Conv1d(256, 512, 41, 4, groups=16, padding=20)),
                norm_f(nn.Conv1d(512, 1024, 41, 4, groups=16, padding=20)),
                norm_f(nn.Conv1d(1024, 1024, 41, 1, groups=16, padding=20)),
                norm_f(nn.Conv1d(1024, 1024, 5, 1, padding=2)),
            ]
        )
        self.post_conv = norm_f(nn.Conv1d(1024, 1, 3, 1, padding=1))

    def forward(self, x: torch.Tensor):
        """
        x: (B, T)
        """
        f_map = []
        x = x.unsqueeze(1)  # (B, 1, T)
        for conv in self.convs:
            x = self.activation(conv(x))
            f_map.append(x)
        x = self.post_conv(x)
        f_map.append(x)
        return x.flatten(1, -1), f_map


class MultiScaleDiscriminator(Model):
    def __init__(self):
        super().__init__()
        self.pooling = nn.AvgPool1d(4, 2, padding=2)
        self.discriminators = nn.ModuleList(
            [ScaleDiscriminator(i == 0) for i in range(3)]
        )

    def forward(self, x: torch.Tensor):
        """
        x: (B, T)
        Returns: list of outputs from each scale discriminator
        """
        outputs = []
        for i, d in enumerate(self.discriminators):
            if i != 0:
                x = self.pooling(x)
            outputs.append(d(x))
        return outputs


class GeneralLossDescriminator(Model):
    """TODO: build an unified loss for both mpd and msd here."""

    def __init__(self):
        super().__init__()
        self.mpd = MultiPeriodDiscriminator()
        self.msd = MultiScaleDiscriminator()
        self.print_trainable_parameters()

    def _get_group_(self):
        pass

    def forward(self, x: Tensor, y_hat: Tensor):
        return


def discriminator_loss(d_outputs_real, d_outputs_fake):
    loss = 0.0
    for real_out, fake_out in zip(d_outputs_real, d_outputs_fake):
        real_score = real_out[0]
        fake_score = fake_out[0]
        loss += torch.mean(F.relu(1.0 - real_score)) + torch.mean(
            F.relu(1.0 + fake_score)
        )
    return loss


def generator_adv_loss(d_outputs_fake):
    loss = 0.0
    for fake_out in d_outputs_fake:
        fake_score = fake_out[0]
        loss += -torch.mean(fake_score)
    return loss


def feature_matching_loss(
    d_outputs_real,
    d_outputs_fake,
    loss_fn: Callable[[Tensor, Tensor], Tensor] = F.mse_loss,
):
    loss = 0.0
    for real_out, fake_out in zip(d_outputs_real, d_outputs_fake):
        real_feats = real_out[1]
        fake_feats = fake_out[1]
        for real_f, fake_f in zip(real_feats, fake_feats):
            loss += loss_fn(fake_f, real_f)
    return loss
