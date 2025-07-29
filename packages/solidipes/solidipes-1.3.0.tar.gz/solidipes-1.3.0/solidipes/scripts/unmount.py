import argparse

command = "unmount"
command_help = "Unmount cloud storage"


def main(args) -> None:
    import os

    from ..mounters.cloud import Mounter, get_cloud_info, list_mounts, set_cloud_info
    from ..utils import bcolors, get_path_relative_to_root

    mounts = list_mounts(only_mounted=not args.forget)
    # --list-mounted: show mounted directories
    if args.list_mounted:
        print("Currently mounted directories:")

        for path, mount_info in mounts.items():
            if not mount_info.get("mounted"):
                continue
            print(f"    {path} {bcolors.BRIGHT_GREEN}({mount_info['type']}, {mount_info['system']}){bcolors.RESET}")

        return

    if args.all:
        from ..mounters.cloud import unmount_all

        unmount_all(**vars(args))
        return

    config = get_cloud_info()

    # --path: unmount specified directory, otherwise unmount all
    if args.path:
        path = args.path.rstrip(os.sep)
        if path not in mounts:
            print(f'"{path}" has not been mounted with "solidipes mount".')
            return
        paths_to_unmount = [path]
    else:
        paths_to_unmount = list(mounts.keys())

    if len(paths_to_unmount) == 0:
        print("Nothing to unmount.")
        return

    for path in paths_to_unmount:  # path relative working directory
        try:
            if os.path.ismount(path):
                Mounter.unmount(path)
                print(f'Unmounted "{path}"')

        except RuntimeError as e:
            print(f"Error unmounting {path}: {e}")
            continue

        if args.forget:
            path_relative_to_root = get_path_relative_to_root(path)
            if path_relative_to_root in config:
                del config[path_relative_to_root]
                print(f'Forgot mount info for "{path}"')

    if args.forget:
        set_cloud_info(config)


def populate_arg_parser(parser) -> None:
    parser.description = command_help

    parser.add_argument("path", help="Path of the directory to unmount.", nargs="?")

    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Unmount all mounts",
    )

    parser.add_argument(
        "-f",
        "--forget",
        help="Also delete mount info from saved configuration",
        action="store_true",
    )

    parser.add_argument(
        "-l",
        "--list-mounted",
        help="List currently mounted directories",
        action="store_true",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    populate_arg_parser(parser)
    args = parser.parse_args()
    main(args)
