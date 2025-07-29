# Identity Lib

This Python package contains shared code related to Identity systems within UIS. It's primary
purpose is to encourage code-reuse and to allow for client systems to make use of the same
data structures and logic that is contained within our emergent identity APIs.

## Use

Install `ucam-identitylib` using pip:

```
pip install ucam-identitylib
```

The module can then be used as `identitylib`:

```python3
from identitylib.identifiers import Identifier

identifier = Identifier.from_string('wgd23@v1.person.identifiers.cam.ac.uk')
print(identifier)
```

## Developer quickstart

This project depends on `poetry` & `poe`:

```console
pipx install poetry
pipx inject poetry poethepoet[poetry_plugin]
```

This project contains a dockerized testing environment which wraps [tox](https://tox.readthedocs.io/en/latest/).

Tests can be run using the `tox` poe command:

```bash
# Run all PyTest tests and Flake8 checks
$ poetry poe tox

# Run PyTest and Flake8 and recreate test environments
$ poetry poe tox --recreate

# Run just PyTest
$ poetry poe tox -e py3

# Run a single test file within PyTest
$ poetry poe tox -e py3 -- tests/test_identifiers.py

# Run a single test file within PyTest with verbose logging
$ poetry poe tox -e py3 -- tests/test_identifiers.py -vvv
```

### Pulling latest specs from source repositories

Local copies of the OpenAPI specs used to generate the library should be pulled in to this repo
so the specific specs used in each build are under revision control. This can be done using the
provided poe command:

```bash
$ poetry poe pull-specs

# If an access token required for https clones from gitlab repositories
# then this can be specified using:
$ poetry poe pull-specs --token "ACCESS_TOKEN_HERE"

# You may need to first set the $USER environment variable to match the GitLab account name.

```

### Generating the identitylib

The identitylib is generated during the docker build process. To create a local copy of the
identitylib distribution use the poe command:

```bash
$ poetry poe build-local
```

This will create a new folder `/dist` in the current directory with the wheel and tar package for
identitylib.

### Interactive testing

An interactive testing environment is provided to smoke-test any changes to the identitylib against
staging or local instances of the APIs. Note that to test local instance you will need to set the
URL in the config file to `host.docker.internal:<PORT NUMBER>` on linux.

To set up the interactive testing environment, copy the `scripts/api-loader-config.yaml.example`
file to `scripts/api-loader-config.yaml` and populate with valid API key/secret pairs for any of
the APIs you wish to test.

Run the interactive test environment against the latest test release (i.e. uploaded to
`test.pypi.org`) of the library using the poe command:

```bash
$ poetry poe interactive-test
```

To run the interactive tests using a local copy of `identitylib` from the `dist` directory:

```bash
$ poetry poe interactive-test:local --source dist/ucam_identitylib-1.7.0-py3-none-any.whl
```

will build the interactive environment from a local wheel stored in the `dist` directory.

Once the environment is active you can load up test instances and manipulate them using the python
interactive console. The `LOADER` global variable contains a helper class which reads the config
file and generates clients based off it:

```python
# Docker build output...
>>> config, client, inst = LOADER.load_card()
>>> inst.v1beta1_cards_list()
... # Output printed to the screen
```

Use the builtin `help` command to view info on the `LOADER`, and the returned `api_inst` objects
that can be used to make requests.

You can view the structure of the generated `identitylib` package using the `get_module_structure`
function:

```python
>>> import identitylib
>>> from pprint import pprint
>>> pprint(get_module_structure(identitylib))
...
```
