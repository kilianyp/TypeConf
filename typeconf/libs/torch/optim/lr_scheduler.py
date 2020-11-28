from typeconf import SelectConfig


class LRSchedulerConfig(SelectConfig):
    pass


@LRSchedulerConfig.register("step_lr")
class StepLRConfig(SelectConfig):
    gamma : float = 0.1
    last_epoch : int = -1
    verbose : bool = False

    def build(self, optimizer, step_size):
        from torch.optim.lr_scheduler import StepLR
        return StepLR(
            optimizer,
            step_size,
            gamma=self.gamma,
            last_epoch=self.last_epoch,
            verbose=self.verbose
        )

    @classmethod
    def build_config(cls, cfg):
        return cls
