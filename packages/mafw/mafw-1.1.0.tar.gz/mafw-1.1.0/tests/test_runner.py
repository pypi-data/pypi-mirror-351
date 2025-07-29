from pathlib import Path

import pytest
from pluggy import PluginManager

import mafw.mafw_errors
from mafw.runner import MAFwApplication
from mafw.ui.abstract_user_interface import UserInterfaceBase


def test_application_creation1(not_existing_steering_file):
    # creation of an app with a not existing steering file
    with pytest.raises(FileNotFoundError):
        MAFwApplication(not_existing_steering_file)


def test_application_creation2(invalid_steering_file):
    # creation of an app with an invalid steering file and no other arguments.
    with pytest.raises(mafw.mafw_errors.InvalidSteeringFile):
        MAFwApplication(invalid_steering_file)


def test_application_creation3(valid_steering_file):
    # creation of an app with valid steering file and no other arguments.
    app = MAFwApplication(valid_steering_file)
    assert isinstance(app.steering_file, Path)
    assert isinstance(app.plugin_manager, PluginManager)
    assert isinstance(app.user_interface, UserInterfaceBase)
    assert app.user_interface.name == 'rich'


def test_application_creation4(valid_steering_file):
    # creation of an app with valid steering file as string
    steering_file_name_str = str(valid_steering_file)
    app = MAFwApplication(steering_file_name_str)
    assert isinstance(app.steering_file, Path)


def test_application_creation5(valid_steering_file):
    # creation of an app with valid steering file and user interface set to rich
    # but overridden to console in the constructor.
    app = MAFwApplication(valid_steering_file, user_interface='console')
    assert isinstance(app.user_interface, UserInterfaceBase)
    assert app.user_interface.name == 'console'


def test_application_creation6(valid_steering_file):
    # creation of an app with valid steering file and user interface set to rich
    # but overridden to something wrong in the constructor.
    # still get console has fall back.
    app = MAFwApplication(valid_steering_file, user_interface='unknown')
    assert isinstance(app.user_interface, UserInterfaceBase)
    assert app.user_interface.name == 'console'


def test_application_creation7(valid_steering_file):
    # creation of an app with no steering file
    app = MAFwApplication()
    assert not app._initialized

    # attempt to run a not initialised app.
    with pytest.raises(mafw.mafw_errors.RunnerNotInitialized):
        app.run()

    # attempt to run a not initialised app passing steering file to run.
    app.run(valid_steering_file)
    assert app._initialized
