from omegaconf import OmegaConf
import os
from .utils import read_file_cfg


class IRConfig(OmegaConf):
    preset_paths = []
    systems_config = {}

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

    @classmethod
    def register_system_var_from_file(cls, filepath):
        """
        Overwrites any existing

        Or should it update?
        """
        if os.path.isfile(filepath):
            system_config = read_file_cfg(filepath)
            cls.systems_config.update(system_config)
            return
        raise FileNotFoundError(f"System path not found {filepath}")

    @classmethod
    def get_system_var(cls, name):
        if name not in cls.systems_config:
            raise RuntimeError(f"Unknown system variable {name} {cls.systems_config}. Make sure to register")
        return cls.systems_config[name]

    @classmethod
    def register_system_var(cls, key, value):
        cls.systems_config[key] = value


IRConfig.register_resolver("preset", IRConfig.load_preset)
IRConfig.register_resolver("system", IRConfig.get_system_var)
