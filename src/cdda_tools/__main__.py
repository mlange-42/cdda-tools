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
        cli.run_cli(args)
    except Exception as e:  # pylint: disable=broad-except
        if debug:
            traceback.print_exc()
        else:
            print(f"{e.__class__.__name__}: {str(e)}")
            print(
                "  Run with option --debug to view full stack trace:\n"
                "  cdda_tools --debug <command> ..."
            )
        sys.exit(1)
