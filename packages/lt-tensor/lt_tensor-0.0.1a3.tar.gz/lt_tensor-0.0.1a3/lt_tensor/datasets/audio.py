__all__ = ["AudioProcessor"]
from ..torch_commons import *
import torchaudio
from typing import TypeAlias, Union, Optional
from lt_utils.common import PathLike
import librosa
from lt_utils.type_utils import is_file
from torchaudio.functional import resample
from ..transform import inverse_transform


class AudioProcessor:

    def __init__(
        self,
        sample_rate: int = 24000,
        n_mels: int = 80,
        n_fft: int = 2048,
        win_length: int = 2048,
        hop_length: int = 256,
        f_min: float = 0,
        f_max: float | None = None,
        mean: int = -4,
        std: int = 4,
        n_iter: int = 32,
        center: bool = True,
        mel_scale: str = "htk",
        inv_n_fft: int = 16,
        inv_hop: int = 4,
    ):
        self.mean = mean
        self.std = std
        self.n_mels = n_mels
        self.n_fft = n_fft
        self.n_stft = n_fft // 2 + 1
        self.f_min = f_min
        self.f_max = f_max
        self.n_iter = n_iter
        self.hop_length = hop_length
        self.sample_rate = sample_rate
        self.mel_spec = torchaudio.transforms.MelSpectrogram(
            sample_rate=sample_rate,
            n_mels=n_mels,
            n_fft=n_fft,
            win_length=win_length,
            hop_length=hop_length,
            center=center,
            f_min=f_min,
            f_max=f_max,
            mel_scale=mel_scale,
        )
        self.mel_rscale = torchaudio.transforms.InverseMelScale(
            n_stft=self.n_stft,
            m_mels=n_mels,
            sample_rate=sample_rate,
            f_min=f_min,
            f_max=f_max,
            mel_scale=mel_scale,
        )
        self.giffin_lim = torchaudio.transforms.GriffinLim(
            n_fft=n_fft,
            n_iter=n_iter,
            win_length=win_length,
            hop_length=hop_length,
        )
        self._inverse_transform = lambda x, y: inverse_transform(
            x, y, inv_n_fft, inv_hop, inv_n_fft
        )

    def inverse_transform(self, spec: Tensor, phase: Tensor):
        return self._inverse_transform(spec, phase)

    def compute_mel(
        self,
        wave: Tensor,
    ) -> Tensor:
        """Returns: [B, M, ML]"""
        mel_tensor = self.mel_spec(wave)  # [M, ML]
        mel_tensor = (mel_tensor - self.mean) / self.std
        return mel_tensor  # [B, M, ML]

    def reverse_mel(self, mel: Tensor, n_iter: Optional[int] = None):
        if isinstance(n_iter, int) and n_iter != self.n_iter:
            self.giffin_lim = torchaudio.transforms.GriffinLim(
                n_fft=self.n_fft,
                n_iter=n_iter,
                win_length=self.win_length,
                hop_length=self.hop_length,
            )
            self.n_iter = n_iter
        return self.giffin_lim.forward(
            self.mel_rscale(mel),
        )

    def load_audio(
        self,
        path: PathLike,
        top_db: float = 30,
    ) -> Tensor:
        is_file(path, True)
        wave, sr = librosa.load(str(path), sr=self.sample_rate)
        wave, _ = librosa.effects.trim(wave, top_db=top_db)
        return (
            torch.from_numpy(
                librosa.resample(wave, orig_sr=sr, target_sr=self.sample_rate)
                if sr != self.sample_rate
                else wave
            )
            .float()
            .unsqueeze(0)
        )
