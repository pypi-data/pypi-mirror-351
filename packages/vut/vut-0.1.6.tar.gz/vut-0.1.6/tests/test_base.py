import os
import tempfile
from pathlib import Path

import pytest

from vut.base import Base


@pytest.fixture
def class_mapping_file():
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as f:
        f.write("index,class\n0,cat\n1,dog\n2,bird\n")
        file_path = f.name
    yield file_path
    os.remove(file_path)


@pytest.fixture
def action_mapping_file():
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as f:
        f.write("0,walk run jump\n1,sit down stay\n2,eat drink\n")
        file_path = f.name
    yield file_path
    os.remove(file_path)


@pytest.fixture
def video_action_mapping_file():
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as f:
        f.write("video1,action1\nvideo2,action2\nvideo3,action1\n")
        file_path = f.name
    yield file_path
    os.remove(file_path)


@pytest.fixture
def video_boundary_dir():
    temp_dir = tempfile.mkdtemp()

    with open(Path(temp_dir) / "video1.csv", "w") as f:
        f.write("0,100\n101,200\n")

    with open(Path(temp_dir) / "video2.csv", "w") as f:
        f.write("0,150\n151,300\n")

    yield temp_dir

    for file in Path(temp_dir).iterdir():
        file.unlink()
    os.rmdir(temp_dir)


def test_base(
    class_mapping_file,
    action_mapping_file,
    video_action_mapping_file,
    video_boundary_dir,
):
    backgrounds = ["bg1", "bg2"]

    base = Base(
        class_mapping_path=class_mapping_file,
        class_mapping_has_header=True,
        action_mapping_path=action_mapping_file,
        video_action_mapping_path=video_action_mapping_file,
        video_boundary_dir_path=video_boundary_dir,
        backgrounds=backgrounds,
    )

    assert base.text_to_index == {"cat": 0, "dog": 1, "bird": 2}
    assert base.index_to_text == {0: "cat", 1: "dog", 2: "bird"}

    expected_action_to_steps = {
        "0": ["walk", "run", "jump"],
        "1": ["sit", "down", "stay"],
        "2": ["eat", "drink"],
    }
    assert base.action_to_steps == expected_action_to_steps

    expected_video_to_action = {
        "video1": "action1",
        "video2": "action2",
        "video3": "action1",
    }
    assert base.video_to_action == expected_video_to_action

    expected_video_boundaries = {
        "video1": [(0, 100), (101, 200)],
        "video2": [(0, 150), (151, 300)],
    }
    assert base.video_boundaries == expected_video_boundaries

    assert base.backgrounds == backgrounds


def test_base__env_access():
    base = Base()

    os.environ["TEST_VAR"] = "test_value"
    os.environ["TEST_BOOL"] = "true"
    os.environ["TEST_INT"] = "42"
    os.environ["TEST_FLOAT"] = "3.14"

    try:
        assert base.env("TEST_VAR") == "test_value"
        assert base.env("NON_EXISTENT") == ""

        assert base.env.bool("TEST_BOOL") is True
        assert base.env.bool("NON_EXISTENT") is False

        assert base.env.int("TEST_INT") == 42
        assert base.env.int("NON_EXISTENT") == 0

        assert base.env.float("TEST_FLOAT") == 3.14
        assert base.env.float("NON_EXISTENT") == 0.0
    finally:
        for key in ["TEST_VAR", "TEST_BOOL", "TEST_INT", "TEST_FLOAT"]:
            if key in os.environ:
                del os.environ[key]


def test_base__init_with_custom_separator():
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as f:
        f.write("0|cat\n1|dog\n2|bird\n")
        file_path = f.name

    try:
        base = Base(class_mapping_path=file_path, class_mapping_separator="|")

        expected_text_to_index = {"cat": 0, "dog": 1, "bird": 2}
        expected_index_to_text = {0: "cat", 1: "dog", 2: "bird"}

        assert base.text_to_index == expected_text_to_index
        assert base.index_to_text == expected_index_to_text
    finally:
        os.remove(file_path)
