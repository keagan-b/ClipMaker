"""
Developed by Keagan B
ClipMaker -- ui.py


All UI is created in this script.

Each window is defined as its own function, and is placed on the UI stack through change_active_frame
"""

# type hinting enabling
from __future__ import annotations

import os
from utils import get_time_from_milliseconds, get_milliseconds_from_time
from media_player import MediaPlayer, MediaSlider
from tkinter import filedialog, ttk
from functools import partial
import tkinter as tk
from tkinter import ttk
import db_handler

from models import *

ROOT: tk.Tk | None = None
ACTIVE_FRAME = (None, None)
PREVIOUS_FRAMES = []

# clip information
TAG_SECTIONS: list[TagSection] = []
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
    global ROOT, MEDIA_PLAYER, TAG_SECTIONS

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
    start_variable = tk.StringVar()
    start_entry = tk.Entry(media_control_frame, textvariable=start_variable)

    root.start_variable = start_variable

    # add callback for variable editing
    start_variable.trace_add("write", set_start_time)

    end_label = tk.Label(media_control_frame, text="End: ")
    end_variable = tk.StringVar()
    end_entry = tk.Entry(media_control_frame, textvariable=end_variable)

    root.end_variable = end_variable

    # add callback for variable editing
    end_variable.trace_add("write", set_end_time)

    # - clip info frame -
    clip_info_frame = tk.Frame(root)

    root.clip_info_frame = clip_info_frame

    name_label = tk.Label(clip_info_frame, text="Name:")
    name_variable = tk.StringVar()
    name_entry = tk.Entry(clip_info_frame, textvariable=name_variable)

    # bind name entry to root
    root.name_variable = name_variable

    # add callback for variable editing
    name_variable.trace_add("write", set_custom_name)

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
    favorite_variable = tk.BooleanVar()
    favorite_box = tk.Checkbutton(clip_info_frame, variable=favorite_variable, command=set_favorite)

    # bind favorite box to root
    root.favorite_variable = favorite_variable

    tags_label = tk.Label(clip_info_frame, text="Tags")
    tag_list = tk.Listbox(clip_info_frame)

    root.tag_list = tag_list

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
    tag_list.grid(row=5, column=0, rowspan=8, columnspan=5)

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
    tree_dir_menu.add_command(label="Unhide Clips", command=unhide_clips)

    root.tree_dir_menu = tree_dir_menu

    # clip menu
    tree_clip_menu = tk.Menu(clip_list_frame, tearoff=0)

    tree_clip_menu.add_command(label="Hide Clip", command=hide_clip)
    tree_clip_menu.add_command(label="Export Clip")

    root.tree_clip_menu = tree_clip_menu

    # gather Tags
    TAG_SECTIONS = db_handler.get_all_tags()

    # generate tag menu
    root.tag_menu = create_tags_menu()

    # set CLIP FOLDER info
    rescan_folders()

    # populate clip tree
    refresh_clips()

    # == bind events ==

    # bind menu events on the tree
    clip_tree.bind("<Button-3>", tree_menu_popups)

    # bind menu events on tag list
    tag_list.bind("<Button-3>", tags_menu_popup)

    # bind tree selection
    clip_tree.bind("<<TreeviewSelect>>", select_clip)

    # start delayed commits
    delayed_commit()

    return root


def delayed_commit():
    """
    Delays all commits to a single point in time, allowing for the app to appear to be running smoothly
    :return:
    """
    db_handler.DB_OBJ.commit()

    ROOT.after(1000, delayed_commit)


def tree_menu_popups(event):
    """
    Handles context menu events on the clip tree
    :param event: Event data passed by widget
    :return:
    """
    # get currently selected tree element
    try:
        selected: str = ROOT.clip_tree.selection()[0]
    except IndexError:
        selected = ""

    if selected.startswith("C-"):
        # selected element is clip
        popup_menu: tk.Menu = ROOT.tree_clip_menu
    else:
        # selected element is not clip, open generic directory menu
        popup_menu: tk.Menu = ROOT.tree_dir_menu

        # reset Remove/Export &  Unhide options to prepare for changes
        ROOT.tree_dir_menu.delete(1, 2)
        ROOT.tree_dir_menu.delete(tk.LAST, tk.LAST)

        if not selected.startswith("D-"):
            # disable Remove Folder, Export Folder, & Unhide Clips options
            ROOT.tree_dir_menu.insert(index=1, itemType="command", label="Remove Folder", state="disabled")
            ROOT.tree_dir_menu.insert(index=2, itemType="command", label="Export Folder", state="disabled")
            ROOT.tree_dir_menu.add(itemType="command", label="Unhide Clips", state="disabled")
        else:
            # enable Remove Folder, Export Folder, & Unhide Clips options
            ROOT.tree_dir_menu.insert(index=1, itemType="command", label="Remove Folder",
                                      state="normal", command=remove_folder)
            ROOT.tree_dir_menu.insert(index=2, itemType="command", label="Export Folder",
                                      state="normal")
            ROOT.tree_dir_menu.add(itemType="command", label="Unhide Clips",
                                   state="normal", command=unhide_clips)

    try:
        popup_menu.tk_popup(event.x_root, event.y_root)
    finally:
        popup_menu.grab_release()


