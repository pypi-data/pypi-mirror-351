import os
import shutil
import tempfile
import pytest
from datetime import datetime
from Sortium.sorter import Sorter


def create_temp_file(directory, name, content="sample"):
    path = os.path.join(directory, name)
    with open(path, "w") as f:
        f.write(content)
    return path


@pytest.fixture
def setup_type_sort():
    base = tempfile.mkdtemp()

    # Create mixed files
    txt = create_temp_file(base, "doc.txt")
    jpg = create_temp_file(base, "image.jpg")
    mp3 = create_temp_file(base, "music.mp3")
    unknown = create_temp_file(base, "random.xyz")

    yield {
        "base": base,
        "files": [txt, jpg, mp3, unknown],
    }

    shutil.rmtree(base)


@pytest.fixture
def setup_date_sort():
    base = tempfile.mkdtemp()

    images_dir = os.path.join(base, "Images")
    docs_dir = os.path.join(base, "Documents")
    os.makedirs(images_dir)
    os.makedirs(docs_dir)

    file1 = create_temp_file(images_dir, "photo.png")
    file2 = create_temp_file(docs_dir, "report.pdf")

    yield {
        "base": base,
        "Images": images_dir,
        "Documents": docs_dir,
        "files": [file1, file2],
    }

    shutil.rmtree(base)


def test_sort_by_type_moves_files_to_categories(setup_type_sort):
    sorter = Sorter()
    sorter.sort_by_type(setup_type_sort["base"])

    for category in ["Documents", "Images", "Music", "Others"]:
        category_path = os.path.join(setup_type_sort["base"], category)
        if os.path.exists(category_path):
            for file in os.listdir(category_path):
                assert file in ["doc.txt", "image.jpg", "music.mp3", "random.xyz"]


def test_sort_by_type_handles_invalid_path():
    sorter = Sorter()
    with pytest.raises(FileNotFoundError):
        sorter.sort_by_type("non_existent_path")


def test_sort_by_date_sorts_into_date_folders(setup_date_sort):
    sorter = Sorter()
    sorter.sort_by_date(setup_date_sort["base"], ["Images", "Documents"])

    today = datetime.now().strftime("%d-%b-%Y")
    expected_img_dir = os.path.join(setup_date_sort["Images"], today)
    expected_doc_dir = os.path.join(setup_date_sort["Documents"], today)

    assert os.path.isdir(expected_img_dir)
    assert os.path.isdir(expected_doc_dir)

    assert "photo.png" in os.listdir(expected_img_dir)
    assert "report.pdf" in os.listdir(expected_doc_dir)


def test_sort_by_date_missing_category_skips_gracefully(setup_date_sort):
    sorter = Sorter()
    # 'Videos' does not exist, should be skipped
    sorter.sort_by_date(setup_date_sort["base"], ["Videos"])


def test_sort_by_date_invalid_root_raises():
    sorter = Sorter()
    with pytest.raises(FileNotFoundError):
        sorter.sort_by_date("invalid_path", ["Images"])
