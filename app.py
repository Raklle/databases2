from flask import Flask
from tkinter import *
from tkinter import ttk
from enum import Enum
import pygubu
import os
import pathlib
import models

class GuiEnum(Enum):
    LOGIN = 0
    LOBBIES = 1
    EXIT = 2
    ROOM = 3

PROJECT_PATH = pathlib.Path(__file__).parent
LOBBY_UI = os.path.join(PROJECT_PATH, "lobby.ui")
LOGIN_UI = os.path.join(PROJECT_PATH, "login.ui")
ROOM_UI = os.path.join(PROJECT_PATH, "room.ui")

app = Flask(__name__)
@app.route('/')

class RoomGui:
    def __init__(self, root, change_scene, game_id) -> None:
        self.root = pygubu.Builder()
        self.root.add_resource_path(PROJECT_PATH)
        self.root.add_from_file(ROOM_UI)
        self.change_scene = change_scene
        self.game_id = game_id

        self.mainwindow = self.root.get_object('main_frame', None)
        root.protocol("WM_DELETE_WINDOW", self.callback)

        frame = self.root.get_object('room_frame', None)

        frame.columnconfigure(0, minsize=200)
        frame.columnconfigure(1, minsize=200)
        frame.columnconfigure(2, minsize=200)

        for i in range(10):
            frame.rowconfigure(i, minsize=20)

        players = models.get_players(self.game_id)

        for i in range(len(players)):
            label1 = Label(frame, text=str(i))
            label1.grid(column = 0, row = i, sticky='we')

            label2 = Label(frame, text="0")
            label2.grid(column = 2, row = i, sticky='we')

            label3 = Label(frame, text=players[i][0])
            label3.grid(column = 1, row = i, sticky='we')

        self.mainwindow.mainloop()

    def exit(self):
        self.mainwindow.destroy()
        self.change_scene(GuiEnum.EXIT)

    def callback(self):
        self.mainwindow.destroy()
        self.change_scene(GuiEnum.LOBBIES)


class LoginGui:
    def __init__(self, root, change_scene) -> None:
        self.root = pygubu.Builder()
        self.root.add_resource_path(PROJECT_PATH)
        self.root.add_from_file(LOGIN_UI)
        self.change_scene = change_scene

        self.mainwindow = self.root.get_object('main_frame', None)

        button = self.root.get_object('create_user')
        button.bind('<Button-1>', lambda event: self.callback())
        root.protocol("WM_DELETE_WINDOW", self.exit)

        self.mainwindow.mainloop()

    def exit(self):
        self.mainwindow.destroy()
        self.change_scene(GuiEnum.EXIT)

    def callback(self):
        self.mainwindow.destroy()
        self.change_scene(GuiEnum.LOBBIES)

class LobbyGui:
    def __init__(self, root, change_scene) -> None:
        self.root = pygubu.Builder()
        self.root.add_resource_path(PROJECT_PATH)
        self.root.add_from_file(LOBBY_UI)
        self.change_scene = change_scene

        self.mainwindow = self.root.get_object('main_frame', None)
        root.protocol("WM_DELETE_WINDOW", self.callback)

        frame = self.root.get_object('lobbies_frame', None)
        games = models.get_games()

        frame.columnconfigure(0, minsize=200)
        frame.columnconfigure(1, minsize=200)
        frame.columnconfigure(2, minsize=200)

        for i in range(10):
            frame.rowconfigure(i, minsize=20)

        for i in range(len(games)):
            label1 = Label(frame, text=games[i][0])
            label1.bind('<Button-1>', lambda event: self.callback(GuiEnum.ROOM, games[i][0]))
            label1.grid(column = 0, row = i, sticky='we')

            label2 = Label(frame, text="0")
            label2.bind('<Button-1>', lambda event: self.callback(GuiEnum.ROOM, games[i][0]))
            label2.grid(column = 1, row = i, sticky='we')

            label3 = Label(frame, text=games[i][3])
            label3.bind('<Button-1>', lambda event: self.callback(GuiEnum.ROOM, games[i][0]))
            label3.grid(column = 2, row = i, sticky='we')

        self.mainwindow.mainloop()

    def callback(self, new_scene : GuiEnum = GuiEnum.LOGIN, game_id: int = None):
        self.mainwindow.destroy()
        self.change_scene(new_scene, game_id)

def hello_world():  # put application's code here
    class GuiManager:
        def __init__(self) -> None:
                    self.main_screen = None
                    self.current_screen = GuiEnum.LOGIN
                    self.root = Tk()
                    self.root.title("Poker")
                    self.load_scene()
                    self.root.mainloop()
                    self.room_id = None

        def change_scene(self, new_scene : GuiEnum, scene_data = None):
            self.current_screen = new_scene

            if new_scene == GuiEnum.ROOM:
                self.room_id = scene_data

            self.load_scene()

        def load_scene(self):
            if self.current_screen == GuiEnum.LOGIN: 
                self.main_screen = LoginGui(self.root, self.change_scene)

            if self.current_screen == GuiEnum.LOBBIES: 
                self.main_screen = LobbyGui(self.root, self.change_scene)

            if self.current_screen == GuiEnum.ROOM: 
                self.main_screen = RoomGui(self.root, self.change_scene, self.room_id)

            if self.current_screen == GuiEnum.EXIT:
                self.root.destroy()
                return 

    GuiManager()

hello_world()
