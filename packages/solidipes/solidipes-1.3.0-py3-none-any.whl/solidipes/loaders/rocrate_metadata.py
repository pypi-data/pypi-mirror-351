from typing import Callable, Literal, Optional, TypeVar, Union

from rocrate.model.dataset import Dataset as ROCrateDataset
from rocrate.model.file import File as ROCrateFile
from rocrate.rocrate import ROCrate

from ..utils import logging
from ..utils.utils import get_study_root_path

print = logging.invalidPrint
logger = logging.getLogger()


class ObservableDict:
    def __init__(self, data: dict, callback=callable) -> None:
        """Proxy RO-Crate metadata dictionary to trigger a callback (e.g. write json) on changes."""
        self._data = data
        self._callback = callback

    def __getattr__(self, key):
        return getattr(self._data, key)

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value) -> None:
        self._data[key] = value
        self._callback()

    def __delitem__(self, key) -> None:
        del self._data[key]
        self._callback()

    def clear(self) -> None:
        self._data.clear()
        self._callback()

    def update(self, data) -> None:
        deleted_keys = set(self._data.keys()) - set(data.keys())

        for key in deleted_keys:
            del self._data[key]

        self._data.update(data)
        self._callback()

    def replace(self, data) -> None:
        """Replace the dictionary with a new one."""
        self._data.clear()
        self._data.update(data)
        self._callback()

    def pop(self, key):
        value = self._data.pop(key)
        self._callback()
        return value

    def items(self):
        return self._data.items()

    def __repr__(self) -> str:
        return repr(self._data)

    def __eq__(self, other):
        return self._data == other


class ROCrateProxy:
    def __init__(self) -> None:
        """RO-Crate crate object proxy."""
        self._crate: Optional[ROCrate] = None

    @property
    def crate(self) -> ROCrate:
        if self._crate is not None:
            return self._crate

        try:
            self._crate = ROCrate(get_study_root_path())
        except ValueError:  # Not a valid RO-Crate: missing ro-crate-metadata.json
            self._crate = ROCrate()

        return self._crate

    def write_json(self) -> None:
        study_root_path = get_study_root_path()
        logger.info(f"Writing RO-Crate metadata {study_root_path}")

        not_ok = True
        while not_ok:
            try:
                self.crate.write(study_root_path)
                not_ok = False
            except FileNotFoundError as e:
                logger.error(e)
                import os

                fname = os.path.relpath(e.filename, self.crate.source)
                self.crate.delete(fname)

    def __getattr__(self, key: str):
        attr = getattr(self.crate, key)

        if key not in ["add_dataset", "add_file", "add_tree"]:
            return attr

        def exec_and_write_json(*args, **kwargs):
            result = attr(*args, **kwargs)
            self.write_json()
            return result

        return exec_and_write_json


rocrate = ROCrateProxy()


class ROCrateMetadata:
    """RO-Crate metadata."""

    def __init__(self, *args, **kwargs) -> None:
        self.unique_identifier: Optional[str] = None
        self._rocrate_type: Literal["dataset", "directory", "file"] = "file"
        self._rocrate_entity: Optional[Union[ROCrateDataset, ROCrateFile]] = None

    def get_rocrate_entity(self) -> Union[ROCrateDataset, ROCrateFile]:
        if self._rocrate_entity is None:
            self._rocrate_entity = rocrate.get(self.unique_identifier.replace("\\", "/"))

        if self._rocrate_entity is None:
            rocrate_add_method = getattr(rocrate, f"add_{self._rocrate_type}")
            self._rocrate_entity = rocrate_add_method(self.path, dest_path=self.unique_identifier)

        return self._rocrate_entity

    def get_rocrate_metadata(self) -> ObservableDict:
        return ObservableDict(self.get_rocrate_entity().properties(), rocrate.write_json)


T = TypeVar("T")


def rocrate_metadata(func: Callable[[], T]):
    """Decorator to get and save a class field as RO-Crate metadata."""

    def getter(self) -> Optional[T]:
        return self.get_rocrate_metadata().get(func.__name__, None)

    def setter(self, value: Optional[T]) -> None:
        self.get_rocrate_metadata()[func.__name__] = value

    return property(getter, setter)
