"""
Developed by Keagan B
ClipMaker -- db_handler.py

Database interaction utilities

"""
from __future__ import annotations

import sqlite3
import models

DB_OBJ: sqlite3.Connection | None = None


def get_database(path: str = "./clips.db", should_wipe=False) -> sqlite3.Connection:
    """
    Create a connection to the database. If a database doesn't exist, create it.

    :param path: Path of database to create/connect to
    :param should_wipe: Should the database be wiped on app start up?
    :return: sqlite3.Connection object to database
    """
    global DB_OBJ

    # check if a database has already been established
    if DB_OBJ is None:
        db = sqlite3.connect(path)
    else:
        db = DB_OBJ

    if should_wipe:
        # drop all tables to wipe DB
        db.execute("DROP TABLE IF EXISTS tag_sections")
        db.execute("DROP TABLE IF EXISTS tags")
        db.execute("DROP TABLE IF EXISTS tag_section_to_tags")
        db.execute("DROP TABLE IF EXISTS clips")
        db.execute("DROP TABLE IF EXISTS clip_to_tags")
        db.execute("DROP TABLE IF EXISTS clip_folders")
        db.execute("DROP TABLE IF EXISTS clip_folder_to_clips")

    db.execute("""
    CREATE TABLE IF NOT EXISTS tag_sections
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        section_name TEXT UNIQUE
    );
    """)

    db.execute("""
    CREATE TABLE IF NOT EXISTS tags
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tag_name TEXT 
    );
    """)

    db.execute("""
    CREATE TABLE IF NOT EXISTS tag_section_to_tags
    (
        section_id INTEGER NOT NULL,
        tag_id INTEGER NOT NULL,
        FOREIGN KEY (section_id) REFERENCES tag_sections(id),
        FOREIGN KEY (tag_id) REFERENCES tags(id)
    )
    """)

    db.execute("""
    CREATE TABLE IF NOT EXISTS clips
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT UNIQUE,
        custom_name TEXT,
        is_favorite INTEGER DEFAULT 0 CHECK(is_favorite == 0 || is_favorite == 1),
        is_hidden INTEGER DEFAULT 0 CHECK (is_hidden == 0 || is_hidden == 1),
        trimmed_start INTEGER DEFAULT 0,
        trimmed_end INTEGER default -1
    );
    """)

    db.execute("""
    CREATE TABLE IF NOT EXISTS clip_to_tags
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        clip_id INTEGER NOT NULL,
        tag_id INTEGER NOT NULL,
        FOREIGN KEY (clip_id) REFERENCES clips(id),
        FOREIGN KEY (tag_id) REFERENCES tags(id)
    )
    """)

    db.execute("""
    CREATE TABLE IF NOT EXISTS clip_folders
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT UNIQUE,
        include_subdirs INTEGER DEFAULT 0 CHECK (include_subdirs == 0 || include_subdirs == 1)
    );
    """)

    db.execute("""
    CREATE TABLE IF NOT EXISTS clip_folder_to_clips
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        clip_folder_id INTEGER,
        clip_id INTEGER,
        FOREIGN KEY (clip_folder_id) REFERENCES clip_folders(id),
        FOREIGN KEY (clip_id) REFERENCES clips(id)
    );
    """)

    db.commit()

    DB_OBJ = db

    return db


def does_dir_exist(path) -> int | None:
    """
    Check if a directory exists in the database
    :param path: Path of the directory to check
    :return: DB ID of directory object, or None if it does not exist
    """
    cursor = DB_OBJ.cursor()
    data = cursor.execute("SELECT id FROM clip_folders WHERE path=?", (path,)).fetchone()
    cursor.close()

    # return the id of the directory
    if data is not None:
        return data[0]
    else:
        # no directory found, return nothing
        return None


