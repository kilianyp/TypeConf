from typeconf import read_file_cfg


def test_basic_config():
    cfg = read_file_cfg('tests/configs/basic.py')
    assert cfg['test1'] == 1
    assert cfg['test2'] == 2


def test_import_config():
    cfg = read_file_cfg('tests/configs/import.py')
    assert cfg['test1'] == 1
    assert cfg['test2'] == 3


def test_torch_config():
    import torch
    cfg = read_file_cfg('tests/configs/torch.py')
    assert cfg['nonlinearity'] == torch.relu
