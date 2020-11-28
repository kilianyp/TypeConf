from typeconf import SelectConfig
import pytest

class MasterConfig(SelectConfig):
    pass
MasterConfig._registered = SelectConfig._registered.copy()


@MasterConfig.register('slave1')
class Slave1Config(MasterConfig):
    def build(self):
        return


@MasterConfig.register('Slave2')
class Slave2Config(MasterConfig):
    def build(self):
        return


def test_caseinsensitive():
    slave1 = MasterConfig.build_config({'name': 'Slave1'})
    slave2 = MasterConfig.build_config({'name': 'slave2'})
    assert slave1 == Slave1Config
    assert slave2 == Slave2Config


def test_nooverwrite():
    with pytest.raises(ValueError):
        @MasterConfig.register('slave1')
        class SlaveConfig(MasterConfig):
            pass


class Master2Config(SelectConfig):
    pass
Master2Config._registered = SelectConfig._registered.copy()


def test_differentnamespace():
    @Master2Config.register('slave1')
    class SlaveConfig(Master2Config):
        pass
    slave = Master2Config.build_config({'name': 'slave1'})
    assert slave == SlaveConfig
