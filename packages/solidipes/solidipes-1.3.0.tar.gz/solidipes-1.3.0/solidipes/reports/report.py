import argparse
from abc import ABC, abstractmethod


class Report(ABC):
    command: str
    command_help: str

    @abstractmethod
    def make(self, args: argparse.Namespace) -> None:
        pass

    @abstractmethod
    def populate_arg_parser(self, parser: argparse.ArgumentParser) -> None:
        pass
