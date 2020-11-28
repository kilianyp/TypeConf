from . import OptimizerConfig

@OptimizerConfig.register("Adadelta")
class AdadeltaConfig(OptimizerConfig):
    lr : float = 1.0
    rho : float = 1.0
    eps : float = 1e-06
    weight_decay = 0

    def build(self, params):
        from torch.optim import Adadelta
        return Adadelta(
            params,
            lr=self.lr,
            rho=self.rho,
            eps=self.eps,
            weight_decay=self.weight_decay
        )
