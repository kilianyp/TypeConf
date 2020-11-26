from typeconf.libs.torchvision.datasets.MNIST import MNISTConfig


def afn(*args, **kwargs):
    return args

cfg = {
    'name': "MNIST",
    'root': './mnist/',
    'target_transform': afn
}

cfg = MNISTConfig(**cfg)
def bfn():
    pass
cfg.target_transform = bfn
try:
    mnist = cfg.build()
except:
    cfg.download = True
    mnist = cfg.build()
print(mnist)
