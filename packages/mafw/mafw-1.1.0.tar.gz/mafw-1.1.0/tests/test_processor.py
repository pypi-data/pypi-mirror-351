import random
import time
from typing import Any, Collection

import pytest

from mafw.db.db_configurations import default_conf
from mafw.decorators import database_required, single_loop, while_loop
from mafw.enumerators import LoopingStatus, LoopType, ProcessorExitStatus, ProcessorStatus
from mafw.examples.loop_modifier import FindNPrimeNumber, FindPrimeNumberInRange
from mafw.examples.sum_processor import AccumulatorProcessor, GaussAdder
from mafw.mafw_errors import (
    AbortProcessorException,
    MissingDatabase,
    MissingOverloadedMethod,
    MissingSuperCall,
    ProcessorParameterError,
)
from mafw.processor import ActiveParameter, PassiveParameter, Processor, ProcessorList, validate_database_conf


@single_loop
class MyDummyProcessor(Processor):
    active_param: ActiveParameter[int] = ActiveParameter('active_param', default=15, help_doc='An active parameter')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # one compulsory parameter
        self._comp_param: PassiveParameter[int] = PassiveParameter('comp_param', value=5)

        # one optional parameter
        self._opt_param: PassiveParameter[str] = PassiveParameter('opt_param', default='optional')


def test_creation_of_process_parameters():
    with pytest.raises(ProcessorParameterError) as e:
        PassiveParameter('new_param')

    assert 'Processor parameter cannot have both value and default value set to None' == str(e.value)

    for wrong_name in ['12', '1dsfoo-bar', 'bar for']:
        with pytest.raises(ProcessorParameterError) as e:
            PassiveParameter(wrong_name)
        assert 'not a valid python identifier' in str(e)


def test_processor_with_parameters():
    tp = MyDummyProcessor()
    comp_param = tp.get_parameter('comp_param')
    assert comp_param.name == 'comp_param'
    assert comp_param.value == 5
    assert not comp_param.is_optional
    assert comp_param.is_set

    opt_param = tp.get_parameter('opt_param')
    assert opt_param.name == 'opt_param'
    assert opt_param.value == 'optional'
    assert opt_param.is_optional
    assert not opt_param.is_set
    opt_param.value = 'now is set'
    assert opt_param.is_set

    tp.set_parameter_value('opt_param', 'from_proc')
    assert opt_param.value == 'from_proc'
    tp.get_parameter('opt_param').value = 'direct_assignment'
    assert opt_param.value == 'direct_assignment'

    tp.delete_parameter('opt_param')
    with pytest.raises(ProcessorParameterError) as e:
        tp.get_parameter('opt_param')
    assert 'No parameter (opt_param)' in str(e.value)

    assert tp.active_param == tp.get_parameter('active_param').value
    tp.active_param += 1
    assert tp.active_param == tp.get_parameter('active_param').value
    tp.set_parameter_value('active_param', -15)
    assert tp.active_param == tp.get_parameter('active_param').value

    with pytest.raises(ProcessorParameterError) as e:
        tp.get_parameter('missing')
    assert 'No parameter (missing)' in str(e.value)

    class AnotherProcess(Processor):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.p1 = PassiveParameter('same_name', default='value')
            self.p2 = PassiveParameter('same_name', default='another_value')

    with pytest.raises(ProcessorParameterError) as e:
        AnotherProcess(looper='single')
    assert 'Duplicated' in str(e.value)

    class ActiveProcessor(Processor):
        param1 = ActiveParameter('param', default=0)
        param2 = ActiveParameter('param', 2)

    with pytest.raises(ProcessorParameterError) as e:
        ActiveProcessor(looper='single')
    assert 'Duplicated' in str(e.value)

    @single_loop
    class ConfigProcessor(Processor):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.p1 = PassiveParameter('param1', default='value')
            self.p2 = PassiveParameter('param2', default='another_value')

    cp = ConfigProcessor(param1='1st*', param2='2nd*')
    assert cp.get_parameter('param1').value == '1st*'
    assert cp.get_parameter('param2').value == '2nd*'

    config = {'ConfigProcessor': {'param1': '1st', 'param2': '2nd'}}
    cp = ConfigProcessor(config=config, param2='2nd*')
    assert cp.get_parameter('param1').value == '1st'  # this should remain unchanged.
    assert cp.get_parameter('param2').value == '2nd*'

    config = {'WrongNameProcessor': {'param1': '1st', 'param2': '2nd'}}
    cp = ConfigProcessor(config=config)
    assert cp.get_parameter('param1').value == 'value'
    assert cp.get_parameter('param2').value == 'another_value'


