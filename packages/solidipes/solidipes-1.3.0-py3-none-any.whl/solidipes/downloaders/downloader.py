import argparse
from abc import ABC, abstractmethod


class Downloader(ABC):
    command: str
    command_help: str

    @abstractmethod
    def download(self, args: argparse.Namespace) -> None:
        pass

    @abstractmethod
    def populate_arg_parser(self, parser: argparse.ArgumentParser) -> None:
        pass
