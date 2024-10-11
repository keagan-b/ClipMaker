# ClipMaker
Small UI-based tool to help with the editing and categorizing of videos

*Please note this is still a work in progress. Some features do not currently work, please see below.*

---

## How To Use

1. Import a folder by right-clicking the left most panel and selecting "Add Folder"
2. Select a clip by clicking on its name in the tree view
3. Change the display name of the clip and mark it as a favorite on the right side of the UI.
4. Add tags by right-clicking the tag box on the bottom right

---

## Requirements

The majority of this project uses preinstalled packages (such as `tkinter` for UI), but the video handling is done through the Python VLC bindings. You can install this package from pip by using `pip install python-vlc`.

Additionally, this program relies on `ffmpeg-python`, which can be installed with `pip install ffmpeg-python`. If you don't have it installed, you'll need to download ffmpeg. You can download it from their [site](https://ffmpeg.org/download.html). Please added to your system path.

---
## Features
- [x] Importing folders
- [x] Editing clip display names
- [x] Marking clips as favorites
- [x] Clip media controls
- [x] Tag creation & assignment
- [x] Tag sections/groups
- [x] Clip filtering/sorting with tags
- [x] Clip export options
- [ ] UI rework