from unittest.mock import Mock

import pytest


@pytest.fixture
def screen():
    return Mock(status={}, width=80, height=20)
