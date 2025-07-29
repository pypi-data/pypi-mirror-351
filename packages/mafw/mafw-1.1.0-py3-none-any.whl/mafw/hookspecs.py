"""
Defines the hook specification decorator bound the MAFw library.
"""

import pluggy

from mafw.processor import Processor
from mafw.ui.abstract_user_interface import UserInterfaceBase

mafw_hookspec = pluggy.HookspecMarker('mafw')


@mafw_hookspec
def register_processors() -> list[Processor]:
    """Register multiple processor classes"""
    return []


@mafw_hookspec
def register_user_interfaces() -> list[UserInterfaceBase]:
    """Register multiple user interfaces"""
    return []