def add_folder():
    """
    Add a new folder to the clip folder view
    :return:
    """
    # get directory from user
    new_folder = filedialog.askdirectory(mustexist=True)

    # make sure an empty folder wasn't specified
    if new_folder == "" or new_folder is None:
        return

    # check if directory is already in database
    if db_handler.does_dir_exist(new_folder) is None:
        # add new folder to database if it doesn't exist
        db_handler.add_dir(new_folder)

    # refresh the loaded clips
    rescan_folders()
    refresh_clips()


def remove_folder():
    """
    Delete a folder from the database & clip tree view
    :return:
    """
    global CLIP_FOLDERS, CURRENT_CLIP

    selected: str = ROOT.clip_tree.selection()[0]

    for folder in CLIP_FOLDERS:
        if folder.db_id == int(selected[2:]):
            clip_folder = folder
            break
    else:
        # no folder found, return
        return

    CLIP_FOLDERS.remove(clip_folder)

    # remove the current clip if its in this folder
    if CURRENT_CLIP in clip_folder.clips:
        CURRENT_CLIP = None

    # remove node & children from the clip tree
    ROOT.clip_tree.delete(selected)

    # remove folder & children in database
    db_handler.remove_folder(clip_folder)

    # refresh tree view
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
    # clear tree
    ROOT.clip_tree.delete(*ROOT.clip_tree.get_children())

    for clip_folder in CLIP_FOLDERS:
        folder_obj = ROOT.clip_tree.insert("", tk.END, text=clip_folder.get_dir_name(), iid=f"D-{clip_folder.db_id}")

        for clip in clip_folder.clips:
            if not clip.is_hidden:
                ROOT.clip_tree.insert(folder_obj, tk.END, text=clip.get_clip_name(), iid=f"C-{clip.db_id}")


def select_clip(_event) -> None:
    """
    Event handler for the clip tree item selection
    :param _event:
    :return:
    """
    global CURRENT_CLIP

    # find selected element
    try:
        selected: str = ROOT.clip_tree.selection()[0]
    except IndexError:
        selected = ""

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

        ROOT.favorite_variable.set(clip.is_favorite)

        # clear tag list
        ROOT.tag_list.delete(0, tk.END)

        # add tags to list
        for tag in clip.tags:
            ROOT.tag_list.insert(tk.END, tag.name)

        # set start entry
        if clip.trimmed_start != -1:
            ROOT.start_variable.set(get_time_from_milliseconds(clip.trimmed_start))
        else:
            ROOT.start_variable.set("00:00")

        # set end entry
        if clip.trimmed_end != -1:
            ROOT.end_variable.set(get_time_from_milliseconds(clip.trimmed_end))
        else:
            # tick update handles times set as "-1".
            ROOT.end_variable.set("-1")


def hide_clip() -> None:
    """
    Hides a clip selected in the clip tree
    :return:
    """
    # check that a current clip is set
    if CURRENT_CLIP is not None:
        # set new favorite status
        CURRENT_CLIP.is_hidden = True

        ROOT.clip_tree.delete(f"C-{CURRENT_CLIP.db_id}")

        # update favorite
        db_handler.update_clip(CURRENT_CLIP)


def set_favorite() -> None:
    """
    Favorites the currently selected clip
    :return:
    """
    # check that a current clip is set
    if CURRENT_CLIP is not None:
        # set new favorite status
        CURRENT_CLIP.is_favorite = ROOT.favorite_variable.get()

        # update favorite
        db_handler.update_clip(CURRENT_CLIP)


def set_custom_name(*_args) -> None:
    # check that a current clip is set
    if CURRENT_CLIP is not None:
        # get new custom name
        CURRENT_CLIP.custom_name = ROOT.name_variable.get()

        # update name
        db_handler.update_clip(CURRENT_CLIP)

        # update tree
        ROOT.clip_tree.item(f"C-{CURRENT_CLIP.db_id}", text=CURRENT_CLIP.custom_name)


