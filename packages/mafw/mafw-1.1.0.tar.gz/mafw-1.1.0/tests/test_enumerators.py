import pytest

from mafw.enumerators import LoopType


def test_loop_type():
    known_types = ('single', 'for_loop', 'while_loop')
    for t in known_types:
        LoopType(t)

    unknown_type = ('12test34', 'Signle')
    for t in unknown_type:
        with pytest.raises(ValueError, match=t):
            LoopType(t)

    t = LoopType.ForLoop
    nt = LoopType(t)

    assert t == nt
