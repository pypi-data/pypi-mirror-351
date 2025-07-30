import argparse
from pathlib import Path

import minute_count.version as version
from minute_count.minute_count import minute_overview
from minute_count.terminal_formatting import add_color

PROGRAM_NAME = "minute-count"


def command_entry_point():
    try:
        main()
    except KeyboardInterrupt:
        print(add_color(1, "Program was interrupted by user"))


def main():
    parser = argparse.ArgumentParser(prog=PROGRAM_NAME,
                                     description="A command-line tool for generating an overview over the amount of minutes (in terms of mp3 files) in a directory",
                                     allow_abbrev=True, add_help=True, exit_on_error=True)

    parser.add_argument("FILE", help="The path for which to calculate the overview")
    parser.add_argument("-r", "--recursive", action="store_true",
                        help="Generates overview for all subdirectories. Note that this information is calculated anyways, as the seconds in a directory is just summed over all files contained within it.")
    parser.add_argument("-f", "--file", action="store_true",
                        help="Show the overview for files as well as directories")
    parser.add_argument("-s", "--no-seconds", action="store_true", help="Hides the seconds part of the duration")
    parser.add_argument("-a", "--hidden", action="store_true",
                        help="Also account for hidden files, meaning files prefixed with a period")
    parser.add_argument("--version", action="store_true", help="Show the current version of the program")

    args = parser.parse_args()

    if args.version:
        print(f"{PROGRAM_NAME} version {version.program_version}")
        return

    path = Path(args.FILE)

    if not path.exists():
        print(f"The path {add_color(1, path)} does not exist")
        return

    minute_overview(
        path,
        args.recursive,
        True,
        args.file,
        args.hidden,
        True,
        not args.no_seconds
    )
