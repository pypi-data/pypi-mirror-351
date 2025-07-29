import pytest

from mafw.active import Active


class MyClass:
    status = Active('OK')

    def do(self):
        self.status = 'ERROR'

    @staticmethod
    def on_status_change(old_status, new_status):
        if new_status == 'ERROR':
            raise Exception(f'MyClass status is {new_status}')


def test_action_functionality():
    with pytest.raises(Exception) as e:
        my_class = MyClass()
        my_class.do()

    assert 'ERROR' in str(e)