def test_processor_status():
    class MyProcessor(Processor):
        def on_processor_status_change(self, old_status: ProcessorStatus, new_status: ProcessorStatus):
            if new_status == ProcessorStatus.Init:
                assert self.processor_status == ProcessorStatus.Init

    my_p = MyProcessor(looper='single')
    assert my_p.processor_status == ProcessorStatus.Init
    my_p.start()
    assert my_p.processor_status == ProcessorStatus.Start
    my_p.finish()
    assert my_p.processor_status == ProcessorStatus.Finish


def test_processor_looper():
    import random

    from mafw.examples.sum_processor import AccumulatorProcessor

    last_value = random.randint(1, 1000)

    ap = AccumulatorProcessor(last_value=last_value)
    ap.execute()
    assert ap.accumulated_value == last_value * (last_value - 1) / 2


def test_processor_no_loop():
    import random

    from mafw.examples.sum_processor import GaussAdder

    last_value = random.randint(1, 1000)

    gs = GaussAdder(last_value=last_value)
    gs.execute()
    assert gs.sum_value == last_value * (last_value - 1) / 2


def test_adders():
    import random

    from mafw.examples.sum_processor import AccumulatorProcessor, GaussAdder

    last_value = random.randint(1, 1000)
    accumulator = AccumulatorProcessor(last_value=last_value)
    accumulator.execute()
    gauss = GaussAdder(last_value=last_value)
    gauss.execute()
    assert gauss.sum_value == accumulator.accumulated_value


def test_loop_modifier():
    from mafw.examples.loop_modifier import ModifyLoopProcessor

    # generate a random number corresponding to the last item
    last_value = random.randint(10, 1000)

    # get a sample with event to be skipped
    skip_items = random.sample(range(last_value), k=4)

    # find an event to abort after the last skipped one
    max_skip = max(skip_items)
    if max_skip + 1 < last_value:
        abort_item = max_skip + 1
    else:
        abort_item = last_value - 1

    # create the processor and execute it
    mlp = ModifyLoopProcessor(total_item=last_value, items_to_skip=skip_items, item_to_abort=abort_item)
    mlp.execute()

    # compare the recorded skipped items with the list we provided.
    assert mlp.skipped_items == list(sorted(skip_items))

    # check that the last item was the abort item.
    assert mlp.item == abort_item


def test_processor_list():
    # creation and execution of a processor list with no arguments.
    proc_list = ProcessorList()
    proc_list.execute()

    # creation and execution of a processor list with name but no arguments
    proc_list = ProcessorList(name='empty list')
    proc_list.execute()

    # creation and execution of a processor list with name and a list of processors
    last_value = random.randint(1, 1000)
    ga = GaussAdder(last_value=last_value)
    ap = AccumulatorProcessor(last_value=last_value)
    proc_list = ProcessorList(ga, ap, name='two item list')
    proc_list.execute()
    assert ap.accumulated_value == int(last_value * (last_value - 1) / 2)
    assert ga.sum_value == ap.accumulated_value

    # creation and execution of processor list with name and no arguments, but appending processors
    # warning adding two copies of the same processor, will cause the parameter of both to change in the same way.
    # parameters are class attributes!
    last_value += 1
    proc_list2 = ProcessorList(name='items will be appended')
    ga = GaussAdder(last_value=last_value)
    proc_list2.append(ga)
    ap = AccumulatorProcessor(last_value=last_value)
    proc_list2.append(ap)
    proc_list2.execute()
    assert ap.accumulated_value == int(last_value * (last_value - 1) / 2)
    assert ga.sum_value == ap.accumulated_value

    # extending proc_list with proc_list2
    proc_list.extend(proc_list2)
    proc_list.name = 'extended list'
    assert len(proc_list) == 4

    # they were all already executed. the output already exists.
    assert proc_list[0].sum_value == proc_list[1].accumulated_value
    assert proc_list[2].sum_value == proc_list[3].accumulated_value
    assert proc_list[1].accumulated_value != proc_list[3].accumulated_value
    assert proc_list[0].sum_value != proc_list[2].sum_value

    # execute all of them again. this time the last_value will be the same for all because of class instance limitation
    proc_list.execute()
    assert proc_list[0].sum_value == proc_list[1].accumulated_value
    assert proc_list[2].sum_value == proc_list[3].accumulated_value
    assert proc_list[1].accumulated_value == proc_list[3].accumulated_value
    assert proc_list[0].sum_value == proc_list[2].sum_value

    # processor list nesting
    last_value += 1
    nest_list = ProcessorList(name='nested')

    list1 = ProcessorList(name='list1')
    list1.append(GaussAdder(last_value=last_value))
    list1.append(AccumulatorProcessor(last_value=last_value))

    list2 = ProcessorList(name='list2')
    list2.extend([GaussAdder(last_value=last_value), AccumulatorProcessor(last_value=last_value)])

    nest_list.append(list1)
    nest_list.append(list2)
    assert len(nest_list) == 2

    nest_list.execute()
    assert nest_list[0][0].sum_value == nest_list[1][0].sum_value
    assert nest_list[0][0].sum_value == int(last_value * (last_value - 1) / 2)

    # checking resource distribution
    list1 = ProcessorList(name='list1')
    list1.append(GaussAdder(last_value=last_value))
    list1.append(AccumulatorProcessor(last_value=last_value))
    list1.execute()

    # list1 should have a timer duration, and each of its members should have a timer with the same duration
    assert list1.timer.duration != 0
    assert all([list1.timer.duration == item.timer.duration for item in list1])


