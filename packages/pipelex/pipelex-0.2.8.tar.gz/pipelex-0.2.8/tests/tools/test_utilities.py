import inspect

from pipelex import pretty_print
from pipelex.tools.config.manager import config_manager


class TestUtilities:
    def test_get_package_name_here_1(self):
        frame = inspect.currentframe()
        module = inspect.getmodule(frame)
        assert module is not None
        package_name = module.__name__.split(sep=".", maxsplit=1)[0]
        pretty_print(package_name, title="package_name")
        assert package_name == "tests"

    def test_get_package_name_here_2(self):
        """Get the name of the package containing this module."""
        package_name = __name__.split(".", maxsplit=1)[0]
        pretty_print(package_name, title="package_name")
        assert package_name == "tests"

    def test_get_project_name(self):
        project_name = config_manager.get_project_name()
        pretty_print(project_name, title="project_name")
