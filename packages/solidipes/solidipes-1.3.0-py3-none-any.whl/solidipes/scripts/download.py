import argparse

from solidipes.plugins.discovery import downloader_list

command = "download"
command_help = "Download dataset to an online repository"


# Get all downloaders
downloader_subclasses_instances = [Subclass() for Subclass in downloader_list]
downloaders = {}
for e in downloader_subclasses_instances:
    commands = e.command
    if isinstance(commands, str):
        commands = [commands]
    for c in commands:
        downloaders[c] = e


def main(args) -> None:
    platform = args.platform
    downloader = downloaders[platform]
    downloader.download(args)


def populate_arg_parser(parser) -> None:
    # Create subparsers for each download platform
    downloader_parsers = parser.add_subparsers(dest="platform", help="Target hosting platform")
    downloader_parsers.required = True

    for downloader_command in downloaders:
        downloader_parser = downloader_parsers.add_parser(
            downloader_command, help=downloaders[downloader_command].command_help
        )
        downloaders[downloader_command].populate_arg_parser(downloader_parser)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    populate_arg_parser(parser)
    args = parser.parse_args()
    main(args)
