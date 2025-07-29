# coding:utf-8

import os

from xkits_command.attribute import __author__
from xkits_command.attribute import __author_email__
from xkits_command.attribute import __project__
from xkits_command.attribute import __urlhome__
from xkits_command.attribute import __version__


class Project:

    def __init__(self, name: str, license: str, allow_update: bool = False):  # noqa:E501 pylint: disable=redefined-builtin
        # check illegal characters in project name
        for char in [" "]:
            if char in name:
                raise ValueError(f"Illegal character '{char}' in '{name}'")
        self.__name: str = name
        self.__module: str = self.get_module_name(name)
        self.__license: str = license
        self.__allow_update: bool = allow_update

    @property
    def name(self) -> str:
        return self.__name

    @property
    def module(self) -> str:
        return self.__module

    @property
    def license(self) -> str:
        return self.__license

    @property
    def allow_update(self) -> bool:
        return self.__allow_update

    @classmethod
    def get_module_name(cls, project_name: str) -> str:
        return project_name.replace("-", "_")

    def write(self, path: str, content: str) -> bool:
        if not os.path.exists(path) or self.allow_update:
            with open(path, "w", encoding="utf-8") as whdl:
                if len(content) > 0 and content[-1] != "\n":
                    content += "\n"
                whdl.write(content)
        return True

    def init_requirements(self):
        self.write("requirements.txt", f'''{__project__}>={__version__}''')  # noqa:E501

    def init_coveragerc(self):
        self.write(".coveragerc", f'''[run]
omit =
    {self.module}/unittest/*
    {self.module}/attribute.py

[report]
exclude_lines =
    pragma: no cover
    raise NotImplementedError
    if __name__ == .__main__.:
    def __repr__
''')

    def init_pylintrc(self):
        self.write(".pylintrc", '''[MASTER]
disable=
    C0103,   # invalid-name
    C0114,   # missing-module-docstring
    C0115,   # missing-class-docstring
    C0116,   # missing-function-docstring
    C0301,   # line-too-long
''')

    def init_makefile(self):
        self.write("Makefile", f'''MAKEFLAGS += --always-make

VERSION := $(shell python3 setup.py --version)

all: build reinstall test


release: all
	git tag -a v${{VERSION}} -m "release v${{VERSION}}"
	git push origin --tags


clean-cover:
	rm -rf cover .coverage coverage.xml htmlcov
clean-tox:
	rm -rf .stestr .tox
clean: build-clean test-clean clean-cover clean-tox


upload:
	xpip-upload --config-file .pypirc dist/*


build-clean:
	xpip-build --debug setup --clean
build-requirements:
	pip3 install -r requirements.txt
build: build-clean build-requirements
	xpip-build --debug setup --all


install:
	pip3 install --force-reinstall --no-deps dist/*.whl
uninstall:
	pip3 uninstall -y {self.name}
reinstall: uninstall install


test-prepare:
	pip3 install --upgrade mock pylint flake8 pytest pytest-cov
pylint:
	pylint $(shell git ls-files {self.module}/*.py)
flake8:
	flake8 {self.module} --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 {self.module} --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
pytest:
	pytest --cov={self.module} --cov-report=term-missing --cov-report=xml --cov-report=html --cov-config=.coveragerc --cov-fail-under=100
pytest-clean:
	rm -rf .pytest_cache
test: test-prepare pylint flake8 pytest
test-clean: pytest-clean
''')  # noqa:W191,E101,E501

    def init_project(self):
        command_module = self.get_module_name(__project__)
        os.makedirs(self.module, exist_ok=True)
        os.makedirs(os.path.join(self.module, "unittest"), exist_ok=True)
        self.write(os.path.join(self.module, "__init__.py"), "")
        self.write(os.path.join(self.module, "unittest", "__init__.py"), "")
        self.write(os.path.join(self.module, "attribute.py"),
                   f'''# coding:utf-8

__project__ = "{self.name}"
__version__ = "0.1.alpha.1"
__urlhome__ = "{__urlhome__}"
__description__ = "Automatically created by {__project__}."

# author
__author__ = "{__author__}"
__author_email__ = "{__author_email__}"
''')
        self.write(os.path.join(self.module, "command.py"),
                   f'''# coding:utf-8

from typing import Optional
from typing import Sequence

from {command_module} import ArgParser
from {command_module} import Command
from {command_module} import CommandArgument
from {command_module} import CommandExecutor

from {self.module}.attribute import __description__
from {self.module}.attribute import __project__
from {self.module}.attribute import __urlhome__
from {self.module}.attribute import __version__


@CommandArgument(__project__, description=__description__)
def add_cmd(_arg: ArgParser):  # pylint: disable=unused-argument
    pass


@CommandExecutor(add_cmd)
def run_cmd(cmds: Command) -> int:  # pylint: disable=unused-argument
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    cmds = Command()
    cmds.version = __version__
    return cmds.run(root=add_cmd, argv=argv, epilog=f"For more, please visit {{__urlhome__}}.")  # noqa:E501
''')

    def init_readme(self):
        self.write("README.md", f'''# {self.name}

> Automatically created by {__project__}.''')

    def init_setup(self):
        # create setup.cfg
        self.write("setup.cfg", f'''[metadata]
keywords = command-line, argparse, argcomplete
long_description = file: README.md
long_description_content_type = text/markdown
license = {self.license}
license_files = LICENSE
platforms = any
classifiers =
    Programming Language :: Python
    Programming Language :: Python :: 3

[options]
zip_safe = True
include_package_data = True
python_requires = >=3.8

[options.entry_points]
console_scripts =
    {self.name} = {self.module}.command:main
''')

        # create setup.py
        self.write("setup.py", f'''# coding=utf-8

from urllib.parse import urljoin

from setuptools import find_packages
from setuptools import setup
from setuptools.command.install import install

from {self.module}.attribute import __author__
from {self.module}.attribute import __author_email__
from {self.module}.attribute import __description__
from {self.module}.attribute import __project__
from {self.module}.attribute import __urlhome__
from {self.module}.attribute import __version__

__urlcode__ = __urlhome__
__urldocs__ = __urlhome__
__urlbugs__ = urljoin(__urlhome__, "issues")


def all_requirements():
    def read_requirements(path: str):
        with open(path, "r", encoding="utf-8") as rhdl:
            return rhdl.read().splitlines()

    requirements = read_requirements("requirements.txt")
    return requirements


class CustomInstallCommand(install):
    """Customized setuptools install command"""

    def run(self):
        install.run(self)  # Run the standard installation
        # Execute your custom code after installation


setup(
    name=__project__,
    version=__version__,
    description=__description__,
    url=__urlhome__,
    author=__author__,
    author_email=__author_email__,
    project_urls={{"Source Code": __urlcode__,
                  "Bug Tracker": __urlbugs__,
                  "Documentation": __urldocs__}},
    packages=find_packages(include=["{self.module}*"], exclude=["{self.module}.unittest"]),  # noqa:E501
    install_requires=all_requirements(),
    cmdclass={{
        "install": CustomInstallCommand,
    }}
)
''')  # noqa:E501

    @classmethod
    def create(cls, name: str, license: str, allow_update: bool = False) -> int:  # noqa:E501 pylint: disable=redefined-builtin
        instance = cls(name=name, license=license, allow_update=allow_update)
        instance.init_requirements()
        instance.init_coveragerc()
        instance.init_pylintrc()
        instance.init_makefile()
        instance.init_project()
        instance.init_readme()
        instance.init_setup()
        return 0
