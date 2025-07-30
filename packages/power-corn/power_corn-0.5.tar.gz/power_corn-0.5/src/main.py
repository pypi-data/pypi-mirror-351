import argparse
from .scripts import simplev7, get_power_info
from .modules.utilities import create_tables_if_not_exists
from . import install_cron


def run_default():
    create_tables_if_not_exists()
    simplev7.main()
    get_power_info.main()


def main():
    parser = argparse.ArgumentParser(description="power_corn CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("install-cron", help="Install cron tasks for power_corn")

    args = parser.parse_args()

    if args.command == "install-cron":
        install_cron.main()
    else:
        run_default()
