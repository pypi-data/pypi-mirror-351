import json
import os
import shutil

import pytest
import utils

import solidipes as sp
from solidipes.utils.utils import get_study_root_path

# Imported fixtures
# - study_dir


@pytest.fixture
def text_file(study_dir):
    asset_path = utils.get_asset_path("text.txt")
    file_path = study_dir / "data" / "text.txt"

    os.makedirs(file_path.parent, exist_ok=True)
    shutil.copy(asset_path, file_path)
    return sp.load_file(str(file_path))


def test_get_metadata(text_file) -> None:
    metadata = text_file.get_rocrate_metadata()
    expected_metadata = {
        "@id": "data/text.txt",
        "@type": "File",
    }
    assert metadata == expected_metadata

    # Check written json
    root_path = get_study_root_path()
    rocrate_metadata_path = os.path.join(root_path, "ro-crate-metadata.json")
    assert os.path.exists(rocrate_metadata_path)

    with open(rocrate_metadata_path, "r") as f:
        written_metadata = json.load(f)
    assert "@graph" in written_metadata
    assert expected_metadata in written_metadata["@graph"]


def test_metadata_modification(text_file) -> None:
    metadata = text_file.get_rocrate_metadata()
    metadata["hello"] = "world"
    expected_metadata = {
        "@id": "data/text.txt",
        "@type": "File",
        "hello": "world",
    }
    assert metadata == expected_metadata

    # Check written json
    root_path = get_study_root_path()
    rocrate_metadata_path = os.path.join(root_path, "ro-crate-metadata.json")
    with open(rocrate_metadata_path, "r") as f:
        written_metadata = json.load(f)
    assert expected_metadata in written_metadata["@graph"]

    # Check reloading the file
    text_file = sp.load_file("data/text.txt")
    metadata = text_file.get_rocrate_metadata()
    assert metadata == expected_metadata
