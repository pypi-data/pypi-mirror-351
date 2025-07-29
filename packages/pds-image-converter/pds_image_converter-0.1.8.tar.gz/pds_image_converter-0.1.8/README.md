# Pds Image Converter
A python module to convert PDS4 images to jpg and other quick view formats.

The public interface of the toolkit is exposed at the root level of the module, i.e.:

```python
from pds_image_converter import convert_image
```

this is expected to be the most stable portion of the toolkit.

## Usage

The tool is expected to be used as an imported function:

```python
from pds_image_converter import convert_image

convert_image(in_image=input_image, output_folder="tmp_out", configfile=cfg)
```

with

- in_image: path to the label (xml) or data file
- output_folder: the output path for the generated image
- configfile: a path to the config file to use, or alternatively the name of one of the default configurations shipped together with this package. For example `janus2quicklook` will be resolved to the config file `janus2quicklook.toml` shipped in the `configs` dir of the package.

## CLI

A cli (`pds-image-converter`) is also present but should not be used to automate the processing of files under pipelines or similar. It is mostly to support manual operation and testing of the tool.


# Additional info, from package template
[![PyPI](https://img.shields.io/pypi/v/pds-image-converter?style=flat-square)](https://pypi.python.org/pypi/pds-image-converter/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pds-image-converter?style=flat-square)](https://pypi.python.org/pypi/pds-image-converter/)
[![PyPI - License](https://img.shields.io/pypi/l/pds-image-converter?style=flat-square)](https://pypi.python.org/pypi/pds-image-converter/)
[![Coookiecutter - Wolt](https://img.shields.io/badge/cookiecutter-Wolt-00c2e8?style=flat-square&logo=cookiecutter&logoColor=D4AA00&link=https://github.com/woltapp/wolt-python-package-cookiecutter)](https://github.com/woltapp/wolt-python-package-cookiecutter)


---

**Documentation**: [https://JANUS-JUICE.github.io/pds-image-converter](https://JANUS-JUICE.github.io/pds-image-converter)

**Source Code**: [https://github.com/JANUS-JUICE/pds-image-converter](https://github.com/JANUS-JUICE/pds-image-converter)

**PyPI**: [https://pypi.org/project/pds-image-converter/](https://pypi.org/project/pds-image-converter/)

---



## Installation

```sh
pip install pds-image-converter
```

## Development

* Clone this repository
* Requirements:
  * [Poetry](https://python-poetry.org/)
  * Python 3.10+
* Create a virtual environment and install the dependencies

```sh
poetry install
```

* Activate the virtual environment

```sh
poetry shell
```

### Testing

```sh
pytest
```

### Documentation

The documentation is automatically generated from the content of the [docs directory](https://github.com/JANUS-JUICE/pds-image-converter/tree/master/docs) and from the docstrings
 of the public signatures of the source code. The documentation is updated and published as a [Github Pages page](https://pages.github.com/) automatically as part each release.



### Releasing

#### Manual release

Releases are done with the command, e.g. incrementing patch:

```bash
poetry run just bump patch
# also push, of course:
git push origin main --tags
```

this will update the changelog, commit it, and make a corresponding tag.

as the CI is not yet configured for publish on pypi it can be done by hand:

```bash
poetry publish --build
```
#### Automatic release - to be fixed


Trigger the [Draft release workflow](https://github.com/JANUS-JUICE/pds-image-converter/actions/workflows/draft_release.yml)
(press _Run workflow_). This will update the changelog & version and create a GitHub release which is in _Draft_ state.

Find the draft release from the
[GitHub releases](https://github.com/JANUS-JUICE/pds-image-converter/releases) and publish it. When
 a release is published, it'll trigger [release](https://github.com/JANUS-JUICE/pds-image-converter/blob/master/.github/workflows/release.yml) workflow which creates PyPI
 release and deploys updated documentation.

### Updating with copier

To update the skeleton of the project using copier:
```sh
 pipx run copier update --defaults
```

### Pre-commit

Pre-commit hooks run all the auto-formatting (`ruff format`), linters (e.g. `ruff` and `mypy`), and other quality
 checks to make sure the changeset is in good shape before a commit/push happens.

You can install the hooks with (runs for each commit):

```sh
pre-commit install
```

Or if you want them to run only for each push:

```sh
pre-commit install -t pre-push
```

Or if you want e.g. want to run all checks manually for all files:

```sh
pre-commit run --all-files
```

---

This project was generated using [a fork](https://github.com/luca-penasa/wolt-python-package-cookiecutter) of the [wolt-python-package-cookiecutter](https://github.com/woltapp/wolt-python-package-cookiecutter) template.
