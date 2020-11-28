from typeconf import SelectConfig

class MasterConfig(SelectConfig):
    pass


@MasterConfig.register('slave1')
class Slave1Config(SelectConfig):
    def build(self):
        return

@MasterConfig.register('Slave2')
class Slave2Config(SelectConfig):
    def build(self):
        return

def test_caseinsensitive():
    slave1 = MasterConfig.parse(**{'name': 'Slave1'})
    slave2 = MasterConfig.parse(**{'name': 'slave2'})
        

