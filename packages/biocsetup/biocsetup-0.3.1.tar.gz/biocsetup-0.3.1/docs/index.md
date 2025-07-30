# biocsetup

BiocSetup helps scaffold new Python packages in [BiocPy](https://github.com/biocpy) with consistent configuration for package management.

It automates the setup process by using PyScaffold with additional configurations specific to BiocPy projects, including documentation setup, GitHub Actions for testing and publishing, and code quality tools.

For more details, see our [developer guide](https://github.com/BiocPy/developer_guide).

## Installation

```bash
pip install biocsetup
```

## Usage

### Command Line Interface

Create a new package using the command line:

```bash
biocsetup my-new-package --description "Description of my package" --license MIT
```

Options:

- `--description`, `-d`: Project description
- `--license`, `-l`: License to use (default: MIT)
- `--rst`: To use reStructuredText, otherwise uses Markdown by default.

### Python API

You can also create packages programmatically:

```python
from biocsetup import create_repository

create_repository(
    project_path="my-new-package",
    description="Description of my package",
    license="MIT",
    rst=False,
)
```

## After setup

- The GitHub workflows use "trusted publisher workflow" to publish packages to PyPI. Read more instructions [here](https://docs.pypi.org/trusted-publishers/).
  - Tagging the repository will trigger an action to test, generate documentation, and publish the package to PyPI.
- Install [tox](https://tox.wiki/en/4.23.2/) to handle package tasks. GitHub Actions relies on the tox configuration to test, generate documentation, and publish packages.
- (Optional) Enable the [pre-commit.ci](https://pre-commit.ci/) bot for your repository.
- (Optional) Install [ruff](https://docs.astral.sh/ruff/) for code formatting.
- (Optional) Setup [codecov](https://about.codecov.io/) for coverage reports.

## Contents

```{toctree}
:maxdepth: 2

Overview <readme>
Tutorial <tutorial>
Contributions & Help <contributing>
License <license>
Authors <authors>
Changelog <changelog>
Module Reference <api/modules>
```

## Indices and tables

* {ref}`genindex`
* {ref}`modindex`
* {ref}`search`

[Sphinx]: http://www.sphinx-doc.org/
[Markdown]: https://daringfireball.net/projects/markdown/
[reStructuredText]: http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
[MyST]: https://myst-parser.readthedocs.io/en/latest/
