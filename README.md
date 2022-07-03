# CDDA-Tools

Python command-line tools for [Cataclysm DDA](https://cataclysmdda.org/).

## Features

* `copy-player`: Copy player between worlds
* `copy-vehicle`: Copy vehicle between worlds
* `vehicle-mod`: Make mods from in-game vehicles
* `notes`: Edit Overmap notes, filtered by glob pattern:
   * List be search pattern
   * Delete notes
   * Mark/unmark dangerous
   * Replace symbol/color/text
   * Full-text search & replace
* `note`: Add Overmap notes
* `find`: Find Overmap terrain types, and maybe later also monsters and items

## Installation

```shell
pip install git+https://github.com/mlange-42/cdda-tools.git
```

## Usage

:warning: Backup your save files before usage! NO WARRANTY! :warning:

Run CDDA-Tools in your Cataclysm game directory:

```shell
python -m cdda_tools --help
python -m cdda_tools <command> --help
```

Alternatively, use option `--dir` to specify the game directory.

> Note that most commands have a `--dry` switch to test them without modifying any files.

## Examples

Copy player `MyPlayer` from `World1` to `MyPlayer` in `World2`:

```shell
cdda_tools copy-player -w World1 -p MyPlayer -w2 World2 -p2 MyPlayer
```

Mark notes as dangerous that contain `Moose` or `moose`, for `MyPlayer` in `World1`. Auto-travel avoidance radius 2:

```shell
cdda_tools notes -w World1 -p MyPlayer danger *moose* --radius 2
cdda_tools notes -w World1 -p MyPlayer danger *Moose* *moose* --case --radius 2
cdda_tools notes -w World1 -p MyPlayer danger *[Mm]oose* --case --radius 2
```

Make a mod from an in-game vehicle:

```shell
cdda_tools vehicle-mod -w World1 -v "My Death Mobile" --id death_mobile > my_death_mobile.json  // Windows
cdda_tools vehicle-mod -w World1 -v "My Death Mobile" --id death_mobile | my_death_mobile.json  // Linux
```
