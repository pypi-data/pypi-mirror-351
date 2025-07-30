DEFAULT_FILE_TYPES: dict[str, list[str]] = {
    "Images": [".jpg", ".jpeg", ".png", ".gif"],
    "Documents": [".pdf", ".docx", ".txt"],
    "Videos": [".mp4", ".avi"],
    "Music": [".mp3", ".wav"],
    "Others": [],
}

"""Default file type categories and their associated file extensions.

This dictionary maps human-readable category names to lists of common file
extensions that belong to each category. It is used by the Sorter class to
determine how files should be categorized and organized during sorting.

Type:
    dict[str, list[str]]

Example:
    >>> DEFAULT_FILE_TYPES["Images"]    
    ['.jpg', '.jpeg', '.png', '.gif']

Categories:
    - "Images": Common image file formats.
    - "Documents": Text and document file formats.
    - "Videos": Video file formats.
    - "Music": Audio file formats.
    - "Others": Files that do not match any of the above categories.
"""