def set_start_time(*_args) -> None:
    # check that a current clip is set
    if CURRENT_CLIP is not None:
        # get new start time
        try:
            CURRENT_CLIP.trimmed_start = get_milliseconds_from_time(ROOT.start_variable.get())
        except AttributeError:
            return

        # update name
        db_handler.update_clip(CURRENT_CLIP)


def set_end_time(*_args) -> None:
    # check that a current clip is set
    if CURRENT_CLIP is not None:
        # get new end time
        try:
            CURRENT_CLIP.trimmed_end = get_milliseconds_from_time(ROOT.end_variable.get())
        except AttributeError:
            return

        # update name
        db_handler.update_clip(CURRENT_CLIP)


def unhide_clips() -> None:
    """
    Unhides clips from the currently selected Clip Folder
    :return:
    """
    selected: str = ROOT.clip_tree.selection()[0]

    # find folder in objects
    for folder in CLIP_FOLDERS:
        if folder.db_id == int(selected[2:]):
            clip_folder = folder
            break
    else:
        # no folder found, return
        return

    for clip in clip_folder.clips:
        # update a clip only if it is currently hidden
        if clip.is_hidden:
            clip.is_hidden = False

            db_handler.update_clip(clip)

    # refresh UI
    refresh_clips()


def tags_menu_popup(event):
    """
    Show tag menu options
    :param event: Event data passed by widget
    :return:
    """
    # grab popup menu from reference
    popup_menu = ROOT.tag_menu

    # delete "Remove Tag"
    popup_menu.delete(tk.END, tk.END)

    # get selected tag
    selected_tag = ROOT.tag_list.get(tk.ACTIVE)

    # check if tag is in clip
    if CURRENT_CLIP is not None:
        for tag in CURRENT_CLIP.tags:
            if tag.name == selected_tag:
                break
        else:
            # no tag found
            tag = None
    else:
        # no clip, no tags
        tag = None

    # determine if tag can be removed
    if tag is not None:
        # enable tag remove button
        popup_menu.insert(index=tk.END, itemType="command", label="Remove Tag",
                          state="normal", command=remove_tag)
    else:
        # disable tag remove button
        popup_menu.insert(index=tk.END, itemType="command", label="Remove Tag", state="disabled")

    # show menu
    try:
        popup_menu.tk_popup(event.x_root, event.y_root)
    finally:
        popup_menu.grab_release()


def create_tags_menu() -> tk.Menu:
    """
    Creates a new tag context menu with updated tags & tag sections
    :return:
    """

    tag_menu = tk.Menu(ROOT.clip_info_frame, tearoff=0)

    tag_menu.add_cascade(label="Tags:")

    # loop through each Tag Section
    for section in TAG_SECTIONS:
        # create a new cascade menu for this section
        cascade_menu = tk.Menu(ROOT.clip_info_frame, tearoff=0)

        # loop through child tags
        for tag in section.tags:
            cascade_menu.add_command(label=tag.name, command=partial(add_tag, tag.db_id))

        # add cascade menu to tag context menu
        tag_menu.add_cascade(label=section.section_name, menu=cascade_menu)

    # add seperator
    tag_menu.add_separator()

    # add new tag command
    tag_menu.add_command(label="New Tag", command=create_tag_popup)
    # delete existing tag command
    tag_menu.add_command(label="Delete Tag", command=create_tag_delete_popup)

    tag_menu.add_separator()
    # add new section command
    tag_menu.add_command(label="New Section", command=create_section_popup)
    # delete existing section command
    tag_menu.add_command(label="Delete Section", command=create_section_delete_popup)

    tag_menu.add_separator()
    # add remove command
    tag_menu.add_command(label="Remove Tag")

    return tag_menu


def add_tag(tag_id: int) -> None:
    if CURRENT_CLIP is not None:
        # get tag
        tag = db_handler.get_tag(tag_id)

        # ensure tag exists
        existing_tags = [x.db_id for x in CURRENT_CLIP.tags]
        if tag is not None and tag.db_id not in existing_tags:
            # add tag to clip tag list
            CURRENT_CLIP.tags.append(tag)

            # add tag to clip
            db_handler.add_tag(CURRENT_CLIP.db_id, tag.db_id)

            # add tag to list
            ROOT.tag_list.insert(tk.END, tag.name)