def test_processor_list_abort(capsys):
    # test AbortProcessorException
    class GoodProcessor(Processor):
        n_loop = ActiveParameter('n_loop', default=100, help_doc='The n of the loop')
        sleep_time = ActiveParameter('sleep_time', default=0.01, help_doc='So much work')

        def get_items(self) -> list[int]:
            return list(range(self.n_loop))

        def process(self):
            # pretend to do something, but actually sleep
            time.sleep(self.sleep_time)

        def finish(self):
            super().finish()
            print(f'{self.name} just finished with status: {self.processor_exit_status.name}')

    class BadProcessor(Processor):
        n_loop = ActiveParameter('n_loop', default=100, help_doc='The n of the loop')
        sleep_time = ActiveParameter('sleep_time', default=0.01, help_doc='So much work')
        im_bad = ActiveParameter('im_bad', default=50, help_doc='I will crash it!')

        def get_items(self) -> list[int]:
            return list(range(self.n_loop))

        def process(self):
            if self.item == self.im_bad:
                self.looping_status = LoopingStatus.Abort
                return
            # let me do my job
            time.sleep(self.sleep_time)

        def finish(self):
            super().finish()
            print(f'{self.name} just finished with status: {self.processor_exit_status.name}')

    proc_list = ProcessorList(name='with exception')
    proc_list.extend([GoodProcessor(), BadProcessor(), GoodProcessor()])
    with pytest.raises(AbortProcessorException):
        proc_list.execute()

    output = capsys.readouterr()
    assert 'GoodProcessor just finished with status: Successful' in output.out.split('\n')
    assert 'BadProcessor just finished with status: Aborted' in output.out.split('\n')
    assert proc_list.processor_exit_status == ProcessorExitStatus.Aborted
    assert proc_list[0].processor_exit_status == ProcessorExitStatus.Successful
    assert proc_list[1].processor_exit_status == ProcessorExitStatus.Aborted
    assert proc_list[2].processor_status == ProcessorStatus.Init


def test_active_parameter():
    from mafw.processor import ActiveParameter, Processor

    @single_loop
    class MyProcess(Processor):
        my_param = ActiveParameter('my_param', default=10)

    my_proc = MyProcess(my_param=12)
    print(my_proc.my_param)  # we expect 12
    assert my_proc.my_param == 12

    second_proc = MyProcess(my_param=15)
    print(second_proc.my_param)  # we expect 15
    assert second_proc.my_param == 15

    print(my_proc.my_param)  # we would expect 12, but we get 15
    assert my_proc.my_param == 15