def add_dir(path) -> models.ClipFolder:
    """
    Add a new directory to the database
    :param path: Path of the directory to add
    :param should_commit:  Should the function immediately commit?
    :return: ClipFolder object representing the new directory
    """
    # add directory to database with default values
    cursor = DB_OBJ.cursor()
    cursor.execute("INSERT INTO clip_folders (path) VALUES (?);", (path,))

    # pull id from database
    db_id = cursor.execute("SELECT last_insert_rowid();").fetchone()[0]
    cursor.close()

    return models.ClipFolder(path=path, db_id=db_id)


def remove_folder(obj: models.ClipFolder) -> None:
    """
    Removes a clip folder and it's children from the database
    :param obj: The folder object to remove
    :return:
    """
    cursor = DB_OBJ.cursor()
    # get list of clips
    clip_ids = cursor.execute("SELECT clip_id FROM clip_folder_to_clips WHERE clip_folder_id = ?;",
                              (obj.db_id,)).fetchall()

    # remove clips from database
    for clip_id in clip_ids:
        clip_id = clip_id[0]
        cursor.execute("DELETE FROM clips WHERE id = ?;", (clip_id,))
        cursor.execute("DELETE FROM clip_to_tags WHERE clip_id - ?;", (clip_id,))
        cursor.execute("DELETE FROM clip_folder_to_clips WHERE clip_id = ?;", (clip_id,))

    # remove clip folder
    cursor.execute("DELETE FROM clip_folders WHERE id = ?;", (obj.db_id,))

    cursor.close()

    DB_OBJ.commit()


def get_clip_folders() -> list[models.ClipFolder]:
    """
    :return: All clip folder objects from the database
    """
    cursor = DB_OBJ.cursor()
    data = cursor.execute("SELECT * FROM clip_folders").fetchall()
    cursor.close()

    clip_folders = []

    # create clip folder objects from data
    for i in data:
        clip_folders.append(build_clip_folder_obj(i))

    return clip_folders


def does_clip_exist(path: str) -> int | None:
    """
    Check if a clip exists in the database
    :param path: Path of the clip to check
    :return: True if clip exists in database, False if not
    """
    cursor = DB_OBJ.cursor()
    data = cursor.execute("SELECT id FROM clips WHERE path=?", (path,)).fetchone()
    cursor.close()

    # return the id of the directory
    if data is not None:
        return data[0]
    else:
        # no directory found, return nothing
        return None


def add_clip(clip_folder: int, path: str) -> models.Clip:
    """
    Adds a new clip to the database
    :param clip_folder: Database ID of the clip's parent
    :param path: Path of the new clip to add
    :param should_commit: Should the function immediately commit?
    :return: Clip object representing the new clip
    """
    # add clip to database with default values
    cursor = DB_OBJ.cursor()
    cursor.execute("INSERT INTO clips (path) VALUES (?)", (path,))

    # pull id from database
    db_id = cursor.execute("SELECT last_insert_rowid();").fetchone()[0]

    # add clip & folder relationship
    cursor.execute("INSERT INTO clip_folder_to_clips (clip_folder_id, clip_id) VALUES (?, ?)", (clip_folder, db_id))
    cursor.close()

    return models.Clip(path=path, db_id=db_id)


def get_clip_from_id(db_id: int) -> models.Clip | None:
    """
    Finds a clip in the database using an ID
    :param db_id: The ID of the Clip to find
    :return: A Clip object, or None if no clip was found
    """
    cursor = DB_OBJ.cursor()
    data = cursor.execute("SELECT * FROM clips WHERE id = ?", (db_id,)).fetchone()
    cursor.close()

    if data is not None:
        clip = build_clip_obj(data)
        return clip
    else:
        return None


def update_clip(clip: models.Clip) -> None:
    """
    Save a changes made to a clip object
    :param clip: Clip object to save
    :return:
    """

    cursor = DB_OBJ.cursor()
    cursor.execute("""
    UPDATE clips SET
    path = ?,
    custom_name = ?,
    is_favorite = ?,
    is_hidden = ?,
    trimmed_start = ?,
    trimmed_end = ?
    WHERE id = ?
    """,
                   (clip.path, clip.custom_name,
                    int(clip.is_favorite), int(clip.is_hidden),
                    clip.trimmed_start, clip.trimmed_end,
                    clip.db_id))
    cursor.close()


