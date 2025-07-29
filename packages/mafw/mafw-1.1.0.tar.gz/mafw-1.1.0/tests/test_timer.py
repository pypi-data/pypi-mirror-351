import time

from mafw.timer import Timer


def test_timer():
    durations = []
    n = 10
    scale = 100
    for i in range(n):
        with Timer(suppress_message=True) as t:
            time.sleep(1 / scale)
        durations.append(t.duration)

    expected = n / scale
    print(sum(durations))
    assert 1 < sum(durations) / expected < 1.5
