import argparse

from solidipes.plugins.discovery import uploader_list

command = "upload"
command_help = "Upload dataset to an online repository"


# Get all uploaders
uploader_subclasses_instances = [Subclass() for Subclass in uploader_list]
uploaders = {}
for e in uploader_subclasses_instances:
    commands = e.command
    if isinstance(commands, str):
        commands = [commands]
    for c in commands:
        uploaders[c] = e


def main(args) -> None:
    platform = args.platform
    uploader = uploaders[platform]
    uploader.upload(args)


def populate_arg_parser(parser) -> None:
    # Create subparsers for each upload platform
    uploader_parsers = parser.add_subparsers(dest="platform", help="Target hosting platform")
    uploader_parsers.required = True

    for uploader_command in uploaders:
        uploader_parser = uploader_parsers.add_parser(uploader_command, help=uploaders[uploader_command].command_help)
        uploaders[uploader_command].populate_arg_parser(uploader_parser)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    populate_arg_parser(parser)
    args = parser.parse_args()
    main(args)