def test_passive_parameter():
    from mafw.processor import PassiveParameter, Processor

    class MyProcess(Processor):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, looper='single', **kwargs)
            self.my_param = PassiveParameter('my_param', default=10)

    my_proc = MyProcess(my_param=12)
    print(my_proc.my_param.value)  # we expect 12
    assert my_proc.my_param.value == 12

    second_proc = MyProcess(my_param=15)
    assert second_proc.my_param.value == 15
    print(second_proc.my_param.value)  # we expect 15

    print(my_proc.my_param.value)  # we expect 12 and we get 12!
    assert my_proc.my_param.value == 12


def test_parameter_keyword():
    class MyProcessor(Processor):
        active_param = ActiveParameter('active', default=0, help_doc='An active parameter')

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.passive_param = PassiveParameter('passive', default='I am a string', help_doc='A string')

    my_p = MyProcessor(active=100, passive='a better string', looper='single')

    print(my_p.active_param)  # we get 100
    assert my_p.active_param == 100

    print(my_p.passive_param.value)  # we get 'a better string'
    assert my_p.passive_param.value == 'a better string'


def test_parameter_configuration():
    @single_loop
    class ConfigProcessor(Processor):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.p1 = PassiveParameter('param1', default='value')
            self.p2 = PassiveParameter('param2', default='another_value')

    cp = ConfigProcessor(config=dict(param1='new_value', param2='better_value', param3='do not exists'))
    assert cp.get_parameter('param1').value == 'new_value'
    assert cp.get_parameter('param2').value == 'better_value'
    dumped_config = cp.dump_parameter_configuration(option=2)
    assert dumped_config == dict(param1='new_value', param2='better_value')
    dumped_config = cp.dump_parameter_configuration(option=20)
    assert dumped_config == dict(param1='new_value', param2='better_value')

    config = {'ConfigProcessor': {'param1': '1st', 'param2': '2nd'}}
    cp = ConfigProcessor(config=config)
    assert cp.get_parameter('param1').value == '1st'
    assert cp.get_parameter('param2').value == '2nd'
    dumped_config = cp.dump_parameter_configuration()
    assert config == dumped_config


def test_processor_list_exit_status():
    class SimpleProcessor(Processor):
        n_loop = ActiveParameter('n_loop', default=100)

        def start(self):
            super().start()
            print(f'{self.name} is working')

        def get_items(self) -> list[int]:
            return list(range(self.n_loop))

    class FailingProcessor(Processor):
        n_loop = ActiveParameter('n_loop', default=100)
        i_fail = ActiveParameter('i_fail', default=10)

        def start(self):
            super().start()
            print(f'{self.name} is working')

        def get_items(self) -> list[int]:
            return list(range(self.n_loop))

        def process(self):
            if self.i_item == self.i_fail:
                self.processor_exit_status = ProcessorExitStatus.Aborted

    processor_list = ProcessorList(name='A processor list')
    processor_list.append(FailingProcessor(n_loop=100, i_fail=50))
    processor_list.append(SimpleProcessor(n_loop=100))
    with pytest.raises(AbortProcessorException) as e:
        processor_list.execute()
    assert 'FailingProcessor' in str(e.value)
    assert processor_list[0].i_item == 99
    assert processor_list[1].processor_status == ProcessorStatus.Init


def test_unique_id():
    @single_loop
    class MyProcessor(Processor):
        pass

    @single_loop
    class MyProcessor2(Processor):
        pass

    p0 = MyProcessor()
    p1 = MyProcessor(name='ATestProcessor')
    p2 = MyProcessor(name='ATestProcessor')
    p3 = MyProcessor2(name='ATestProcessor')
    assert p0.unique_name != p1.unique_name != p2.unique_name != p3.unique_id


def test_validate_db_conf():
    # when taken from the module, the configuration is of type 2.
    type2 = default_conf['sqlite']
    validated_conf2 = validate_database_conf(type2)
    assert type2 == validated_conf2

    # transform the conf in a type 1.
    type1 = dict(DBConfiguration=type2)
    type1['OtherField'] = 5

    validated_conf1 = validate_database_conf(type1)
    assert 'OtherField' in validated_conf1
    assert 'DBConfiguration' in validated_conf1


