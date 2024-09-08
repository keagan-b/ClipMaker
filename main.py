"""
Developed by Keagan B
ClipMaker -- main.py

Primary driver script for the app
Creates database connection & starts UI loop

"""

import db_handler
import ui


def main():
    # connect to database
    db = db_handler.get_database(should_wipe=True)

    # set UI database
    ui.DB_OBJ = db

    # create UI
    ui_root = ui.create_ui()
    # ui_root = ui.temp_ui()

    # start main UI loop
    ui_root.mainloop()


if __name__ == "__main__":
    main()
