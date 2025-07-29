import sys
from typing import Any, Collection

import pytest
from playhouse.db_url import connect

from mafw.decorators import (
    database_required,
    depends_on_optional,
    execution_workflow,
    for_loop,
    orphan_protector,
    processor_depends_on_optional,
    single_loop,
    singleton,
    while_loop,
)
from mafw.enumerators import LoopType
from mafw.mafw_errors import MissingDatabase, MissingOptionalDependency, ProcessorParameterError
from mafw.processor import ActiveParameter, Processor, ensure_parameter_registration


@singleton
class ASingletonClass:
    def __init__(self):
        self.num = 10


def test_singleton():
    first = ASingletonClass()
    second = ASingletonClass()
    assert id(first) == id(second)


def test_database_required(capsys):
    class NormalProcessor(Processor):
        def process(self):
            print('ok')

    p = NormalProcessor(looper=LoopType.SingleLoop)
    p.execute()
    captured = capsys.readouterr()
    assert captured.out == 'ok\n'

    @database_required
    class DBProcessor(Processor):
        def process(self):
            print('db ok')

    p = DBProcessor(looper=LoopType.SingleLoop)
    with pytest.raises(MissingDatabase) as e:
        p.execute()
    assert f'{p.name} requires an active database.' in str(e.value)

    database = connect('sqlite:///:memory:')
    p2 = DBProcessor(looper=LoopType.SingleLoop, database=database)
    p2.execute()
    captured = capsys.readouterr()
    assert 'db ok\n' in captured.out


def test_orphan_protector():
    class RemovalProcessor(Processor):
        pass

    removal = RemovalProcessor(looper=LoopType.SingleLoop)
    assert removal.remove_orphan_files

    @orphan_protector
    class Protector(Processor):
        pass

    protector = Protector(looper=LoopType.SingleLoop)
    assert not protector.remove_orphan_files


def test_ensure_parameter_registration():
    @single_loop
    class MyProcessor(Processor):
        @ensure_parameter_registration
        def a_method(self):
            pass

    @ensure_parameter_registration
    def func():
        pass

    @ensure_parameter_registration
    def another(a, b):
        pass

    my_proc = MyProcessor()
    my_proc.a_method()

    with pytest.raises(ProcessorParameterError):
        func()

    with pytest.raises(ProcessorParameterError):
        another(3, 4)


def test_database_required_wrapping():
    class NotDecoProcessor(Processor):
        """This is a not decorated processor"""

        def __init__(self, *args: Any, **kwargs: Any):
            super().__init__(*args, looper=LoopType.SingleLoop, **kwargs)

        def start(self) -> None:
            """This method is not decorated"""
            pass

    assert NotDecoProcessor.__doc__ == 'This is a not decorated processor'
    assert NotDecoProcessor.start.__doc__ == 'This method is not decorated'

    @database_required
    class DBReqProcessor(Processor):
        """This is a DB requiring processor"""

        def start(self) -> None:
            """This is the method that is actually decorated"""
            pass

    assert DBReqProcessor.__doc__ == 'This is a DB requiring processor'
    assert DBReqProcessor.start.__doc__ == 'This is the method that is actually decorated'


def test_workflow_decorators():
    @single_loop
    class SingleProcessor1(Processor):
        pass

    sp1 = SingleProcessor1()
    assert sp1.loop_type == LoopType.SingleLoop

    @execution_workflow(loop_type='single')
    class SingleProcessor2(Processor):
        pass

    sp2 = SingleProcessor2()
    assert sp2.loop_type == LoopType.SingleLoop

    @execution_workflow(loop_type=LoopType.SingleLoop)
    class SingleProcessor3(Processor):
        pass

    sp3 = SingleProcessor3()
    assert sp3.loop_type == LoopType.SingleLoop

    @for_loop
    class ForLoopProcessor1(Processor):
        def get_items(self) -> Collection[Any]:
            return [1]

    flp1 = ForLoopProcessor1()
    assert flp1.loop_type == LoopType.ForLoop

    @execution_workflow(loop_type=LoopType.ForLoop)
    class ForLoopProcessor2(Processor):
        def get_items(self) -> Collection[Any]:
            return [1]

    flp2 = ForLoopProcessor2()
    assert flp2.loop_type == LoopType.ForLoop

    @execution_workflow(loop_type='for_loop')
    class ForLoopProcessor3(Processor):
        def get_items(self) -> Collection[Any]:
            return [1]

    flp3 = ForLoopProcessor3()
    assert flp3.loop_type == LoopType.ForLoop

    @execution_workflow()
    class ForLoopProcessor4(Processor):
        def get_items(self) -> Collection[Any]:
            return [1]

    flp4 = ForLoopProcessor4()
    assert flp4.loop_type == LoopType.ForLoop

    @while_loop
    class WhileLoopProcessor1(Processor):
        def while_condition(self) -> bool:
            return False

    wlp1 = WhileLoopProcessor1()
    assert wlp1.loop_type == LoopType.WhileLoop

    @execution_workflow(loop_type='while_loop')
    class WhileLoopProcessor2(Processor):
        def __init__(self, *args: Any, **kwargs: Any):
            super().__init__(*args, description='a description', **kwargs)

        def while_condition(self) -> bool:
            return False

    wlp2 = WhileLoopProcessor2('wlp2')
    assert wlp2.loop_type == LoopType.WhileLoop
    assert wlp2.description == 'a description'
    assert wlp2.name == 'wlp2'

    @execution_workflow(loop_type=LoopType.WhileLoop)
    class WhileLoopProcessor3(Processor):
        def while_condition(self) -> bool:
            return False

    wlp3 = WhileLoopProcessor3('wlp3', description='test processor')
    assert wlp3.loop_type == LoopType.WhileLoop
    assert wlp3.description == 'test processor'
    assert wlp3.name == 'wlp3'
    assert wlp3.remove_orphan_files is True

    @orphan_protector
    @single_loop
    class SingleProcessor4(Processor):
        pass

    sp4 = SingleProcessor4('sp4', description='doubly decorated')
    assert sp4.loop_type == LoopType.SingleLoop
    assert sp4.remove_orphan_files is False
    assert sp4.name == 'sp4'
    assert sp4.description == 'doubly decorated'


