from . import OptimizerConfig

@OptimizerConfig.register("Adagrad")
class AdagradConfig(OptimizerConfig):
    lr : float = 1e-2
    lr_decay : float = 0
    weight_decay = 0
    eps : float = 1e-10
    initial_accumulator_value : float = 0.0

    def build(self, params):
        from torch.optim import Adagrad
        return Adagrad(
            params,
            lr=self.lr,
            lr_decay=self.lr_decay,
            weight_decay=self.weight_decay,
            initial_accumulator_value=self.initial_accumulator_value,
            eps=self.eps
        )
