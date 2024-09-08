"""
Developed by Keagan B
ClipMaker -- db_handler.py

Database interaction utilities

"""

import sqlite3


def get_database(path: str = "./clips.db", should_wipe=False) -> sqlite3.Connection:
    """
    Create a connection to the database. If a database doesn't exist, create it.

    :param path: Path of database to create/connect to
    :param should_wipe: Should the database be wiped on app start up?
    :return: sqlite3.Connection object to database
    """
    db = sqlite3.connect(path)

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
        path TEXT,
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
        path TEXT,
        include_subdirs INTEGER CHECK (include_subdirs == 0 || include_subdirs == 1)
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

    return db