def test_processor_with_db_conf(capsys):
    # processor with no db, but with db_conf
    @single_loop
    class DBProcessor(Processor):
        pass

    # check of setting of the db configuration
    db_proc = DBProcessor(database_conf=default_conf['sqlite'])
    assert db_proc._database is None
    with pytest.raises(MissingDatabase):
        db_proc.database
    assert db_proc._database_conf == default_conf['sqlite']
    db_proc.execute()
    assert db_proc.database is not None
    assert db_proc.database.is_closed()

    type1 = {'DBConfiguration': default_conf['sqlite'], 'OtherKey': 5}
    db_proc = DBProcessor(database_conf=type1)
    assert db_proc._database is None
    with pytest.raises(MissingDatabase):
        db_proc.database
    assert db_proc._database_conf == type1
    db_proc.execute()
    assert db_proc.database is not None
    assert db_proc.database.is_closed()

    invalid = {'URLS': 'sqlite:///:memory:'}  # URLS instead of URL
    db_proc = DBProcessor(database_conf=invalid)
    assert db_proc._database is None
    with pytest.raises(MissingDatabase):
        db_proc.database
    assert db_proc._database_conf is None
    db_proc.execute()
    assert db_proc._database is None
    with pytest.raises(MissingDatabase):
        db_proc.database

    @database_required
    @single_loop
    class ReqDBProcessor(Processor):
        def start(self):
            super().start()
            print('starting')

    db_proc = ReqDBProcessor(database_conf=default_conf['sqlite'])
    db_proc.execute()
    captured = capsys.readouterr()
    assert 'starting\n' in captured.out

    db_proc = ReqDBProcessor(database_conf=invalid)
    with pytest.raises(MissingDatabase) as e:
        db_proc.execute()
    assert f'{db_proc.name} requires an active database.' in str(e.value)


def test_method_overload():
    class SingleProcessor(Processor):
        def __init__(self, *args: Any, **kwargs: Any):
            super().__init__(*args, looper=LoopType.SingleLoop, **kwargs)

    SingleProcessor()

    class ForLoopProcessor(Processor):
        pass

    with pytest.warns(MissingOverloadedMethod, match='get_items'):
        ForLoopProcessor()

    class ProperForLoopProcessor(Processor):
        def get_items(self) -> Collection[Any]:
            return [12]

    ProperForLoopProcessor()

    @while_loop
    class WhileLoopProcessor(Processor):
        pass

    with pytest.warns(MissingOverloadedMethod, match='while_condition'):
        WhileLoopProcessor()

    @while_loop
    class ProperWhileLoopProcessor(Processor):
        def while_condition(self) -> bool:
            return False

    ProperWhileLoopProcessor()


def test_super_method_call():
    class SingleProcessor(Processor):
        pass

    # no method overload, no need to call super
    SingleProcessor(looper='single')

    # properly overloaded, no warning
    @single_loop
    class ProperlyOverloadedProcessor(Processor):
        def start(self):
            """docstring"""
            # random comment
            super().start()
            i = 10 + 2
            i = i * 2

    ProperlyOverloadedProcessor()

    # Wrongly overloaded, warning!
    class WronglyOverloadedProcessor(Processor):
        def __init__(self, *args: Any, **kwargs: Any):
            super().__init__(*args, looper=LoopType.SingleLoop, **kwargs)

        def start(self) -> None:
            i = 10 + 2
            i = i / 2

        def finish(self) -> None:
            """It does not matter when you call the super."""
            # we do something before
            i = 12
            # we call the super
            super().finish()
            # we do something else
            i = i - 1

    with pytest.warns(MissingSuperCall, match='start'):
        WronglyOverloadedProcessor()

    # Wrongly overloaded, warning!
    # super is commented out in start and finish is just pass
    class WronglyOverloadedProcessor2(Processor):
        def __init__(self, *args: Any, **kwargs: Any):
            super().__init__(*args, looper=LoopType.SingleLoop, **kwargs)

        def start(self) -> None:
            # super().start()
            i = 10 + 2
            i = i - 3

        def finish(self) -> None:
            pass

    with pytest.warns(MissingSuperCall, match='[start|finish]'):
        WronglyOverloadedProcessor2()


def test_prime_processors():
    start_from = 20
    stop_at = 50
    prime_num_to_find = 7

    prime_in_range = FindPrimeNumberInRange(start_from=start_from, stop_at=stop_at)
    n_prime = FindNPrimeNumber(start_from=start_from, prime_num_to_find=prime_num_to_find)

    prime_in_range.execute()
    n_prime.execute()

    assert len(prime_in_range.prime_num_found) == len(n_prime.prime_num_found)
    assert len(prime_in_range.prime_num_found) == prime_num_to_find
