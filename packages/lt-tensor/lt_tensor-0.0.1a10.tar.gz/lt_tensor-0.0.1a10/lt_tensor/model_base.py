__all__ = ["Model"]


import warnings
from .torch_commons import *
from lt_utils.common import *
from lt_utils.misc_utils import log_traceback

T = TypeVar("T")

ROOT_DEVICE = torch.zeros(1).device

POSSIBLE_OUTPUT_TYPES: TypeAlias = Union[
    Tensor,
    Sequence[Tensor],
    Dict[Union[str, Tensor, Any], Union[Sequence[Tensor], Tensor, Any]],
]


class Model(nn.Module, ABC):
    """
    This makes it easier to assign a device and retrieves it later
    """

    _device: torch.device = ROOT_DEVICE
    _autocast: bool = False

    @property
    def autocast(self):
        return self._autocast

    @autocast.setter
    def autocast(self, value: bool):
        self._autocast = value

    @property
    def device(self):
        return self._device

    @device.setter
    def device(self, device: Union[torch.device, str]):
        assert isinstance(device, (str, torch.device))
        self._device = torch.device(device) if isinstance(device, str) else device
        self._apply_device_to()

    def _apply_device_to(self):
        """Add here components that are needed to have device applied to them,
        that usually the '.to()' function fails to apply

        example:
        ```
        def _apply_device_to(self):
            self.my_tensor = self.my_tensor.to(device=self.device)
        ```
        """
        pass

    def freeze_weight(self, weight: Union[str, nn.Module], freeze: bool):
        assert isinstance(weight, (str, nn.Module))
        if isinstance(weight, str):
            if hasattr(self, weight):
                w = getattr(self, weight)
                if isinstance(w, nn.Module):
                    w.requires_grad_(not freeze)
        else:
            weight.requires_grad_(not freeze)

    def _freeze_unfreeze(
        self,
        weight: Union[str, nn.Module],
        task: Literal["freeze", "unfreeze"] = "freeze",
        _skip_except: bool = False,
    ):
        try:
            assert isinstance(weight, (str, nn.Module))
            if isinstance(weight, str):
                w_txt = f"Failed to {task} the module '{weight}'. Reason: is not a valid attribute of {self._get_name()}"
                if hasattr(self, weight):
                    w_txt = f"Failed to {task} the module '{weight}'. Reason: is not a Module type."
                    w = getattr(self, weight)
                    if isinstance(w, nn.Module):
                        w_txt = f"Successfully {task} the module '{weight}'."
                        w.requires_grad_(task == "unfreeze")

            else:
                w.requires_grad_(task == "unfreeze")
                w_txt = f"Successfully '{task}' the module '{weight}'."
            return w_txt
        except Exception as e:
            if not _skip_except:
                raise e
            return str(e)

    def freeze_weight(
        self,
        weight: Union[str, nn.Module],
        _skip_except: bool = False,
    ):
        return self._freeze_unfreeze(weight, "freeze", _skip_except)

    def unfreeze_weight(
        self,
        weight: Union[str, nn.Module],
        _skip_except: bool = False,
    ):
        return self._freeze_unfreeze(weight, "freeze", _skip_except)

    def freeze_all(self, exclude: Optional[List[str]] = None):
        no_exclusions = not exclude
        frozen = []
        not_frozen = []
        for name, param in self.named_parameters():
            if no_exclusions:
                try:
                    param.requires_grad_(False)
                    frozen.append(name)
                except Exception as e:
                    not_frozen.append((name, str(e)))
            elif any(layer in name for layer in exclude):
                try:
                    param.requires_grad_(False)
                    frozen.append(name)
                except Exception as e:
                    not_frozen.append((name, str(e)))
            else:
                not_frozen.append((name, "Excluded"))
        return dict(frozen=frozen, not_frozen=not_frozen)

    def unfreeze_all_except(self, exclude: Optional[list[str]] = None):
        """Unfreezes all model parameters except specified layers."""
        no_exclusions = not exclude
        unfrozen = []
        not_unfrozen = []
        for name, param in self.named_parameters():
            if no_exclusions:
                try:
                    param.requires_grad_(True)
                    unfrozen.append(name)
                except Exception as e:
                    not_unfrozen.append((name, str(e)))
            elif any(layer in name for layer in exclude):
                try:
                    param.requires_grad_(True)
                    unfrozen.append(name)
                except Exception as e:
                    not_unfrozen.append((name, str(e)))
            else:
                not_unfrozen.append((name, "Excluded"))
        return dict(unfrozen=unfrozen, not_unfrozen=not_unfrozen)

    def to(self, *args, **kwargs):
        device, dtype, non_blocking, convert_to_format = torch._C._nn._parse_to(
            *args, **kwargs
        )

        if dtype is not None:
            if not (dtype.is_floating_point or dtype.is_complex):
                raise TypeError(
                    "nn.Module.to only accepts floating point or complex "
                    f"dtypes, but got desired dtype={dtype}"
                )
            if dtype.is_complex:
                warnings.warn(
                    "Complex modules are a new feature under active development whose design may change, "
                    "and some modules might not work as expected when using complex tensors as parameters or buffers. "
                    "Please file an issue at https://github.com/pytorch/pytorch/issues/new?template=bug-report.yml "
                    "if a complex module does not work as expected."
                )

        def convert(t: Tensor):
            try:
                if convert_to_format is not None and t.dim() in (4, 5):
                    return t.to(
                        device,
                        dtype if t.is_floating_point() or t.is_complex() else None,
                        non_blocking,
                        memory_format=convert_to_format,
                    )
                return t.to(
                    device,
                    dtype if t.is_floating_point() or t.is_complex() else None,
                    non_blocking,
                )
            except NotImplementedError as e:
                if str(e) == "Cannot copy out of meta tensor; no data!":
                    raise NotImplementedError(
                        f"{e} Please use torch.nn.Module.to_empty() instead of torch.nn.Module.to() "
                        f"when moving module from meta to a different device."
                    ) from None
                else:
                    raise

        self._apply(convert)
        self.device = device
        return self

    def ipu(self, device: Optional[Union[int, torch.device]] = None) -> T:
        super().ipu(device)
        dvc = "ipu"
        if device is not None:
            dvc += (
                ":" + str(device) if isinstance(device, (int, float)) else device.index
            )
        self.device = dvc
        return self

    def xpu(self, device: Optional[Union[int, torch.device]] = None) -> T:
        super().xpu(device)
        dvc = "xpu"
        if device is not None:
            dvc += (
                ":" + str(device) if isinstance(device, (int, float)) else device.index
            )
        self.device = dvc
        return self

    def cuda(self, device: Optional[Union[int, torch.device]] = None) -> T:
        super().cuda(device)
        dvc = "cuda"
        if device is not None:
            dvc += (
                ":" + str(device) if isinstance(device, (int, float)) else device.index
            )
        self.device = dvc
        return self

    def mtia(self, device: Optional[Union[int, torch.device]] = None) -> T:
        super().mtia(device)
        dvc = "mtia"
        if device is not None:
            dvc += (
                ":" + str(device) if isinstance(device, (int, float)) else device.index
            )
        self.device = dvc
        return self

    def cpu(self) -> T:
        super().cpu()
        self.device = "cpu"
        return self

    def count_trainable_parameters(self, module_name: Optional[str] = None):
        """Gets the number of trainable parameters from either the entire model or from a specific module."""
        if module_name is not None:
            assert hasattr(self, module_name), f"Module {module_name} does not exits"
            module = getattr(self, module_name)
            return sum(
                [
                    x.numel()
                    for x in module.parameters()
                    if hasattr(x, "requires_grad") and x.requires_grad
                ]
            )
        return sum(
            [
                x.numel()
                for x in self.parameters()
                if hasattr(x, "requires_grad") and x.requires_grad
            ]
        )

    def count_non_trainable_parameters(self, module_name: Optional[str] = None):
        """Gets the number of non-trainable parameters from either the entire model or from a specific module."""
        if module_name is not None:
            assert hasattr(self, module_name), f"Module {module_name} does not exits"
            module = getattr(self, module_name)
            return sum(
                [
                    x.numel()
                    for x in module.parameters()
                    if not hasattr(x, "requires_grad") or not x.requires_grad
                ]
            )
        return sum(
            [
                x.numel()
                for x in self.parameters()
                if not hasattr(x, "requires_grad") or not x.requires_grad
            ]
        )

    def get_weights(self, module_name: Optional[str] = None) -> List[Tensor]:
        """Returns the weights of the model entry model or from a specified module"""
        if module_name is not None:
            assert hasattr(self, module_name), f"Module {module_name} does not exits"
            module = getattr(self, module_name)
            params = []
            if isinstance(module, nn.Module):
                return [x.data.detach() for x in module.parameters()]
            elif isinstance(module, (Tensor, nn.Parameter)):
                return [module.data.detach()]
            raise (f"{module_name} is has no weights")
        return [x.data.detach() for x in self.parameters()]

    def print_trainable_parameters(
        self, module_name: Optional[str] = None
    ) -> List[Tensor]:
        params = format(self.count_trainable_parameters(module_name), ",").replace(
            ",", "."
        )
        if module_name:
            print(f'Trainable Parameters from "{module_name}": {params}')
        else:
            print(f"Trainable Parameters: {params}")

    def print_non_trainable_parameters(
        self, module_name: Optional[str] = None
    ) -> List[Tensor]:
        params = format(self.count_non_trainable_parameters(module_name), ",").replace(
            ",", "."
        )
        if module_name:
            print(f'Non-Trainable Parameters from "{module_name}": {params}')
        else:
            print(f"Non-Trainable Parameters: {params}")

    def save_weights(self, path: Union[Path, str]):
        path = Path(path)
        if path.exists():
            assert (
                path.is_file()
            ), "The provided path exists but its a directory not a file!"
            path.rmdir()
        path.parent.mkdir(exist_ok=True, parents=True)
        torch.save(obj=self.state_dict(), f=str(path))

    def load_weights(
        self,
        path: Union[Path, str],
        raise_if_not_exists: bool = False,
        strict: bool = True,
        assign: bool = False,
        weights_only: bool = False,
        mmap: Optional[bool] = None,
        **torch_loader_kwargs,
    ):
        path = Path(path)
        if not path.exists():
            assert not raise_if_not_exists, "Path does not exists!"
            return None
        assert path.is_file(), "The provided path is not a valid file!"
        state_dict = torch.load(
            str(path), weights_only=weights_only, mmap=mmap, **torch_loader_kwargs
        )
        incompatible_keys = self.load_state_dict(
            state_dict,
            strict=strict,
            assign=assign,
        )
        return incompatible_keys

    @torch.no_grad()
    def inference(self, *args, **kwargs):
        if self.training:
            self.eval()
        if self.autocast:
            with torch.autocast(device_type=self.device.type):
                return self(*args, **kwargs)
        return self(*args, **kwargs)

    def train_step(
        self,
        *args,
        **kwargs,
    ):
        """Train Step"""
        if not self.training:
            self.train()
        return self(*args, **kwargs)

    @torch.autocast(device_type=_device.type)
    def ac_forward(self, *args, **kwargs):
        return

    def __call__(self, *args, **kwds) -> POSSIBLE_OUTPUT_TYPES:
        return super().__call__(*args, **kwds)

    @abstractmethod
    def forward(
        self, *args, **kwargs
    ) -> Union[Tensor, Sequence[Tensor], Dict[Any, Union[Any, Tensor]]]:
        pass
