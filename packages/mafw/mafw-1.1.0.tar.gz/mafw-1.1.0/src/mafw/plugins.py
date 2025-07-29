"""
Exports Processor classes to the execution script.
"""

from mafw import mafw_hookimpl
from mafw.db.std_tables import StandardTable
from mafw.examples.db_processors import CountStandardTables, FillFileTableProcessor
from mafw.examples.importer_example import ImporterExample
from mafw.examples.loop_modifier import FindNPrimeNumber, FindPrimeNumberInRange, ModifyLoopProcessor
from mafw.examples.sum_processor import AccumulatorProcessor, GaussAdder
from mafw.processor import Processor
from mafw.ui.abstract_user_interface import UserInterfaceBase
from mafw.ui.console_user_interface import ConsoleInterface
from mafw.ui.rich_user_interface import RichInterface


@mafw_hookimpl
def register_processors() -> list[type[Processor]]:
    """Returns a list of processors to be registered"""
    return [
        AccumulatorProcessor,
        GaussAdder,
        ModifyLoopProcessor,
        FillFileTableProcessor,
        CountStandardTables,
        FindNPrimeNumber,
        FindPrimeNumberInRange,
        ImporterExample,
    ]


@mafw_hookimpl
def register_user_interfaces() -> list[type[UserInterfaceBase]]:
    """Returns a list of user interfaces that can be used"""
    return [ConsoleInterface, RichInterface]


@mafw_hookimpl
def register_standard_tables() -> list[type[StandardTable]]:
    """Returns a list of Models to be used as Standard Tables in MAFw"""
    return []
