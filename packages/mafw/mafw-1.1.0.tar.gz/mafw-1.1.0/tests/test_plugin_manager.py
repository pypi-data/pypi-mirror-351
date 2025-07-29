import itertools
from types import SimpleNamespace

import pluggy
import pytest

from mafw import mafw_hookimpl
from mafw.decorators import single_loop
from mafw.plugin_manager import get_plugin_manager
from mafw.processor import Processor


def test_creation_of_pm():
    pm = get_plugin_manager()
    assert isinstance(pm, pluggy.PluginManager)

    pm1 = get_plugin_manager()
    pm2 = get_plugin_manager(force_recreate=True)
    assert id(pm) != id(pm2)
    assert id(pm) == id(pm1)


@pytest.fixture
def existing_hooks() -> set:
    return {'register_user_interfaces', 'register_processors', 'register_standard_tables'}


def test_presence_of_plugins(existing_hooks):
    pm = get_plugin_manager()
    assert len(pm.get_plugins()) >= 1

    hook_callers = [pm.get_hookcallers(p) for p in pm.get_plugins()]
    hook_callers = set([h.name for hc in hook_callers for h in hc])
    assert hook_callers == existing_hooks


def test_add_additional_processor():
    @single_loop
    class ClassContainerProcessor(Processor):
        pass

    class ClassContainer:
        @staticmethod
        @mafw_hookimpl
        def register_processors() -> list[type[Processor]]:
            return [ClassContainerProcessor]

    sn = SimpleNamespace()

    @single_loop
    class SNProcessor(Processor):
        pass

    @mafw_hookimpl
    def register_processors() -> list[type[Processor]]:
        return [SNProcessor]

    sn.register_processors = register_processors

    pm = get_plugin_manager()
    pm.register(ClassContainer)
    pm.register(sn)

    available_processors_list = list(itertools.chain(*pm.hook.register_processors()))
    available_processors: dict[str, type[Processor]] = {p.__name__: p for p in available_processors_list}

    extra_processors = ['SNProcessor', 'ClassContainerProcessor']
    for p in extra_processors:
        assert p in available_processors
