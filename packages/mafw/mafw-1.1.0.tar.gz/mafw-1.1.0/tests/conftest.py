import pytest


@pytest.fixture
def valid_steering_file(shared_datadir):
    return shared_datadir / 'valid-steering-file.toml'


@pytest.fixture
def invalid_steering_file(shared_datadir):
    return shared_datadir / 'invalid-steering-file.toml'


@pytest.fixture
def not_existing_steering_file(shared_datadir):
    return shared_datadir / 'invalid-steering-file-xxx.toml'


@pytest.fixture
def valid_db_steering_file(shared_datadir):
    return shared_datadir / 'valid-steering-file-db.toml'
