"""
Developed by Keagan B
ClipMaker -- models.py

All class objects used in the application

"""


class ClipFolder:
    """
    Keeps track of folders where clips are located.
    """
    def __init__(self):
        self.db_id = None
        self.path = ""
        self.include_subdirs = False
        self.clips: list[Clip] = []


class Clip:
    """
    Handles individual clip items. Allows the assigning of custom names/tags & marking favorites.

    Also keeps track of "trimmed" clips for mass exporting
    """
    def __init__(self):
        self.db_id = None
        self.path = ""
        self.tags: list[Tag] = []
        self.favorite = False

        self.custom_name = ""
        self.is_hidden = False

        self.trimmed_start = -1
        self.trimmed_end = -1

    def export(self):
        pass


class Tag:
    """
    Tag object that contains a name and database id for better sorting/filtering.
    """
    def __init__(self):
        self.db_id = None
        self.name = ""
