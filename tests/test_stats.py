from typeconf import BaseConfig


class Config(BaseConfig):
    test : int = 2


def test_simple():
    cfg = Config()
    cfg.test
    stats = cfg.get_stats()
    assert stats['test'] == 1


class Config2(BaseConfig):
    nested : Config = Config()


def test_nested():
    cfg = Config2()
    cfg.nested.test
    stats = cfg.get_stats()
    assert stats['nested'] == 1
    assert stats['nested.test'] == 1
    sub_cfg = cfg.nested
    sub_cfg.test
    stats = cfg.get_stats()
    assert stats['nested'] == 2
    assert stats['nested.test'] == 2


class Config3(BaseConfig):
    nested : Config2 = Config2()


def test_nested2():
    cfg = Config3()
    cfg.nested.nested.test
    stats = cfg.get_stats()
    assert stats['nested.nested.test'] == 1


class Config4(BaseConfig):
    test1 : int = 1
    test2 : int = 2


def test_ununsed():
    cfg = Config4()
    unused = cfg.find_unused()
    assert unused == {'test1', 'test2'}
    cfg.test1
    unused = cfg.find_unused()
    assert unused == {'test2'}


def test_access():
    cfg = Config2()
    assert cfg.nested.test == 2
    assert cfg['nested']['test'] == 2

