import argparse

from handlers import get_handler


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='subcommand')

    subparsers.add_parser('deploy')

    return parser


def cli():
    parser = get_parser()
    args = parser.parse_args()

    if args.subcommand is None:
        print('Subcommand required; use -h or --help for more information')
        exit(1)

    handler = get_handler(args.subcommand)
    handler()
