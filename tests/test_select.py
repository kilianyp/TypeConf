from typeconf import BaseConfig, SelectConfig
from typing import List, Optional, Tuple
from pydantic import ValidationError
import pytest


class MasterConfig(SelectConfig):
    pass


@MasterConfig.register('option1')
class Option1Config(MasterConfig):
    def build(self):
        return


@MasterConfig.register('Option2')
class Option2Config(MasterConfig):
    def build(self):
        return


def basic_test():
    slave1 = MasterConfig(**{'name': 'option1'})
    slave2 = MasterConfig(**{'name': 'Option2'})
    assert isinstance(slave1, Option1Config)
    assert isinstance(slave2, Option2Config)


def test_caseinsensitive():
    slave1 = MasterConfig.build_config({'name': 'Option1'})
    slave2 = MasterConfig.build_config({'name': 'option2'})
    assert slave1 == Option1Config
    assert slave2 == Option2Config


def test_list_select():
    class MultiModel(BaseConfig):
        models : List[MasterConfig]

    cfg = {
        "models": [
            {
                "name": "option1",
            },
            {
                "name": "option2",
            }
        ]
    }
    config = MultiModel(**cfg)
    assert isinstance(config.models[0], Option1Config)
    assert isinstance(config.models[1], Option2Config)
    cfg = {
        "models": [
            {
                "name": "option1",
            },
            {
                "name": "optionXYZ",
            }
        ]
    }
    with pytest.raises(ValueError):
        config = MultiModel(**cfg)


def test_optional_select():
    class OptionalModel(BaseConfig):
        model : Optional[MasterConfig]

    cfg = {
        "model": {
            "name": "option1",
        }
    }
    config = OptionalModel(**cfg)
    assert isinstance(config.model, Option1Config)
    config = OptionalModel(**{})


def test_tuple_select():
    class TupleModel(BaseConfig):
        models : Tuple[MasterConfig, MasterConfig]

    cfg = {
        "models": [
            {
                "name": "option1",
            },
            {
                "name": "option2",
            }
        ]
    }
    config = TupleModel(**cfg)
    assert isinstance(config.models[0], Option1Config)
    assert isinstance(config.models[1], Option2Config)
    cfg = {
        "models": [
            {
                "name": "option1",
            },
            {
                "name": "optionXYZ",
            }
        ]
    }
    with pytest.raises(ValueError):
        config = TupleModel(**cfg)


def test_missing_name():
    cfg = {"test": "dummy"}
    with pytest.raises(ValueError):
        MasterConfig(**cfg)


def test_unknown_option():
    cfg = {"name": "unknown"}
    with pytest.raises(ValueError):
        MasterConfig(**cfg)


def test_nooverwrite():
    with pytest.raises(ValueError):
        @MasterConfig.register('option1')
        class SlaveConfig(MasterConfig):
            pass


class DynamicConfig(BaseConfig):
    master : MasterConfig


def test_dynamic_config():
    cfg = DynamicConfig(**{"master": {"name": "option1"}})
    assert isinstance(cfg.master, Option1Config)


def test_dynamic_fail_config():
    with pytest.raises(ValueError):
        cfg = DynamicConfig()


class Master2Config(SelectConfig):
    def build(self):
        return


def test_differentnamespace():
    @Master2Config.register('option1')
    class OptionConfig(Master2Config):
        pass
    slave = Master2Config.build_config({'name': 'option1'})
    assert slave == OptionConfig


def test_wrongparent():
    """
    Throwing error as soon as possible
    """
    with pytest.raises(RuntimeError):
        class ParentConfig(SelectConfig):
            pass

        @ParentConfig.register('child')
        class ChildConfig(BaseConfig):
            def build(self):
                pass


    with pytest.raises(RuntimeError):
        class Parent1Config(SelectConfig):
            pass
        class Parent2Config(SelectConfig):
            pass

        @Parent1Config.register('child')
        class ChildConfig(Parent2Config):
            def build(self):
                pass

    with pytest.raises(RuntimeError):
        class Parent1Config(SelectConfig):
            pass
        class Parent2Config(Parent1Config):
            pass

        @Parent1Config.register('child')
        class ChildConfig(Parent2Config):
            def build(self):
                pass


@pytest.mark.xfail(reason='Not implemented')
def test_subclass():
    """
    TODO is this even relevant?
    """
    class Parent1Config(SelectConfig):
        pass
    class Parent2Config(Parent1Config):
        pass

    @Parent1Config.register('child')
    class ChildConfig(Parent1Config):
        def build(self):
            pass

    @Parent2Config.register('child')
    class ChildConfig(Parent2Config):
        def build(self):
            pass


def test_alias():
    class ParentConfig(SelectConfig):
        pass
    @ParentConfig.register('child1', 'child2')
    class ChildConfig(ParentConfig):
        def build(self):
            pass
    cls = ParentConfig.build_config({'name': 'child1'})
    assert cls == ChildConfig
    cls = ParentConfig.build_config({'name': 'child2'})
    assert cls == ChildConfig

