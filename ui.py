"""

Developed by Keagan B
ClipMaker -- ui.py


All UI is created in this script.

Each window is defined as its own function, and is placed on the UI stack through change_active_frame
"""

# type hinting enabling
from __future__ import annotations

import os
from media_player import MediaPlayer, MediaSlider
from tkinter import filedialog, ttk
import tkinter as tk
from tkinter import ttk
import db_handler

from models import *

ROOT: tk.Tk | None = None
ACTIVE_FRAME = (None, None)
PREVIOUS_FRAMES = []

# current clip information
CLIP_FOLDERS: list[ClipFolder] = []
CURRENT_CLIP: Clip | None = None
MEDIA_PLAYER: MediaPlayer | None = None

VIDEO_SCALE = 1
VIDEO_WIDTH = 15 * VIDEO_SCALE
VIDEO_HEIGHT = 10 * VIDEO_SCALE

TREE_MENU: tk.Menu | None = None

VIDEO_EXTENSIONS: list[str] = []


def create_ui() -> tk.Tk:
    """
    Creates the base UI for the app
    """
    global ROOT, MEDIA_PLAYER

    # create new root
    root = tk.Tk()

    # set global root value
    ROOT = root

    # set title
    root.title("ClipMaker")

    # == create UI elements ==

    # - clip list frame -
    clip_list_frame = tk.Frame(root)

    clip_tree = ttk.Treeview(clip_list_frame, selectmode="browse")
    export_all_btn = tk.Button(clip_list_frame, text="Export All")

    # bind clip tree variable, so it can be used in other functions
    root.clip_tree = clip_tree

    # - playback frame -
    MEDIA_PLAYER = MediaPlayer(root, VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_SCALE)

    #  - media control frame -
    media_control_frame = tk.Frame(root)

    # media control buttons
    skip_back_btn = tk.Button(media_control_frame, text="<--", command=lambda: MEDIA_PLAYER.skip(-15000))
    skip_forward_btn = tk.Button(media_control_frame, text="-->", command=lambda: MEDIA_PLAYER.skip(15000))

    media_slider = MediaSlider(media_control_frame, to=1000, command=MEDIA_PLAYER.move_slider)

    # bind media slider variable to be accessed from the Media Player
    root.media_slider = media_slider

    media_timer = tk.Label(media_control_frame, text="00:00")
    # bind media timer variable to be access from the Media Player
    root.media_timer = media_timer

    previous_btn = tk.Button(media_control_frame, text="Previous")
    next_btn = tk.Button(media_control_frame, text="Next")

    play_btn = tk.Button(media_control_frame, text="⏸", command=lambda: MEDIA_PLAYER.change_play_state())

    # bind play_btn to a variable to be accessed from the Media Player
    root.play_btn = play_btn

    start_label = tk.Label(media_control_frame, text="Start: ")
    start_entry = tk.Entry(media_control_frame)

    end_label = tk.Label(media_control_frame, text="End:")
    end_entry = tk.Entry(media_control_frame)

    # - clip info frame -
    clip_info_frame = tk.Frame(root)

    name_label = tk.Label(clip_info_frame, text="Name:")
    name_variable = tk.StringVar()
    name_entry = tk.Entry(clip_info_frame, textvariable=name_variable)

    # bind name entry to root
    root.name_variable = name_variable

    path_label = tk.Label(clip_info_frame, text="Path:")
    path_variable = tk.StringVar()
    path_entry = tk.Entry(clip_info_frame, state=tk.DISABLED, textvariable=path_variable)

    # bind path entry to root
    root.path_variable = path_variable

    duration_label = tk.Label(clip_info_frame, text="Length:")
    duration_variable = tk.StringVar()
    duration_entry = tk.Entry(clip_info_frame, state=tk.DISABLED, textvariable=duration_variable)

    # bind duration entry to root
    root.duration_variable = duration_variable

    favorite_label = tk.Label(clip_info_frame, text="Favorite: ")
    favorite_box = tk.Checkbutton(clip_info_frame)

    # bind favorite box to root
    root.favorite_box = favorite_box

    tags_label = tk.Label(clip_info_frame, text="Tags")
    tags_list = tk.Listbox(clip_info_frame)

    tag_add_btn = tk.Button(clip_info_frame, text="Add Tag")
    tag_remove_btn = tk.Button(clip_info_frame, text="Remove Tag")

    # == place elements on frames ==

    # create root grid
    root.grid()

    # set root grid columns
    for i in range(3 + VIDEO_HEIGHT):
        root.columnconfigure(i, weight=1)

    # set root grid rows
    for i in range(10 + VIDEO_WIDTH):
        root.rowconfigure(i, weight=1)

    # - clip list frame -
    clip_list_frame.grid(row=0, column=0, sticky="W", padx=10, pady=10)

    # set clip list frame grid columns
    for i in range(5):
        clip_list_frame.columnconfigure(i, weight=1)

    # set clip list frame grid rows
    for i in range(12):
        clip_list_frame.rowconfigure(i, weight=1)

    clip_tree.grid(row=0, column=0, rowspan=12, columnspan=5)

    export_all_btn.grid(row=12, column=0, columnspan=3, sticky="S")

    # - media control frame -
    media_control_frame.grid(row=VIDEO_HEIGHT, column=5, sticky="WSE", padx=10, pady=10)

    # set media control frame grid columns
    for i in range(15):
        media_control_frame.columnconfigure(i, weight=1)

    # set media control frame grid rows
    for i in range(3):
        media_control_frame.rowconfigure(i, weight=1)

    skip_back_btn.grid(row=0, column=1)
    skip_forward_btn.grid(row=0, column=13)

    media_slider.grid(row=0, column=2, columnspan=9, sticky="EW")

    media_timer.grid(row=0, column=11, columnspan=2)

    previous_btn.grid(row=1, column=2, columnspan=2)
    play_btn.grid(row=1, column=7)
    next_btn.grid(row=1, column=11, columnspan=2)

    start_label.grid(row=3, column=3, columnspan=2)
    start_entry.grid(row=3, column=5, columnspan=2)

    end_label.grid(row=3, column=8, columnspan=2)
    end_entry.grid(row=3, column=10, columnspan=2)

    # - clip info frame -
    clip_info_frame.grid(row=0, column=5 + VIDEO_WIDTH, sticky="E", padx=10, pady=10)

    # set clip info frame grid columns
    for i in range(5):
        clip_info_frame.columnconfigure(i, weight=1)

    # set clip list frame grid rows
    for i in range(13):
        clip_info_frame.rowconfigure(i, weight=1)

    name_label.grid(row=0, column=0, columnspan=2)
    name_entry.grid(row=0, column=2, columnspan=3)

    path_label.grid(row=1, column=0, columnspan=2)
    path_entry.grid(row=1, column=2, columnspan=3)

    duration_label.grid(row=2, column=0, columnspan=2)
    duration_entry.grid(row=2, column=2, columnspan=3)

    favorite_label.grid(row=3, column=0, columnspan=2)
    favorite_box.grid(row=3, column=3)

    tags_label.grid(row=4, column=0)
    tags_list.grid(row=5, column=0, rowspan=6, columnspan=5)

    tag_add_btn.grid(row=11, column=1, columnspan=3)
    tag_remove_btn.grid(row=12, column=1, columnspan=3)

    root.protocol("WM_DELETE_WINDOW", close_app)

    # create context menus

    # == Clip Tree Context ==

    # directory menu
    tree_dir_menu = tk.Menu(clip_list_frame, tearoff=0)

    tree_dir_menu.add_command(label="Add Folder", command=add_folder)
    tree_dir_menu.add_command(label="Remove Folder")
    tree_dir_menu.add_command(label="Export Folder")
    tree_dir_menu.add_separator()
    tree_dir_menu.add_command(label="Refresh Clips", command=refresh_clips)
    tree_dir_menu.add_command(label="Unhide Clips")

    root.tree_dir_menu = tree_dir_menu

    # clip menu
    tree_clip_menu = tk.Menu(clip_list_frame, tearoff=0)

    tree_clip_menu.add_command(label="Rename Clip")
    tree_clip_menu.add_command(label="Hide Clip")
    tree_clip_menu.add_command(label="Export Clip")

    root.tree_clip_menu = tree_clip_menu

    # MEDIA_PLAYER.play("./testing.webm")

    # set CLIP FOLDER info
    rescan_folders()

    # populate clip tree
    refresh_clips()

    # == bind events ==

    # bind menu events on the tree
    root.bind("<Button-3>", tree_menu_popups)

    # bind tree selection
    clip_tree.bind("<<TreeviewSelect>>", select_clip)

    return root


