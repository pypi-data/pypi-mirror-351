import argparse
from abc import ABC, abstractmethod


class Uploader(ABC):
    command: str
    command_help: str

    @abstractmethod
    def upload(self, args: argparse.Namespace) -> None:
        pass

    @abstractmethod
    def populate_arg_parser(self, parser: argparse.ArgumentParser) -> None:
        pass


################################################################


def text_progress_bar(filename, size):
    from tqdm import tqdm

    bar = tqdm(
        desc=filename,
        total=size,
        unit="iB",
        unit_scale=True,
        unit_divisor=1024,
    )
    return bar
