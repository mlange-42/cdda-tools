# CDDA-Tools

[![Tests](https://github.com/mlange-42/cdda-tools/actions/workflows/tests.yml/badge.svg)](https://github.com/mlange-42/cdda-tools/actions/workflows/tests.yml)
[![coverage](https://raw.githubusercontent.com/mlange-42/cdda-tools/badges/.badges/main/coverage.svg)](https://github.com/mlange-42/cdda-tools/actions/workflows/tests.yml)
[![Lints](https://github.com/mlange-42/cdda-tools/actions/workflows/lints.yml/badge.svg)](https://github.com/mlange-42/cdda-tools/actions/workflows/lints.yml)

Python command-line tools for [Cataclysm DDA](https://cataclysmdda.org/).

## Features

* `show-data`: Browse the game's JSON data hierarchically or by search
* `table`: Display game data entries and their properties in a table
* `copy-player`: Copy player between worlds
* `copy-vehicle`: Copy vehicle between worlds
* `vehicle-mod`: Make mods from in-game vehicles
* `notes`: Edit Overmap notes, filtered by glob pattern:
   * Delete notes
   * Mark/unmark dangerous
   * Replace symbol/color/text
   * Full-text search & replace
* `note`: Add Overmap notes by coordinates
* `find`: Find Overmap terrain types (maybe later also monsters and items)
* `player`: Inspect player properties, stats, skills, body parts, ...

The tools are built against the experimental version of Cataclysm DDA,
so it may or may not work with stable releases.

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

> Note: You need to create `MyPlayer` in `World2` first. 
> It will be replaced by the player from `World1`.

Copying a vehicle basically works the same.

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

### Inspect the player

Show player skills:

```shell
cdda_tools player -w World1 -p MyPlayer skills
```

Show player properties by JSON path:

```shell
cdda_tools player -w World1 -p MyPlayer path body torso hp_cur
```

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

List everything with `Cake` or `cake` in property `description`:

```shell
cdda_tools show-data pairs description *[Cc]ake* --list
```

> Output:
> 
> ```plaintext
> achievement_lvl_7_cooking                          (achievement)
> MISSION_pizzaiolo_4                                (mission_definition)
> brown_bread                                        (COMESTIBLE)
> ...
> ```

### Tabular display

Compare three weapons in a table:

```shell
cdda_tools table TOOL/rapier TOOL/sword_bayonet TOOL/sword_xiphos --columns bashing cutting piercing weight volume
```

> Output:
>
> ```plaintext
>            id | bas | cut | pie | weight |  volume
>        rapier |   3 |  28 |   - | 1000 g | 1500 ml
> sword_bayonet |   7 |  29 |   - |  923 g | 1750 ml
>  sword_xiphos |   6 |  28 |   - |  800 g |     2 L
> ```
