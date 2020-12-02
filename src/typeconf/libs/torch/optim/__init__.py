from typeconf import SelectConfig


class OptimizerConfig(SelectConfig):
    pass

from .adadelta import AdadeltaConfig
from .adagrad import AdagradConfig