def create_section_popup() -> None:
    """
    Creates a popup window that requests tag section-specific information
    :return:
    """

    popup = tk.Toplevel()

    # name information
    name_label = tk.Label(popup, text="Section Name: ")
    name_variable = tk.StringVar()
    name_entry = tk.Entry(popup, textvariable=name_variable)

    # buttons
    back_button = tk.Button(popup, text="Back", command=popup.destroy)
    save_button = tk.Button(popup, text="Save", command=lambda: create_section(name_variable, popup))

    # place on grid
    popup.grid()

    name_label.grid(row=0, column=0)
    name_entry.grid(row=0, column=1, columnspan=2)

    back_button.grid(row=1, column=0)
    save_button.grid(row=1, column=2)


def create_section(variable: tk.StringVar, popup: tk.Toplevel):
    """
    Creates a new section with specified string variable's value
    :param variable: tk.StringVar to get value from
    :param popup: window that popup originated from
    :return:
    """
    global TAG_SECTIONS
    # create new tag section and add to global variable
    TAG_SECTIONS.append(db_handler.create_tag_section(variable.get()))

    # refresh tag menu
    ROOT.tag_menu = create_tags_menu()

    # close popup
    popup.destroy()


def create_tag_popup() -> None:
    """
    Creates a popup window that requests tag-specific information
    :return:
    """

    # ensure there are valid tag sections first
    if len(TAG_SECTIONS) == 0:
        create_section_popup()
        # check to make sure a section was created
        if len(TAG_SECTIONS) == 0:
            return

    # create a set of section options
    section_options = [section.section_name for section in TAG_SECTIONS]

    popup = tk.Toplevel()

    section_label = tk.Label(popup, text="Tag Section: ")
    section_variable = tk.StringVar()
    section_variable.set(section_options[0])
    section_dropdown = tk.OptionMenu(popup, section_variable, *section_options)

    name_label = tk.Label(popup, text="Tag Name: ")
    name_variable = tk.StringVar()
    name_entry = tk.Entry(popup, textvariable=name_variable)

    # buttons
    back_button = tk.Button(popup, text="Back", command=popup.destroy)
    save_button = tk.Button(popup, text="Save", command=lambda: create_tag(section_variable, name_variable, popup))

    # place items on grid
    popup.grid()

    section_label.grid(row=0, column=0)
    section_dropdown.grid(row=0, column=1, columnspan=2)

    name_label.grid(row=1, column=0)
    name_entry.grid(row=1, column=1, columnspan=2)

    back_button.grid(row=2, column=0)
    save_button.grid(row=2, column=2)


def create_tag(section_variable: tk.StringVar, name_variable: tk.StringVar, popup: tk.Toplevel) -> None:
    """
    Creates a new tag from a section name, tag name, and a popup frame
    :param section_variable: variable containing the section name
    :param name_variable: variable containing the new tag name
    :param popup: popup frame reference
    :return:
    """
    chosen_section = section_variable.get()

    # find section object
    for section in TAG_SECTIONS:
        if section.section_name == chosen_section:
            chosen_section = section
            break
    else:
        # section not found
        return

    # create new tag
    tag = db_handler.create_tag(chosen_section.db_id, name_variable.get())

    # add tag to section tag list
    chosen_section.tags.append(tag)

    # reload tag context menu
    ROOT.tag_menu = create_tags_menu()

    # close popup
    popup.destroy()


def remove_tag():
    active_tag = ROOT.tag_list.get(tk.ACTIVE)

    if CURRENT_CLIP is not None:
        # find tag in current clip tags
        for tag in CURRENT_CLIP.tags:
            if tag.name == active_tag:
                break
        else:
            tag = None

        # check if tag was found
        if tag is not None:
            # remove tag from list
            CURRENT_CLIP.tags.remove(tag)

            # remove tag in DB
            db_handler.remove_tag(CURRENT_CLIP.db_id, tag.db_id)

            # refresh UI
            select_clip(None)


def change_tag_dropdown(*_args) -> None:
    """
    Changes the tags listed in the tag dropdown when deleting a tag
    :return:
    """
    try:
        section_variable: tk.StringVar = ROOT.section_variable
        tag_dropdown: tk.OptionMenu = ROOT.tag_dropdown
        tag_var: tk.StringVar = ROOT.tag_variable
    except AttributeError:
        print("objs not found")
        return

    chosen_section = section_variable.get()

    # find section object
    for section in TAG_SECTIONS:
        if section.section_name == chosen_section:
            chosen_section = section
            break
    else:
        # section not found
        return

    # get tags
    tags = db_handler.get_tags_in_section(chosen_section.db_id)

    # delete existing tag options
    tag_dropdown['menu'].delete(0, tk.END)

    for tag in tags:
        # add in new options
        tag_dropdown['menu'].add_command(label=tag.name)

    tag_var.set(tags[0].name)


