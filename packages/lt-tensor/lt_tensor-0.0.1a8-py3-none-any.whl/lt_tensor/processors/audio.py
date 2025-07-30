__all__ = ["AudioProcessor"]
from lt_tensor.torch_commons import *
from lt_utils.common import *
from lt_utils.type_utils import is_file, is_array
from lt_tensor.misc_utils import log_tensor
import librosa
import torchaudio

from lt_tensor.transform import InverseTransformConfig, InverseTransform
from lt_utils.file_ops import FileScan, get_file_name, path_to_str

from lt_tensor.model_base import Model


class AudioProcessor(Model):
    def __init__(
        self,
        sample_rate: int = 24000,
        n_mels: int = 80,
        n_fft: int = 1024,
        win_length: Optional[int] = None,
        hop_length: Optional[int] = None,
        f_min: float = 0,
        f_max: float | None = None,
        n_iter: int = 32,
        center: bool = True,
        mel_scale: Literal["htk", "slaney"] = "htk",
        std: int = 4,
        mean: int = -4,
        inverse_transform_config: Union[
            Dict[str, Union[Number, Tensor, bool]], InverseTransformConfig
        ] = dict(n_fft=16, hop_length=4, win_length=16, center=True),
        *__,
        **_,
    ):
        super().__init__()
        assert isinstance(inverse_transform_config, (InverseTransformConfig, dict))
        self.mean = mean
        self.std = std
        self.n_mels = n_mels
        self.n_fft = n_fft
        self.n_stft = n_fft // 2 + 1
        self.f_min = f_min
        self.f_max = f_max
        self.n_iter = n_iter
        self.hop_length = hop_length or n_fft // 4
        self.win_length = win_length or n_fft
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
            n_mels=n_mels,
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
        if isinstance(inverse_transform_config, dict):
            inverse_transform_config = InverseTransformConfig(
                **inverse_transform_config
            )
        self._inv_transform = InverseTransform(**inverse_transform_config.to_dict())

    def inverse_transform(self, spec: Tensor, phase: Tensor, *_, **kwargs):
        return self._inv_transform(spec, phase, **kwargs)

    def compute_mel(
        self, wave: Tensor, base: float = 1e-6, add_base: bool = False
    ) -> Tensor:
        """Returns: [B, M, ML]"""
        wave_device = wave.device
        mel_tensor = self.mel_spec(wave.to(self.device))  # [M, ML]
        if not add_base:
            return (mel_tensor - self.mean) / self.std
        return ((torch.log(base + mel_tensor.unsqueeze(0)) - self.mean) / self.std).to(
            device=wave_device
        )

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

    def find_audios(self, path: PathLike, additional_extensions: List[str] = []):
        extensions = [
            "*.wav",
            "*.aac",
            "*.m4a",
            "*.mp3",
            "*.ogg",
            "*.opus",
            "*.flac",
        ]
        extensions.extend(
            [x for x in additional_extensions if isinstance(x, str) and "*" in x]
        )
        return FileScan.files(
            path,
            extensions,
        )

    def find_audio_text_pairs(
        self,
        path,
        additional_extensions: List[str] = [],
        text_file_patterns: List[str] = [".normalized.txt", ".original.txt"],
    ):
        is_array(text_file_patterns, True, validate=True)  # Rases if empty or not valid
        additional_extensions = [
            x
            for x in additional_extensions
            if isinstance(x, str)
            and "*" in x
            and not any(list(map(lambda y: y in x), text_file_patterns))
        ]
        audio_files = self.find_audios(path, additional_extensions)
        results = []
        for audio in audio_files:
            base_audio_dir = Path(audio).parent
            audio_name = get_file_name(audio, False)
            for pattern in text_file_patterns:
                possible_txt_file = Path(base_audio_dir, audio_name + pattern)
                if is_file(possible_txt_file):
                    results.append((audio, path_to_str(possible_txt_file)))
                    break
        return results

    def stft_loss(self, signal: Tensor, ground: Tensor, base: float = 1e-5):
        sig_mel = self(signal, base)
        gnd_mel = self(ground, base)
        return torch.norm(gnd_mel - sig_mel, p=1) / torch.norm(gnd_mel, p=1)

    # def forward(self, wave: Tensor, base: Optional[float] = None):
    def forward(
        self,
        *inputs: Union[Tensor, float],
        ap_task: Literal[
            "get_mel", "get_loss", "inv_transform", "revert_mel"
        ] = "get_mel",
        **inputs_kwargs,
    ):
        if ap_task == "get_mel":
            return self.compute_mel(*inputs, **inputs_kwargs)
        elif ap_task == "get_loss":
            return self.stft_loss(*inputs, **inputs_kwargs)
        elif ap_task == "inv_transform":
            return self.inverse_transform(*inputs, **inputs_kwargs)
        elif ap_task == "revert_mel":
            return self.reverse_mel(*inputs, **inputs_kwargs)
        else:
            raise ValueError(f"Invalid task '{ap_task}'")