def tree_menu_popups(event):
    if True:
        # selected element is directory
        popup_menu: tk.Menu = ROOT.tree_dir_menu
    else:
        # selected element is clip
        popup_menu: tk.Menu = ROOT.tree_clip_menu

    try:
        popup_menu.tk_popup(event.x_root, event.y_root)
    finally:
        popup_menu.grab_release()


def add_folder():
    # get directory from user
    new_folder = filedialog.askdirectory(mustexist=True)

    # check if directory is already in database
    if db_handler.does_dir_exist(new_folder) is None:
        # add new folder to database if it doesn't exist
        db_handler.add_dir(new_folder, should_commit=True)

    # refresh the loaded clips
    rescan_folders()
    refresh_clips()


def rescan_folders() -> None:
    """
    Rescans all folders loaded into the clip maker
    :return:
    """
    global CLIP_FOLDERS

    # grab all clip folder objects
    clip_folders = db_handler.get_clip_folders()

    for clip_folder in clip_folders:
        # add clip items from folder
        for file in os.listdir(clip_folder.path):
            # loop through valid extensions
            for extension in VIDEO_EXTENSIONS:
                # check if path is a video file
                if file.endswith(f".{extension}"):
                    # create a full path object
                    path = os.path.join(clip_folder.path, file)

                    # ensure clip doesn't already exist in database
                    clip = db_handler.does_clip_exist(path)
                    if clip is None:
                        # add clip to database
                        clip = db_handler.add_clip(clip_folder=clip_folder.db_id, path=path)
                    else:
                        # grab clip object from database
                        clip = db_handler.get_clip_from_id(clip)

                    # add clip to clip folder list
                    clip_folder.clips.append(clip)

                    # move on to next clip
                    break

    # commit any updates
    db_handler.DB_OBJ.commit()

    # set global clip folders
    CLIP_FOLDERS = clip_folders


