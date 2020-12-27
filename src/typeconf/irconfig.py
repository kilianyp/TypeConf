from omegaconf import OmegaConf
import os
from .utils import read_file_cfg


class IRConfig(OmegaConf):
    preset_paths = []

    @classmethod
    def register_preset_dir(cls, path):
        cls.preset_paths.append(path)

    @classmethod
    def load_preset(cls, path):
        for p in cls.preset_paths:
            filepath = os.path.join(p, path)
            if os.path.isfile(filepath):
                return read_file_cfg(filepath)
        raise ValueError(f"{path} not found in preset paths")

IRConfig.register_resolver("preset", IRConfig.load_preset)
