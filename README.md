# CDDA-Tools

Python command-line tools for [Cataclysm DDA](https://cataclysmdda.org/).

## Features

* Copy player between worlds
* Copy vehicle between worlds
* Edit Overmap notes, filtered by glob pattern:
   * Delete notes
   * Mark/unmark dangerous
   * Replace symbol/color/text
   * Full-text search & replace

## Installation

```shell
pip install git+https://github.com/mlange-42/cdda-tools.git
```

## Usage

Run CDDA-Tools in your CDDA game directory:

```shell
python -m cdda_tools --help
python -m cdda_tools <command> --help
```

Alternatively, use option `--dir` to specify the game directory.
