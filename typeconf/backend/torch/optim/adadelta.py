from pydantic import BaseModel


class SelectModel(BaseModel):
    name : str


class AdadeltaConfigModel(SelectModel):
    lr : float = 1.0
    rho : float = 1.0
    eps : float = 1e-06
    weight_decay = 0


class AdadeltaBuilder(BaseBuilder):
    def build_config(cfg):
        return AdadeltaConfigModel

    def build_object(cfg : AdadeltaConfigModel, params):
        from torch.optim import Adadelta
        return Adadelta(
            params,
            lr=cfg.lr,
            rho=cfg.rho,
            eps=cfg.eps,
            weight_decay=cfg.weight_decay
        )
