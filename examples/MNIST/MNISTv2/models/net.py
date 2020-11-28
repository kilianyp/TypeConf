from torch import nn
import torch
import torch.nn.functional as F
from . import ModelConfig


@ModelConfig.register("net")
class NetConfig(ModelConfig):
    dropout_rate1 : float = 0.25
    dropout_rate2 : float = 0.5

    def _build(self):
        return Net(self.dropout_rate1, self.dropout_rate2)


class Net(nn.Module):
    def __init__(self, dropout_rate1=0.25, dropout_rate2=0.5):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, 1)
        self.conv2 = nn.Conv2d(32, 64, 3, 1)
        self.dropout1 = nn.Dropout(dropout_rate1)
        self.dropout2 = nn.Dropout(dropout_rate2)
        self.fc1 = nn.Linear(9216, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.conv1(x)
        x = F.relu(x)
        x = self.conv2(x)
        x = F.relu(x)
        x = F.max_pool2d(x, 2)
        x = self.dropout1(x)
        x = torch.flatten(x, 1)
        x = self.fc1(x)
        x = F.relu(x)
        x = self.dropout2(x)
        x = self.fc2(x)
        output = F.log_softmax(x, dim=1)
        return output


