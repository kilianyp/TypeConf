"""
Used https://github.com/pytorch/examples/blob/0f0c9131ca5c79d1332dce1f4c06fe942fbdc665/mnist/main.py as a startpoint.
"""
from __future__ import print_function
import torch
import torch.nn.functional as F
from torchvision import datasets, transforms
from typeconf import BaseConfig
from models import ModelConfig
from typeconf.libs.torch.optim import OptimizerConfig
from typeconf.libs.torch.optim.lr_scheduler import LRSchedulerConfig


class MNISTOptimizerConfig(OptimizerConfig):
    name = "Adadelta"
    lr : float = 1.0


class MNISTLRSchedulerConfig(LRSchedulerConfig):
    name = "step_lr"
    gamma = 0.7


class MNISTModelConfig(ModelConfig):
    name = "net"


class MNISTConfig(BaseConfig):
    batch_size: int = 64
    test_batch_size: int = 1000
    epochs: int = 14
    no_cuda: bool = False
    dry_run: bool = False
    seed: int = 1
    log_interval: int = 10
    save_model: bool = True
    gamma: float = 0.7
    model: MNISTModelConfig
    optimizer: MNISTOptimizerConfig
    lr_scheduler: MNISTLRSchedulerConfig


def train(args, model, device, train_loader, optimizer, epoch):
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = F.nll_loss(output, target)
        loss.backward()
        optimizer.step()
        if batch_idx % args.log_interval == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                100. * batch_idx / len(train_loader), loss.item()))
            if args.dry_run:
                break


def test(model, device, test_loader):
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += F.nll_loss(output, target, reduction='sum').item()  # sum up batch loss
            pred = output.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(test_loader.dataset)

    print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
        test_loss, correct, len(test_loader.dataset),
        100. * correct / len(test_loader.dataset)))


def main():
    kwargs = MNISTConfig.parse_cli_args()
    cfg = MNISTConfig(**kwargs)
    print(cfg)

    use_cuda = not cfg.no_cuda and torch.cuda.is_available()
    torch.manual_seed(cfg.seed)

    device = torch.device("cuda" if use_cuda else "cpu")

    train_kwargs = {'batch_size': cfg.batch_size}
    test_kwargs = {'batch_size': cfg.test_batch_size}
    if use_cuda:
        cuda_kwargs = {'num_workers': 1,
                       'pin_memory': True,
                       'shuffle': True}
        train_kwargs.update(cuda_kwargs)
        test_kwargs.update(cuda_kwargs)

    transform=transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
        ])
    dataset1 = datasets.MNIST('..', train=True, download=True,
                              transform=transform)
    dataset2 = datasets.MNIST('..', train=False,
                              transform=transform)
    train_loader = torch.utils.data.DataLoader(dataset1, **train_kwargs)
    test_loader = torch.utils.data.DataLoader(dataset2, **test_kwargs)

    model = cfg.model.build()
    model = model.to(device)
    optimizer = cfg.optimizer.build(model.parameters())

    scheduler = cfg.lr_scheduler.build(optimizer, step_size=1)
    for epoch in range(1, cfg.epochs + 1):
        train(cfg, model, device, train_loader, optimizer, epoch)
        test(model, device, test_loader)
        scheduler.step()

    if cfg.save_model:
        torch.save(model.state_dict(), "mnist_cnn.pt")
    print(cfg.get_stats())


if __name__ == '__main__':
    main()
