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

## Examples

**Copy player** `MyPlayer` from `World1` to `MyPlayer` in `World2`:

```shell
cdda_tools copy-player -w World1 -p MyPlayer -w2 World2 -p2 MyPlayer
```

**Mark notes as dangerous** that contain `Moose` or `moose`, for `MyPlayer` in `World1`. Auto-travel avoidance radius 2:

```shell
cdda_tools notes -w World1 -p MyPlayer danger *[Mm]oose* --radius 2
```