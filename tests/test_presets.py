from typeconf import BaseConfig, SelectConfig



class ModelConfig(SelectConfig):
    pass


@ModelConfig.register("unet")
class UnetConfig(ModelConfig):
    weights = "http://torch.com"
    def build(self):
        pass



class Config(BaseConfig):
    model : ModelConfig


def test_preset():
    cfg = Config(model={'preset': 'unet_pretrained'})

