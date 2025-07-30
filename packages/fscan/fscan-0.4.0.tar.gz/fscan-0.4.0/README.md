# Fscan

[![PyPI version](https://badge.fury.io/py/fscan.svg)](https://badge.fury.io/py/fscan)
![Conda](https://img.shields.io/conda/v/conda-forge/fscan?label=conda-forge)
![PyPI - License](https://img.shields.io/pypi/l/fscan)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/fscan)

Fscan pipeline for characterizing persistent narrowband spectral artifacts in gravitational wave detector data

## Installation

On Unix systems, Fscan can be installed easily using PyPI:

```shell
pip install fscan
```

## Example for running Fscan

Run the `FscanDriver <args>` exectuable with appropriate arguments (see `FscanDriver -h` for additional details). For example at CIT:

```bash
$ FscanDriver -C 1 -O 1 -A ligo.dev.o4.detchar.linefind.fscan -U albert.einstein --full-band-avg=1 --analysisStart=20200229 --analysisDuration=1day --averageDuration=1day -y fscan/configuration/examples/example_ch_info.yml -f .
```

### Another example (using a configuration file)

Running from the Fscan source directory,

```bash
FscanDriver --config configuration/example.config
```

Be sure to edit the arguments in `example.config` to reflect the locations of your lalsuite and fscan installations.
