"""Inspect the player"""
import argparse
import json
import math

from .. import game, json_utils
from . import Command, util


class InspectPlayer(Command):
    """Inspect the player"""

    def add_subcommand(self, subparsers):
        parser = subparsers.add_parser(
            "player",
            help="Inspect the player.",
            description="Inspect the player.\n\n"
            "Example:\n\n"
            "  cdda_tools player ...",
            formatter_class=argparse.RawTextHelpFormatter,
        )

        util.add_world_option(parser, "the game world")

        parser.add_argument(
            "--player",
            "-p",
            type=str,
            help="the player to inspect, optional if only one player in world",
        )

        subparsers = parser.add_subparsers(
            help="Player sub-commands",
            dest="player_subcommand",
            required=True,
        )

        _add_parser_path(subparsers)
        _add_parser_stats(subparsers)
        _add_parser_skills(subparsers)
        _add_parser_profs(subparsers)
        _add_parser_body(subparsers)

    def exec(self, arg):
        if arg.player_subcommand == "path":
            yield from _path(arg)
        elif arg.player_subcommand == "stats":
            yield from _stats(arg)
        elif arg.player_subcommand == "skills":
            yield from _skills(arg)
        elif arg.player_subcommand == "profs":
            yield from _profs(arg)
        elif arg.player_subcommand == "body":
            yield from _body(arg)
        else:
            raise ValueError(
                "Unknown player sub-command '{}'.".format(arg.player_subparser)
            )


def _profs(arg):
    world_dir = util.get_world_path(arg.dir, arg.world)
    save, _, _player_name = util.get_save_path(world_dir, arg.player)

    source = json_utils.read_json(save)
    player = source["player"]
    profs = player["proficiencies"]

    for prof in profs["known"]:
        yield prof

    if arg.raw:
        for prof in profs["learning"]:
            yield "{:30} {} h".format(prof["id"], round(prof["practiced"] / 3600, 1))
    else:
        data = game.read_game_data(arg.dir, ["proficiency"])
        all_profs = data["proficiency"]

        for prof in profs["learning"]:
            total_time = all_profs[prof["id"]]["time_to_learn"]
            yield "{:30} {} h / {}".format(
                prof["id"], round(prof["practiced"] / 3600, 1), total_time
            )


def _stats(arg):
    world_dir = util.get_world_path(arg.dir, arg.world)
    save, _, _player_name = util.get_save_path(world_dir, arg.player)

    source = json_utils.read_json(save)
    player = source["player"]

    yield "Str {:2}/{:2}".format(player["str_cur"], player["str_max"])
    yield "Dex {:2}/{:2}".format(player["dex_cur"], player["dex_max"])
    yield "Int {:2}/{:2}".format(player["int_cur"], player["int_max"])
    yield "Per {:2}/{:2}".format(player["per_cur"], player["per_max"])


def _skills(arg):
    world_dir = util.get_world_path(arg.dir, arg.world)
    save, _, _player_name = util.get_save_path(world_dir, arg.player)

    source = json_utils.read_json(save)
    player = source["player"]
    skills = player["skills"]

    for skill, stats in skills.items():
        rel_exp = int((100 * stats["exercise"]) / _required_exercise(stats["level"]))
        rel_exp_know = int(
            (100 * stats["knowledgeExperience"])
            / _required_exercise(stats["knowledgeLevel"])
        )
        yield "{:15} {:2} {:2}% | {:2} {:2}%".format(
            skill, stats["level"], rel_exp, stats["knowledgeLevel"], rel_exp_know
        )


def _body(arg):
    world_dir = util.get_world_path(arg.dir, arg.world)
    save, _, _player_name = util.get_save_path(world_dir, arg.player)

    source = json_utils.read_json(save)
    player = source["player"]
    body = player["body"]

    yield "        |   HP | Temp |  Wet |"
    for part, stats in body.items():
        temp = int((stats["temp_conv"] - 5000) * 0.02)
        hit_pt = int((100 * stats["hp_cur"]) / stats["hp_max"])
        wet = stats["wetness"]
        yield "{:7} | {:3}% | {:4} | {:4} |".format(part, hit_pt, temp, wet)


def _path(arg):
    # pylint: disable=duplicate-code
    world_dir = util.get_world_path(arg.dir, arg.world)
    save, _, _player_name = util.get_save_path(world_dir, arg.player)

    source = json_utils.read_json(save)
    player = source["player"]

    extract = player
    search_str = "player"

    if arg.values is not None:
        for key in arg.values:
            util.check_is_dict(extract, search_str)

            if key in extract:
                extract = extract[key]
            else:
                raise ValueError(f"Id {key} not found in {search_str}")
            search_str += f"/{key}"

    if arg.keys:
        keys = list(extract.keys())
        keys.sort()
        if arg.label:
            yield search_str + "=" + keys
        else:
            yield keys
    else:
        text = json.dumps(extract, indent=4)
        if arg.label:
            yield search_str + "=" + text
        else:
            yield text


def _required_exercise(level):
    return 10000 * math.pow(level + 1, 2)


def _add_parser_path(subparsers):
    parser_path = subparsers.add_parser(
        "path",
        help="Show data by JSON path.",
        description="Show data by JSON path.\n\n"
        "Examples:\n\n"
        "  cdda_tools player -w MyWorld -p MyPlayer path dex_cur\n"
        "  cdda_tools player -w MyWorld -p MyPlayer path body torso hp_cur",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # pylint: disable=duplicate-code
    parser_path.add_argument(
        "values",
        type=str,
        nargs="*",
        help="key path to print player data for",
    )
    parser_path.add_argument(
        "--keys",
        "-k",
        action="store_true",
        help="print only property keys",
    )
    parser_path.add_argument(
        "--label",
        "-l",
        action="store_true",
        help="print keys in front of the data",
    )


def _add_parser_stats(subparsers):
    _parser_stats = subparsers.add_parser(
        "stats",
        help="Show player stats.",
        description="Show player stats.\n\n"
        "Example:\n\n"
        "  cdda_tools player -w MyWorld -p MyPlayer stats",
        formatter_class=argparse.RawTextHelpFormatter,
    )


def _add_parser_skills(subparsers):
    _parser_stats = subparsers.add_parser(
        "skills",
        help="Show player skills.",
        description="Show player skills.\n\n"
        "Example:\n\n"
        "  cdda_tools player -w MyWorld -p MyPlayer skills",
        formatter_class=argparse.RawTextHelpFormatter,
    )


def _add_parser_profs(subparsers):
    parser_stats = subparsers.add_parser(
        "profs",
        help="Show player proficiencies.",
        description="Show player proficiencies.\n\n"
        "Example:\n\n"
        "  cdda_tools player -w MyWorld -p MyPlayer profs",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser_stats.add_argument(
        "--raw",
        "-r",
        action="store_true",
        help="print raw profs stats (does not require game JSON data)",
    )


def _add_parser_body(subparsers):
    _parser_body = subparsers.add_parser(
        "body",
        help="Show player body parts.",
        description="Show player body parts.\n\n"
        "Example:\n\n"
        "  cdda_tools player -w MyWorld -p MyPlayer body",
        formatter_class=argparse.RawTextHelpFormatter,
    )
