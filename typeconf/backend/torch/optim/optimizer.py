from pydantic import BaseModel




class OptimizerBuilder(SelectBuilder):
    def build_config(self, cfg):
        name = cfg['name']
        if name == "adadelta":
            from . import adadelta
            config = adadelta.build_config(cfg)
            self.build_object = adadelta.build_object
        return config

