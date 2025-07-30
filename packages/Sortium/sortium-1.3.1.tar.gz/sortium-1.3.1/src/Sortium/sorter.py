import os
import shutil
from .file_utils import get_file_modified_date, get_subdirectories_names
from .config import DEFAULT_FILE_TYPES

"""
This module defines the Sorter class for organizing files within directories.

The Sorter class helps sort files based on their type (e.g., Images, Documents)
and their last modification date. It can move files into categorized folders,
further organize them by modification date, and flatten nested directories by
moving files out.
"""

# Main sorter class.


class Sorter:
    """
    Sorter class to organize files in a directory by file type and modification date.

    Attributes:
        file_types_dict (dict[str, list[str]]): A mapping of file category names (e.g., "Images", "Documents") to lists of associated file extensions (e.g., [".jpg", ".png"]). This dictionary is used to determine how files should be grouped during sorting. If not provided, the default mapping from `DEFAULT_FILE_TYPES` is used.

    Example:
        >>> file_types = {
        ...     "Images": [".jpg", ".jpeg", ".png", ".gif"],
        ...     "Documents": [".pdf", ".docx", ".txt"],
        ...     "Videos": [".mp4", ".avi"],
        ...     "Music": [".mp3", ".wav"],
        ...     "Others": []
        ... }
        >>> sorter = Sorter(file_types)
        >>> sorter.sort_by_type('/path/to/downloads')
        >>> sorter.sort_by_date('/path/to/downloads', ['Images', 'Documents'])
    """

    def __init__(self, file_types_dict: dict[str, list[str]] = DEFAULT_FILE_TYPES):
        self.file_types_dict = file_types_dict

    def __get_category(self, extension: str) -> str:
        """
        Determines the category of a file based on its extension.

        Args:
            extension (str) : The extension of the file that will be sorted.

        Returns:
            str: Category of the file based on the file_types_dict.
        """
        for category, extensions in self.file_types_dict.items():
            if extension.lower() in extensions:
                return category
        return "Others"

    def sort_by_type(self, folder_path: str, ignore_dir: list[str] = None) -> None:
        """
        Sorts files in a directory into subdirectories by file type.

        Args:
            folder_path (str): Path to the directory containing unsorted files.
            ignore_dir (list[str]): Names of subdirectories within `folder_path` that should be ignored during processing.

        Raises:
            FileNotFoundError: If the specified folder does not exist.
        """

        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"The path '{folder_path}' does not exist.")

        try:
            sub_dir_list = get_subdirectories_names(folder_path, ignore_dir)
            for sub_dir_name in sub_dir_list:
                file_path = os.path.join(folder_path, sub_dir_name)

                if os.path.isfile(file_path):
                    _, ext = os.path.splitext(sub_dir_name)
                    category = self.__get_category(ext)

                    dest_folder = os.path.join(folder_path, category)
                    os.makedirs(dest_folder, exist_ok=True)

                    try:
                        shutil.move(file_path, os.path.join(dest_folder, sub_dir_name))
                    except Exception as e:
                        print(f"Error moving file '{sub_dir_name}': {e}")
        except Exception as e:
            print(f"An error occurred while sorting by type: {e}")

    def sort_by_date(self, folder_path: str, folder_types: list[str]) -> None:
        """
        Sorts files inside specified category folders into subfolders based on their last modified date.

        Each file is moved into a subfolder named by the modification date in the format "DD-MMM-YYYY".

        Args:
            folder_path (str): Root directory path containing the category folders.
            folder_types (list[str]): List of category folder names to process (e.g., ['Images', 'Documents']).

        Raises:
            FileNotFoundError: If the root folder (`folder_path`) does not exist.

        Notes:
            - If a category folder in `folder_types` does not exist, it will be skipped with a printed message.
            - Errors during moving individual files are caught and printed but do not stop the process.
        """
        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"The folder path '{folder_path}' does not exist.")
        for folder_type in folder_types:
            sub_folder_path = os.path.join(folder_path, folder_type)
            if os.path.exists(sub_folder_path):
                try:
                    for filename in os.listdir(sub_folder_path):
                        file_path = os.path.join(sub_folder_path, filename)
                        if os.path.isfile(file_path):
                            try:
                                # Get modified date and format it
                                modified = get_file_modified_date(file_path)
                                date_folder = modified.strftime("%d-%b-%Y")

                                # Create a subfolder for the date and move the file
                                dest_folder = os.path.join(sub_folder_path, date_folder)
                                os.makedirs(dest_folder, exist_ok=True)
                                shutil.move(
                                    file_path, os.path.join(dest_folder, filename)
                                )
                            except Exception as e:
                                print(f"Error sorting file '{filename}' by date: {e}")
                except Exception as e:
                    print(
                        f"An error occurred while processing folder '{sub_folder_path}': {e}"
                    )
            else:
                print(f"Sub-folder '{sub_folder_path}' not found, skipping.")