def test_function_depends_on_optional():
    missing_lib = 'missing_lib'
    available_lib = 'sys'

    @depends_on_optional(module_name=available_lib)
    def get_python_version():
        return sys.version_info

    get_python_version()

    # missing lib but all other defaults, raise = False, warn = True
    @depends_on_optional(module_name=missing_lib)
    def failing_python_version_all_defaults():
        return sys.version_info

    with pytest.warns(MissingOptionalDependency, match=missing_lib):
        assert failing_python_version_all_defaults() is None

    # missing lib, raise = True, warn = True
    @depends_on_optional(module_name=missing_lib, raise_ex=True)
    def failing_python_version_raise():
        return sys.version_info

    with pytest.raises(ImportError, match=missing_lib):
        assert failing_python_version_raise() is None

    # missing lib, silent, raise = False, warn = False
    @depends_on_optional(module_name=missing_lib, warn=False)
    def silent_failing():
        return sys.version_info

    assert silent_failing() is None


def test_processor_depends_on_optional(capsys):
    available_libs = 'os;sys'

    @processor_depends_on_optional(available_libs)
    @single_loop
    class GoodProcessor(Processor):
        p1 = ActiveParameter('p1', default=0)

        def process(self) -> None:
            print('GoodProcessor is good')
            print(f'p1 = {self.p1}')

    gp = GoodProcessor()
    gp.execute()
    captured = capsys.readouterr().out
    assert 'GoodProcessor is good\n' in captured
    assert 'p1 = 0' in captured

    gp = GoodProcessor(p1=12)
    gp.execute()
    captured = capsys.readouterr().out
    assert 'GoodProcessor is good\n' in captured
    assert 'p1 = 12\n' in captured
    assert 'p1 = 0\n' not in captured

    missing_libs = 'lib1;lib2'

    with pytest.warns(MissingOptionalDependency, match=missing_libs):
        # raise false, warn true
        @processor_depends_on_optional(missing_libs)
        @single_loop
        class MissingProcessorWarn(Processor):
            p1 = ActiveParameter('p1', default=0)

            def process(self) -> None:
                print('MissingProcessorWarn is missing')
                print(f'p1 = {self.p1}')

    with pytest.raises(ImportError, match=missing_libs):

        @processor_depends_on_optional(missing_libs, raise_ex=True)
        @single_loop
        class MissingProcessorRaise(Processor):
            p1 = ActiveParameter('p1', default=0)

            def process(self) -> None:
                print('MissingProcessorRaise is missing')
                print(f'p1 = {self.p1}')

    @processor_depends_on_optional(missing_libs, raise_ex=False, warn=False)
    @single_loop
    class MissingProcessorSilent(Processor):
        p1 = ActiveParameter('p1', default=0)

        def process(self) -> None:
            print('MissingProcessorSilent is missing')
            print(f'p1 = {self.p1}')

    mps = MissingProcessorSilent(p1=12)
    mps.execute()
    captured = capsys.readouterr().out
    assert captured == ''

    @processor_depends_on_optional(missing_libs, raise_ex=False, warn=False)
    @for_loop
    class MissingForLoopProcessorSilent(Processor):
        p1 = ActiveParameter('p1', default=0)

        def process(self) -> None:
            print('MissingProcessorSilent is missing')
            print(f'p1 = {self.p1}')

    mps = MissingForLoopProcessorSilent(p1=12)
    assert mps.loop_type == LoopType.SingleLoop
