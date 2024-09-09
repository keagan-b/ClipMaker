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
        db.execute("DROP TABLE IF EXISTS tags")
        db.execute("DROP TABLE IF EXISTS clips")
        db.execute("DROP TABLE IF EXISTS clip_to_tags")
        db.execute("DROP TABLE IF EXISTS clip_folders")
        db.execute("DROP TABLE IF EXISTS clip_folder_to_clips")

    db.execute("""
    CREATE TABLE IF NOT EXISTS tags
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tag_name TEXT 
    );
    """)

    db.execute("""
    CREATE TABLE IF NOT EXISTS clips
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT UNIQUE,
        custom_name TEXT,
        is_favorite INTEGER DEFAULT 0 CHECK(is_favorite == 0 || is_favorite == 1),
        is_hidden INTEGER DEFAULT 0 CHECK (is_hidden == 0 || is_hidden == 1),
        trimmed_start INTEGER DEFAULT -1,
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


def add_dir(path, should_commit: bool = False) -> models.ClipFolder:
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

    if should_commit:
        DB_OBJ.commit()

    return models.ClipFolder(path=path, db_id=db_id)


def remove_folder(obj: models.ClipFolder) -> None:
    """
    Removes a clip folder and it's children from the database
    :param obj: The folder object to remove
    :return:
    """
    cursor = DB_OBJ.cursor()
    # get list of clips
    clip_ids = cursor.execute("SELECT clip_id FROM clip_folder_to_clips WHERE clip_folder_id = ?;", (obj.db_id,)).fetchall()

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


def add_clip(clip_folder: int, path: str, should_commit: bool = False) -> models.Clip:
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

    if should_commit:
        DB_OBJ.commit()

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

        # get tags

        return clip
    else:
        return None


def build_clip_obj(data: list) -> models.Clip:
    """
    Utility function that creates a clip object from a data array
    :param data: Data to build clip from
    :return: Built clip object
    """
    return models.Clip(
        db_id=data[0],
        path=data[1],
        custom_name=data[2],
        is_favorite=bool(data[3]),
        is_hidden=bool(data[4]),
        trimmed_start=data[5],
        trimmed_end=data[6]
    )


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
