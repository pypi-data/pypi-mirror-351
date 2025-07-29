__all__ = ["masked_cross_entropy"]
import math
import random
from .torch_commons import *
from lt_utils.common import *
import torch.nn.functional as F


def masked_cross_entropy(
    logits: torch.Tensor,  # [B, T, V]
    targets: torch.Tensor,  # [B, T]
    lengths: torch.Tensor,  # [B]
    reduction: str = "mean",
) -> torch.Tensor:
    """
    CrossEntropyLoss with masking for variable-length sequences.
    - logits: unnormalized scores [B, T, V]
    - targets: ground truth indices [B, T]
    - lengths: actual sequence lengths [B]
    """
    B, T, V = logits.size()
    logits = logits.view(-1, V)
    targets = targets.view(-1)

    # Create mask
    mask = torch.arange(T, device=lengths.device).expand(B, T) < lengths.unsqueeze(1)
    mask = mask.reshape(-1)

    # Apply CE only where mask == True
    loss = F.cross_entropy(
        logits[mask], targets[mask], reduction="mean" if reduction == "mean" else "none"
    )
    if reduction == "none":
        return loss
    return loss


def diff_loss(pred_noise, true_noise, mask=None):
    """Standard diffusion noise-prediction loss (e.g., DDPM)"""
    if mask is not None:
        return F.mse_loss(pred_noise * mask, true_noise * mask)
    return F.mse_loss(pred_noise, true_noise)


def hybrid_diff_loss(pred_noise, true_noise, alpha=0.5):
    """Combines L1 and L2"""
    l1 = F.l1_loss(pred_noise, true_noise)
    l2 = F.mse_loss(pred_noise, true_noise)
    return alpha * l1 + (1 - alpha) * l2


def gan_d_loss(real_preds, fake_preds, use_lsgan=True):
    loss = 0
    for real, fake in zip(real_preds, fake_preds):
        if use_lsgan:
            loss += F.mse_loss(real, torch.ones_like(real)) + F.mse_loss(
                fake, torch.zeros_like(fake)
            )
        else:
            loss += -torch.mean(torch.log(real + 1e-7)) - torch.mean(
                torch.log(1 - fake + 1e-7)
            )
    return loss


def gan_d_loss(real_preds, fake_preds, use_lsgan=True):
    loss = 0
    for real, fake in zip(real_preds, fake_preds):
        if use_lsgan:
            loss += F.mse_loss(real, torch.ones_like(real)) + F.mse_loss(
                fake, torch.zeros_like(fake)
            )
        else:
            loss += -torch.mean(torch.log(real + 1e-7)) - torch.mean(
                torch.log(1 - fake + 1e-7)
            )
    return loss


def gan_g_loss(fake_preds, use_lsgan=True):
    loss = 0
    for fake in fake_preds:
        if use_lsgan:
            loss += F.mse_loss(fake, torch.ones_like(fake))
        else:
            loss += -torch.mean(torch.log(fake + 1e-7))
    return loss


def feature_matching_loss(real_feats, fake_feats):
    """real_feats and fake_feats are lists of intermediate features"""
    loss = 0
    for real_layers, fake_layers in zip(real_feats, fake_feats):
        for r, f in zip(real_layers, fake_layers):
            loss += F.l1_loss(f, r.detach())
    return loss


def feature_loss(real_fmaps, fake_fmaps, weight=2.0):
    loss = 0.0
    for dr, dg in zip(real_fmaps, fake_fmaps):  # Each (layer list from a discriminator)
        for r_feat, g_feat in zip(dr, dg):
            loss += F.l1_loss(r_feat, g_feat)
    return loss * weight


def discriminator_loss(disc_real_outputs, disc_generated_outputs):
    loss = 0.0
    r_losses = []
    g_losses = []

    for dr, dg in zip(disc_real_outputs, disc_generated_outputs):
        r_loss = F.mse_loss(dr, torch.ones_like(dr))
        g_loss = F.mse_loss(dg, torch.zeros_like(dg))
        loss += r_loss + g_loss
        r_losses.append(r_loss)
        g_losses.append(g_loss)

    return loss, r_losses, g_losses


def generator_loss(fake_outputs):
    total = 0.0
    g_losses = []
    for out in fake_outputs:
        loss = F.mse_loss(out, torch.ones_like(out))
        g_losses.append(loss)
        total += loss
    return total, g_losses


def multi_resolution_stft_loss(y, y_hat, fft_sizes=[512, 1024, 2048]):
    loss = 0
    for fft_size in fft_sizes:
        hop = fft_size // 4
        win = fft_size
        y_stft = torch.stft(
            y, n_fft=fft_size, hop_length=hop, win_length=win, return_complex=True
        )
        y_hat_stft = torch.stft(
            y_hat, n_fft=fft_size, hop_length=hop, win_length=win, return_complex=True
        )

        loss += F.l1_loss(torch.abs(y_stft), torch.abs(y_hat_stft))
    return loss
