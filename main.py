"""
Developed by Keagan B
ClipMaker -- main.py

Primary driver script for the app
Creates database connection & starts UI loop

TODO:
UI Scaling
Clip exporting
Folder exporting
Previous/Next buttons
Restart video after reaching end
Subfolder support
"""
import os
import db_handler
import ui


def main():
    # connect to database
    db = db_handler.get_database(should_wipe=False)

    # set UI database
    ui.DB_OBJ = db

    # load video extensions
    if os.path.exists("./video_extensions.txt"):
        with open("./video_extensions.txt", "r") as f:
            extensions = f.read()
            f.close()

        # split extensions & remove newlines
        ui.VIDEO_EXTENSIONS = extensions.split("\n")

    # create UI
    ui_root = ui.create_ui()

    # start main UI loop
    ui_root.mainloop()


if __name__ == "__main__":
    main()
