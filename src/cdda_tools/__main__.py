"""
Cataclysm DDA Python tools, CLI entrypoint.
"""
import sys
import traceback

from . import cli

if __name__ == "__main__":
    args = cli.parse_args()
    debug = args.debug
    try:
        for line in cli.run_cli(args):
            print(line)
    except Exception as e:  # pylint: disable=broad-except
        if debug:
            traceback.print_exc()
        else:
            print(f"{e.__class__.__name__}: {str(e)}")
            print(
                "\nRun with option --debug to view full stack trace:\n"
                "  cdda_tools --debug <command> ..."
            )
        sys.exit(1)

    sys.exit(0)
