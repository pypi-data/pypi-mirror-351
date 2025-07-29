from typing import Any

import pytest
from rich import print
from rich.console import Console
from rich.traceback import Traceback

import pipelex.config
import pipelex.pipelex
from pipelex import log
from pipelex.config import get_config

pytest_plugins = [
    "pipelex.test_extras.shared_pytest_plugins",
]


@pytest.fixture(scope="module", autouse=True)
def reset_pipelex_config_fixture():
    # Code to run before each test
    print("\n[magenta]pipelex setup[/magenta]")
    try:
        pipelex_instance = pipelex.pipelex.Pipelex.make()
        config = get_config()
        log.verbose(config, title="Test config")
        assert isinstance(config, pipelex.config.PipelexConfig)
        assert config.project_name == "pipelex"
    except Exception as exc:
        Console().print(Traceback())
        pytest.exit(f"Critical Pipelex setup error: {exc}")
    yield
    # Code to run after each test
    print("\n[magenta]pipelex teardown[/magenta]")
    pipelex_instance.teardown()


@pytest.fixture(scope="function", autouse=True)
def pretty():
    # Code to run before each test
    print("\n")
    yield
    # Code to run after each test
    print("\n")


@pytest.fixture(scope="session", autouse=True)  # pyright: ignore[reportUntypedFunctionDecorator, reportUnknownMemberType]
def apply_manage_pipelex_libraries(manage_pipelex_libraries_with_overwrite: Any):  # pyright: ignore[reportUnknownParameterType]
    return