def create_tag_section(section_name: str) -> models.TagSection:
    """
    Creates a new tag section
    :param section_name: Name of the new tag section
    :return:
    """
    cursor = DB_OBJ.cursor()
    cursor.execute("INSERT INTO tag_sections (section_name) VALUES (?);", (section_name,))

    # grab database ID
    db_id = cursor.execute("SELECT last_insert_rowid();").fetchone()[0]
    cursor.close()

    return models.TagSection(db_id, section_name)


def delete_tag_section(db_id: int) -> None:
    cursor = DB_OBJ.cursor()
    # get all tags associated to this section
    tags = cursor.execute("SELECT tag_id FROM tag_section_to_tags WHERE section_id = ?;", (db_id,)).fetchall()

    for tag in tags:
        # delete tag
        delete_tag(tag[0])

    # delete this tag section
    cursor.execute("DELETE FROM tag_sections WHERE id = ?;", (db_id,))
    cursor.close()


def get_tags_in_section(section_id: int) -> list[models.Tag]:
    """
    Returns a list of Tag containing each tag in a section
    :param section_id: Section to get tags from
    :return:
    """
    cursor = DB_OBJ.cursor()
    data = cursor.execute("SELECT tag_id FROM tag_section_to_tags WHERE section_id = ?;", (section_id,)).fetchall()

    tags = []

    # build tags and append to list
    for tag in data:
        tag_data = cursor.execute("SELECT * FROM tags WHERE id = ?;", (tag[0],)).fetchone()
        tags.append(build_tag_obj(tag_data))

    cursor.close()

    return tags


def create_tag(tag_section: int, tag_name: str) -> models.Tag:
    """
    Creates a new tag object
    :param tag_section: The section ID that this tag belongs to
    :param tag_name: Name of the new tag
    :return:
    """
    cursor = DB_OBJ.cursor()
    cursor.execute("INSERT INTO tags (tag_name) VALUES (?);", (tag_name,))

    # grab database ID
    db_id = cursor.execute("SELECT last_insert_rowid();").fetchone()[0]

    # add to relationship table
    cursor.execute("INSERT INTO tag_section_to_tags (section_id, tag_id) VALUES (?, ?)", (tag_section, db_id))

    cursor.close()

    return models.Tag(db_id, tag_name)


def delete_tag(db_id: int) -> None:
    """
    Deletes a tag from the database
    :param db_id:  The ID of the tag to delete
    :return:
    """
    cursor = DB_OBJ.cursor()
    # delete tag data
    cursor.execute("DELETE FROM tags WHERE id = ?;", (db_id,))
    # delete relationship to clips
    cursor.execute("DELETE FROM clip_to_tags WHERE tag_id = ?;", (db_id,))
    # delete relationship to tag section
    cursor.execute("DELETE FROM tag_section_to_tags WHERE tag_id = ?;", (db_id,))
    cursor.close()


def add_tag(clip_id: int, tag_id: int) -> None:
    """
    Add a tag to a clip
    :param clip_id: ID of clip
    :param tag_id: ID of tag
    :return:
    """
    cursor = DB_OBJ.cursor()
    cursor.execute("INSERT INTO clip_to_tags (clip_id, tag_id) VALUES (?, ?)", (clip_id, tag_id))
    cursor.close()


def remove_tag(clip_id: int, tag_id: int) -> None:
    """
    Remove a tag from a clip
    :param clip_id: ID of clip
    :param tag_id: ID of tag
    :return:
    """
    cursor = DB_OBJ.cursor()
    cursor.execute("DELETE FROM clip_to_tags WHERE clip_id = ? AND tag_id = ?;", (clip_id, tag_id))
    cursor.close()


def get_tag(db_id: int) -> models.Tag | None:
    """
    Get a tag based on it's database ID
    :param db_id: ID of the tag
    :return: Tag object, or None if the tag does not exist
    """
    cursor = DB_OBJ.cursor()
    data = cursor.execute("SELECT * FROM tags WHERE id = ?", (db_id,)).fetchone()
    cursor.close()

    if data is not None:
        return build_tag_obj(data)
    else:
        return None


