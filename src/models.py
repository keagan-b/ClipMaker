"""
Developed by Keagan B
ClipMaker -- models.py

All class objects used in the application

"""
import os


class ClipFolder:
    """
    Keeps track of folders where clips are located.
    """

    def __init__(self, db_id: int, path: str, include_subdirs: bool = False):
        self.db_id = db_id
        self.path = path
        self.include_subdirs = include_subdirs

        self.clips: list[Clip] = []

    def get_dir_name(self) -> str:
        """
        :return: The name of this directory
        """
        return os.path.dirname(self.path)


class Clip:
    """
    Handles individual clip items. Allows the assigning of custom names/tags & marking favorites.

    Also keeps track of "trimmed" clips for mass exporting
    """

    def __init__(self, db_id: int, path: str, custom_name: str = "", is_favorite: bool = False, is_hidden: bool = False, trimmed_start: int = -1, trimmed_end: int = -1):
        self.db_id = db_id
        self.path = path

        self.custom_name = custom_name
        self.is_favorite = is_favorite
        self.is_hidden = is_hidden

        self.trimmed_start = trimmed_start
        self.trimmed_end = trimmed_end

        self.tags: list[Tag] = []

    def get_clip_name(self) -> str:
        """
        :return: The custom name of this clip if set, or the file name
        """
        if self.custom_name == "" or self.custom_name is None:
            # return path name if no custom name is set
            return os.path.basename(self.path)
        else:
            # otherwise return the custom name
            return self.custom_name

    def export(self):
        pass


class TagSection:
    """
    A tag "section" - a grouping of tags that share some similar quality.
    Used in the Tag adder/remover
    """
    def __init__(self, db_id: int, section_name: str):
        self.db_id = db_id
        self.section_name = section_name

        self.tags: list[Tag] = []


class Tag:
    """
    Tag object that contains a name and database id for better sorting/filtering.
    """

    def __init__(self, db_id: int, name: str):
        self.db_id = db_id
        self.name = name
