# CDDA-Tools

[![Tests](https://github.com/mlange-42/cdda-tools/actions/workflows/tests.yml/badge.svg)](https://github.com/mlange-42/cdda-tools/actions/workflows/tests.yml)

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
* `show-data`: Browse the game's JSON data hierarchically or by ID search

## Installation

```shell
pip install git+https://github.com/mlange-42/cdda-tools.git
```

## Usage

:warning: Backup your save files before using these tools! ABSOLUTELY NO WARRANTY! :warning:

Run CDDA-Tools in your Cataclysm game directory:

```shell
python -m cdda_tools --help
python -m cdda_tools <command> --help
```

Alternatively, use option `--dir` to specify the game directory.

> Note that most commands have a `--dry` switch to test them without modifying any files.

## Examples

### Copy player

Copy player `MyPlayer` from `World1` to `MyPlayer` in `World2`:

```shell
cdda_tools copy-player -w World1 -p MyPlayer -w2 World2 -p2 MyPlayer
```

### Make a vehicle mod

Make a mod from an in-game vehicle:

```shell
cdda_tools vehicle-mod -w World1 -v "My Death Mobile" --id death_mobile > my_death_mobile.json  // Windows
cdda_tools vehicle-mod -w World1 -v "My Death Mobile" --id death_mobile | my_death_mobile.json  // Linux
```

> Note: You will need to create the accompanying `modinfo.json` file yourself. 

### Manipulate overmap notes

Mark notes as dangerous that contain `Moose` or `moose`, for `MyPlayer` in `World1`. Auto-travel avoidance radius 2:

```shell
cdda_tools notes -w World1 -p MyPlayer danger *moose* --radius 2
cdda_tools notes -w World1 -p MyPlayer danger *Moose* *moose* --case --radius 2
cdda_tools notes -w World1 -p MyPlayer danger *[Mm]oose* --case --radius 2
```

> Note: try `cdda_tools notes -h` to explore features like editing and deleting notes.

### Browse the game's JSON data

List all JSON entries with `wrench` in their ID:

```shell
cdda_tools show-data ids *wrench* --list
```

> Output:
> 
> ```plaintext
> mon_feral_sailor_lug_wrench_death_drops            (item_group)
> cordless_impact_wrench                             (TOOL)
> socket_wrench_set                                  (TOOL)
> ...
> ```

Show all JSON categories:

```shell
cdda_tools show-data path --keys
```

> Output:
> 
> ```plaintext
> ['AMMO', 'ARMOR', 'BATTERY', 'BIONIC_ITEM', 'BOOK', 'COMESTIBLE',
> 'ENGINE', 'GENERIC', 'GUN', 'GUNMOD', 'ITEM_CATEGORY', 'LOOT_ZONE',
> ... 
> ```

Show JSON entry for `wrench` of category `TOOL`:

```shell
cdda_tools show-data path TOOL wrench
```

> Output:
> 
> ```plaintext
> {
>     "id": "wrench",
>     "type": "TOOL",
>     "name": {
> ...
> ```