def refresh_clips() -> None:
    """
    Refresh the clip tree with info from CLIP_FOLDERS
    :return:
    """
    for clip_folder in CLIP_FOLDERS:
        folder_obj = ROOT.clip_tree.insert("", tk.END, text=clip_folder.get_dir_name(), iid=f"D-{clip_folder.db_id}")

        for clip in clip_folder.clips:
            ROOT.clip_tree.insert(folder_obj, tk.END, text=clip.get_clip_name(), iid=f"C-{clip.db_id}")


def select_clip(_event) -> None:
    """
    Event handler for the clip tree item selection
    :param _event:
    :return:
    """
    global CURRENT_CLIP

    # find selected element
    selected: str = ROOT.clip_tree.selection()[0]

    # only handle C- events
    if selected.startswith("C-"):
        # load clip from ID
        clip = db_handler.get_clip_from_id(int(selected[2:]))

        # set global current clip
        CURRENT_CLIP = clip

        # queue clip into media player
        MEDIA_PLAYER.play(clip.path)

        # populate information fields
        ROOT.name_variable.set(clip.get_clip_name())

        ROOT.path_variable.set(clip.path)

        # duration is set in the Media Player due to technical limitations

        # ROOT.favorite_box.config()



def close_app():
    """
    Destroys the root object & closes the app
    :return:
    """
    global ROOT

    if ROOT is not None:
        ROOT.destroy()


def change_active_frame(frame: tk.Frame | ttk.Notebook = None, update_event=None) -> None:
    """
    Driver function that controls the appearance of UI elements on the stack.

    :param frame: Frame to add to stack & bring forward
    :param update_event: Event to trigger when this frame is put on the top of the stack
    :return: None.
    """
    global ACTIVE_FRAME, PREVIOUS_FRAMES

    old_frame: tk.Frame = ACTIVE_FRAME[0]

    # hide old frame
    if old_frame is not None:
        old_frame.grid_forget()

    # active the previous active frame
    if frame is None and len(PREVIOUS_FRAMES) > 0:
        ACTIVE_FRAME = PREVIOUS_FRAMES.pop(-1)
    # activate a new frame
    else:
        # ensure there is an active frame
        if ACTIVE_FRAME[0] is not None:
            # append old frame
            PREVIOUS_FRAMES.append(ACTIVE_FRAME)

        # set new frame
        ACTIVE_FRAME = (frame, update_event)

    # trigger update
    if ACTIVE_FRAME[1] is not None:
        ACTIVE_FRAME[1]()

    # show new frame
    ACTIVE_FRAME[0].grid(row=0, column=0, sticky="NEWS")
