# Legion Utils

Utilities for Legion Reporters and Monitors

## Usage

TODO

## Installation & Setup

To install legion-utils with [`pip`](https://pip.pypa.io/en/stable/) execute the following:

```bash
pip install /path/to/repo/legion-utils
```

If you don't want to re-install every time there is an update, and prefer to just pull from the git repository, then use the `-e` flag.

## Development

### Standards

- Be excellent to each other
- Code coverage must be at 100% for all new code, or a good reason must be provided for why a given bit of code is not covered.
  - Example of an acceptable reason: "There is a bug in the code coverage tool and it says its missing this, but it's not".
  - Example of unacceptable reason: "This is just exception handling, its too annoying to cover it".
- The code must pass the following analytics tools. Similar exceptions are allowable as in rule 2.
  - `pylint --disable=C0111,W1203,R0903 --max-line-length=100 ...`
  - `flake8 --max-line-length=100 ...`
  - `mypy --ignore-missing-imports --follow-imports=skip --strict-optional ...`
- All incoming information from users, clients, and configurations should be validated.
- All internal arguments passing should be typechecked whenever possible with `typeguard.typechecked`

### Development Setup

Using [PDM](https://pdm-project.org/latest/) install from inside the repo directory:

```bash
pdm install
```

#### IDE Setup

**PyCharm**

You're going to want to install the [Pydantic PyCharm Plugin](https://koxudaxi.github.io/pydantic-pycharm-plugin/type-checker-for-pydantic/) for proper type-safety warnings and stuff.

## Testing

All testing should be done with `pytest` which is installed with the `dev` requirements.

To run all the unit tests, execute the following from the repo directory:

```bash
pdm run pytest
```

This should produce a coverage report in `htmlcov/`

While developing, you can use [`watchexec`](https://github.com/watchexec/watchexec) to monitor the file system for changes and re-run the tests:

```bash
watchexec -r -e py,yaml pdm run pytest
```

To run a specific test file:

```bash
pdm run pytest tests/unit/test_core.py
```

To run a specific test:

```bash
pdm run pytest tests/unit/test_core.py::test_hello
```

For more information on testing, see the `pytest.ini` file as well as the [documentation](https://docs.pytest.org/en/stable/).

### Building & Publishing to PyPi

You can use [Twine](https://www.geeksforgeeks.org/how-to-publish-python-package-at-pypi-using-twine-module/) to publish this code to [PyPi](https://pypi.org/project/legion-utils/) assuming you have an account and the relevant project permissions. This can be configured using a [`~/.pypirc` file]() like so:

```
[distutils]
  index-servers =
    pypi
    testpypi

[testpypi]
  username = __token__
  password = <PYPI TOKEN>

[pypi]
  username = __token__
  password = <PYPI TOKEN>
```

You can get the PyPi Tokens here: https://pypi.org/help/#apitoken

Once you have that set up, you can build, publish to the test server, and then the prod server with the following commands:

```bash
pdm build;

pdm publish-test; # test

pdm publish-prod; # prod
```