def create_tag_delete_popup() -> None:
    """
    Creates a popup window that requests which tag to delete
    :return:
    """
    global ROOT

    # ensure there are valid tag sections first
    if len(TAG_SECTIONS) == 0:
        create_section_popup()
        # check to make sure a section was created
        if len(TAG_SECTIONS) == 0:
            return

    # create a set of section options
    section_options = [section.section_name for section in TAG_SECTIONS]
    section_tags = db_handler.get_tags_in_section(TAG_SECTIONS[0].db_id)

    popup = tk.Toplevel()

    tag_label = tk.Label(popup, text="Tag: ")
    tag_variable = tk.StringVar()
    tag_variable.set(section_tags[0].name)
    tag_dropdown = tk.OptionMenu(popup, tag_variable, *[tag.name for tag in section_tags])

    section_label = tk.Label(popup, text="Tag Section: ")
    section_variable = tk.StringVar()
    section_variable.set(section_options[0])
    section_dropdown = tk.OptionMenu(popup, section_variable, *section_options)

    # set global variables
    ROOT.section_variable = section_variable
    ROOT.tag_dropdown = tag_dropdown
    ROOT.tag_variable = tag_variable

    section_variable.trace_add("write", change_tag_dropdown)

    # buttons
    back_button = tk.Button(popup, text="Back", command=popup.destroy)
    save_button = tk.Button(popup, text="Delete", command=lambda: delete_tag(section_variable, tag_variable, popup))

    # place items on grid
    popup.grid()

    section_label.grid(row=0, column=0)
    section_dropdown.grid(row=0, column=1, columnspan=2)

    tag_label.grid(row=1, column=0)
    tag_dropdown.grid(row=1, column=1, columnspan=2)

    back_button.grid(row=2, column=0)
    save_button.grid(row=2, column=2)


def create_section_delete_popup() -> None:
    """
    Creates a popup window that requests which section to delete
    :return:
    """

    # ensure there are valid tag sections first
    if len(TAG_SECTIONS) == 0:
        create_section_popup()
        # check to make sure a section was created
        if len(TAG_SECTIONS) == 0:
            return

    # create a set of section options
    section_options = [section.section_name for section in TAG_SECTIONS]

    popup = tk.Toplevel()

    section_label = tk.Label(popup, text="Tag Section: ")
    section_variable = tk.StringVar()
    section_variable.set(section_options[0])
    section_dropdown = tk.OptionMenu(popup, section_variable, *section_options)

    # buttons
    back_button = tk.Button(popup, text="Back", command=popup.destroy)
    save_button = tk.Button(popup, text="Delete", command=lambda: delete_section(section_variable, popup))

    # place items on grid
    popup.grid()

    section_label.grid(row=0, column=0)
    section_dropdown.grid(row=0, column=1, columnspan=2)

    back_button.grid(row=1, column=0)
    save_button.grid(row=1, column=2)


def delete_tag(section_variable: tk.StringVar, tag_variable: tk.StringVar, popup: tk.Toplevel) -> None:
    chosen_section = section_variable.get()

    # find section object
    for section in TAG_SECTIONS:
        if section.section_name == chosen_section:
            chosen_section = section
            break
    else:
        # section not found
        return

    chosen_tag = tag_variable.get()
    for tag in db_handler.get_tags_in_section(chosen_section.db_id):
        if tag.name == chosen_tag:
            chosen_tag = tag
            break
    else:
        return

    db_handler.delete_tag(chosen_tag.db_id)

    # reload tag context menu
    ROOT.tag_menu = create_tags_menu()

    # refresh UI
    select_clip(None)

    # close popup
    popup.destroy()


def delete_section(section_variable: tk.StringVar, popup: tk.Toplevel) -> None:
    """
    Deletes a tag section
    :param section_variable: variable containing the section name
    :param popup: popup frame reference
    :return:
    """
    chosen_section = section_variable.get()

    # find section object
    for section in TAG_SECTIONS:
        if section.section_name == chosen_section:
            chosen_section = section
            TAG_SECTIONS.remove(section)
            break
    else:
        # section not found
        popup.destroy()
        return

    db_handler.delete_tag_section(chosen_section.db_id)

    # reload tag context menu
    ROOT.tag_menu = create_tags_menu()

    # refresh UI
    select_clip(None)

    # close popup
    popup.destroy()


def close_app():
    """
    Destroys the root object & closes the app
    :return:
    """
    global ROOT

    if ROOT is not None:
        ROOT.destroy()
