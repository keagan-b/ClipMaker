"""
Developed by Keagan B
ClipMaker -- media_player.py

VLC integration for the primary UI. Inspired by the VLC Python Bindings example script for tkinter.
http://git.videolan.org/?p=vlc/bindings/python.git;a=blob_plain;f=examples/tkvlc.py;hb=HEAD
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
import vlc

TICK_INCREMENT_MS = 100


class MediaPlayer(tk.Frame):
    def __init__(self, parent: tk.Frame | tk.Tk, video_width: int = 15, video_height: int = 10,
                 video_scale: int = 1):
        self.video_width = 15 * video_scale
        self.video_height = 10 * video_scale

        tk.Frame.__init__(self, parent)

        # set parent (typically root)
        self.parent = parent

        # create VLC instance
        self.Instance = vlc.Instance()

        # create new VLC player
        self.player = self.Instance.media_player_new()

        # create video frame & video canvas
        self.video_frame = ttk.Frame(self.parent)
        self.video_canvas = tk.Canvas(self.video_frame)

        # place canvas on parent
        self.video_canvas.grid(row=0, column=5)
        self.video_frame.grid(row=0, column=5, rowspan=self.video_height, columnspan=self.video_width, sticky="NSWE")
        self.video_frame.update_idletasks()

        # media slider handler
        self._is_sliding = False

        # tick update handlers
        self._tick_timer = self.after(1)

        # media length tracker
        self._length = 0

        # start first tick
        self.handle_tick()

    def play(self, path):
        # get media
        media = self.Instance.media_new(path)

        # add media to player
        self.player.set_media(media)

        # grab canvas ID
        canvas_id = self.video_canvas.winfo_id()

        # set display element to canvas
        self.player.set_hwnd(canvas_id)

        # reset media length counter
        self._length = 0

        # reset audio settings
        self.player.audio_set_mute(False)
        self.player.audio_set_volume(100)

        # reset media position
        self._set_time(0)

        # play media
        self.player.play()

    def skip(self, increment: int = 0) -> None:
        """
        :param increment: Milliseconds to change current point in video by
        :return:
        """
        if self.player:
            current_time = self.player.get_time()

            self._set_time(current_time + increment)

    def change_play_state(self) -> None:
        """
        Toggles the current play state of the media
        :return:
        """
        is_playing = False

        if self.player:
            if self.player.is_playing():
                # pause video
                is_playing = True

            # toggle pause state
            self.player.pause()

        if is_playing:
            button_value = "⏸"
        else:
            button_value = "⏵"

        # change play button text
        self.parent.play_btn.configure(text=button_value)

    def move_slider(self, _event) -> None:
        """
        Event handler for slider movement
        :param _event: Unused event information
        :return:
        """
        if self.player:
            self._is_sliding = True

            time = self.parent.media_slider.get()

            self._tick_s = self.after_idle(self._set_time, time * TICK_INCREMENT_MS)

    def handle_tick(self):
        # ensure player exists
        if self.player:
            # get media slider information
            try:
                slider = self.parent.media_slider
            except AttributeError:
                slider = None

            # ensure slider exists
            if slider:
                # check if the currently playing content length is over 0 and we're not sliding
                if self._length > 0 and not self._is_sliding:
                    # get current time
                    time = max(0, self.player.get_time() // TICK_INCREMENT_MS)
                    # if times don't match, update slider
                    if time != slider.get():
                        slider.set(time)

                    minutes = ((time // 10) // 60)
                    seconds = ((time // 10) % 60)

                    self.parent.media_timer.configure(text=f"{minutes}:{seconds:02}")

                else:
                    # get current media length (in milliseconds)
                    length = self.player.get_length()
                    if length > 0:
                        # set new media length
                        self._length = max(1, length // TICK_INCREMENT_MS)

                        # update slider config
                        slider.config(to=self._length)

                        # update duration box
                        minutes = ((length // 1000) // 60)
                        seconds = ((length // 1000) % 60)

                        self.parent.duration_variable.set(f"{minutes}:{seconds:02}")

        # set tick timer
        self._tick_timer = self.after(TICK_INCREMENT_MS, self.handle_tick)

    def _set_time(self, milliseconds: int) -> None:
        """
        Set the current player's time
        :param milliseconds: Milliseconds to seek to
        :return:
        """
        if self.player:
            self.player.set_time(milliseconds)
        self._is_sliding = False


class MediaSlider(tk.Scale):
    _var = None

    def __init__(self, frame, to=1, **kwargs):
        """
        Creates a custom media slider object
        :param frame: Parent frame
        :param to: Max size of scale
        :param kwargs: Other arguments for the tk.Scale object
        """
        if isinstance(to, int):
            from_val, var = 0, tk.IntVar()
        else:
            from_val, var = 0, tk.DoubleVar()

        # create config for media slider
        config = {
            "from_": from_val,
            "to": to,
            "orient": tk.HORIZONTAL,
            "showvalue": 0,
            "variable": var
        }

        # update config with other keys
        config.update(kwargs)

        # create new scale object
        tk.Scale.__init__(self, frame, **config)

        self._var = var

    def set(self, value):
        """
        Set the value of the slider
        :param value: Value to set slider to
        :return:
        """
        self._var.set(value)
        tk.Scale.set(self, value)
