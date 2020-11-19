def load_cfg():
    path = 'config.py'
    if path.endswith('.py'):
        exec(open(path).read())
        return locals()['cfg']


# cfg = load_cfg()
cfg = {
    "model": {
        "name": "dummy",
        "test": 1,
        "num_classes": 1,
        "weights": "/data1/pfeiffky/gog/experiments/GoG/pretrain_202007101435/training_checkpoint_36760.pt",
    },
    "training": {
        "optimizer": {
            "name": "adagrad"
        },
        "max_epochs": 30,
    },
}
print('\n\n')
from typeconf.experiment import ExperimentBuilder
experiment_cfg = ExperimentBuilder().parse(cfg)
print(experiment_cfg.training)
model_cfg = experiment_cfg.model 
model = model_cfg.build()
