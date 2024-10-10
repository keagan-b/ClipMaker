"""
Developed by Keagan B
ClipMaker -- media_handler.py

Handles the trimming of individual clips and entire folders.
"""
import os.path

import tkinter as tk
import db_handler
import pathlib
import ffmpeg


def trim_clip(input_path: str, output_dir: str, start: int, end: int) -> None:
    """
    Trim a clip down to the chosen start/end size
    :param input_path: Path to input clip
    :param output_dir: Path to the output directory
    :param start: Starting millisecond to trim from
    :param end: Ending millisecond to trim to
    :return:
    """

    # get start in seconds
    start = start // 1000

    # get end in seconds
    if end < 0:
        end = end // 1000

    # get input path
    input_path = f"{str(pathlib.Path(input_path).absolute())}"

    # get output file name
    output_loc = f"{str(pathlib.Path(output_dir).joinpath(pathlib.Path(input_path).name).absolute())}"

    if os.path.exists(output_loc):
        os.remove(output_loc)

    # grab input file
    input_stream = ffmpeg.input(input_path)

    # get video and audio streams
    video = input_stream.video
    audio = input_stream.audio

    # trim input streams
    if end > 0:
        video = video.trim(start=start, end=end)
    else:
        video = video.trim(start=start)

    # trim audio stream
    if end > 0:
        audio = audio.filter('atrim', start=start, end=end)
    else:
        audio = audio.filter('atrim', start=start)

    # set video output location and input streams
    out = ffmpeg.output(video, audio, output_loc)

    # run commands
    out.run()


def export_folder(clip_ids: list[int], output_dir: str) -> None:
    """
    Loops through a list of clips and
    :param clip_ids: list of clip ids
    :param output_dir: Directory to output videos to
    :return:
    """

    # loop through clip ids
    for clip_id in clip_ids:
        # get clip from database
        clip = db_handler.get_clip_from_id(clip_id)
        # trim the clip
        trim_clip(clip.path, output_dir, clip.trimmed_start, clip.trimmed_end)


def create_export_ui():
    # create a popup
    popup = tk.Toplevel()

    # alert label
    label = tk.Label(popup, text="Exporting. This may take a few moments.")

    # close button
    close_button = tk.Button(popup, text="close", command=popup.destroy)

    popup.grid()

    label.grid(row=0, column=0)
    close_button.grid(row=1, column=0)

    popup.update()