def get_tag_owner_section(tag_id: int) -> models.TagSection | None:
    """
    Get a section based on a tag's id
    :param tag_id: ID of the tag
    :return: Section object that owns the tag, or None if no section is found
    """
    cursor = DB_OBJ.cursor()
    section_id = cursor.execute("SELECT section_id FROM tag_section_to_tags WHERE tag_id = ?", (tag_id,)).fetchone()
    data = cursor.execute("SELECT * FROM tag_sections WHERE id = ?", (section_id[0],)).fetchone()
    cursor.close()

    if data is not None:
        return build_tag_section_obj(data)
    else:
        return None


def get_all_tags() -> list[models.TagSection]:
    """
    Find all tags and tag sections
    :return: A list of TagSection with a populated Tag list
    """
    cursor = DB_OBJ.cursor()
    data = cursor.execute("SELECT * FROM tag_sections").fetchall()

    tag_sections: list[models.TagSection] = []
    for tag_section in data:
        # build tag sections
        tag_section = build_tag_section_obj(tag_section)

        # get tags in tag section
        tag_section.tags.extend(get_tags_in_section(tag_section.db_id))

        # add tag section to list
        tag_sections.append(tag_section)

    return tag_sections


def get_tags_on_clip(clip_id: int) -> list[models.Tag]:
    """
    Get all of the tags on a clip
    :param clip_id: the ID of the clip to get tags for
    :return: List of Tag objects
    """
    cursor = DB_OBJ.cursor()
    # get all tag IDs attached to this clip
    tag_ids = cursor.execute("SELECT * FROM clip_to_tags WHERE clip_id = ?", (clip_id,)).fetchall()

    tags = []
    for tag in tag_ids:
        # Get tag info from tag ids & add to the list
        data = cursor.execute("SELECT * FROM tags WHERE id = ?", (tag[2],)).fetchone()
        tags.append(build_tag_obj(data))

    cursor.close()

    return tags


def has_tag(clip_id: int, tag_id: int) -> bool:
    """
    Checks if a tag is present on a clip
    :param clip_id: Clip ID to check
    :param tag_id: Tag ID to check
    :return: True if the tag is on the clip, False if the tag is not on the clip.
    """
    cursor = DB_OBJ.cursor()
    data = cursor.execute("SELECT * FROM clip_to_tags WHERE clip_id = ? AND tag_id = ?", (clip_id, tag_id)).fetchone()
    cursor.close()

    if data is not None:
        return True
    else:
        return False


def build_clip_obj(data: list) -> models.Clip:
    """
    Utility function that creates a clip object from a data array
    :param data: Data to build clip from
    :return: Built clip object
    """
    clip = models.Clip(
        db_id=data[0],
        path=data[1],
        custom_name=data[2],
        is_favorite=bool(data[3]),
        is_hidden=bool(data[4]),
        trimmed_start=data[5],
        trimmed_end=data[6]
    )

    # get all the tag objects on this clip
    clip.tags.extend(get_tags_on_clip(clip.db_id))

    return clip


def build_clip_folder_obj(data: list) -> models.ClipFolder:
    """
    Utility function that creates a clip folder object from a data array
    :param data: Data to build clip folder from
    :return: Built clip folder object
    """
    return models.ClipFolder(
        db_id=data[0],
        path=data[1],
        include_subdirs=bool(data[2])
    )


def build_tag_obj(data: list) -> models.Tag:
    """
    Utility function that creates a tag object from a data array
    :param data: Data to build tag from
    :return: Built tag object
    """

    return models.Tag(
        db_id=data[0],
        name=data[1]
    )


def build_tag_section_obj(data: list) -> models.TagSection:
    """
    Utility function that creates a tag section object from a data array
    :param data: Data to build tag section from
    :return: Built tag section object
    """

    return models.TagSection(
        db_id=data[0],
        section_name=data[1]
    )
