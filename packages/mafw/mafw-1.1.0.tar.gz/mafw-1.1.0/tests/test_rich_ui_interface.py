import time

from mafw.processor import ActiveParameter, Processor
from mafw.ui.abstract_user_interface import UserInterfaceBase
from mafw.ui.rich_user_interface import RichInterface


def test_virtual_inheritance():
    assert issubclass(RichInterface, UserInterfaceBase)


def test_execution_with_single_processor():
    class MyProcessor(Processor):
        n_loop = ActiveParameter('n_loop', default=10)
        sleep = ActiveParameter('sleep', default=0.001)

        def get_items(self) -> list[int]:
            return list(range(self.n_loop))

        def process(self):
            time.sleep(self.sleep)

    rich_ui = RichInterface(progress_kws=dict(auto_refresh=True, expand=True))

    p = MyProcessor(user_interface=rich_ui)
    p.execute()
