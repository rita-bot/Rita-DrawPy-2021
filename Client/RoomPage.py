from tkinter import *

import threading
import RoomsPage
import Game


class RoomPage(object):
    def __init__(self, client):
        self.client = client
        self.client.listeners.append(self.handle_server_action)
        self.client.current_page = self
        self.start_game_button = None
        self.leave_room_button = None
        self.room_label = None
        self.controls = []
        self.root = Tk()

        self.root.eval('tk::PlaceWindow . center')

        self.root.title('DrawPy - Rooms')

        self.client.send('room:get_room_info')
        self.was_drawn = False

        self.root.resizable(False, False)
        self.root.mainloop()

    def handle_server_action(self, action, args):
        """
        handles a message that was sent from the server
        :param action: action to send
        :param args: the action's arguments
        """
        if action == 'refresh_room_info':
            self.clear_room()
            self.client.send('room:get_room_info')
        elif action == 'room_info':
            if self.was_drawn is True:
                self.clear_room()
            self.draw_room(action, args)
        elif action == 'left_room':
            threading.Thread(target=self.back).start()

    def draw_room(self, action, args):
        """
        create a room ui
        :param action: action to send
        :param args: the action's arguments
        """
        (name, players) = args.split(':')
        self.room_label = Label(self.root, text=f"Room {name}:", width=25, padx=10, pady=10)
        self.room_label.pack(fill=X, pady=20, padx=80)
        self.controls.append(self.room_label)
        players_count = len(players.split('-'))

        for player in players.split('-'):
            name_parts = player.split('@')
            player_name = name_parts[0]
            choose_room = Label(self.root, text=player_name, width=25, padx=10, pady=10)
            choose_room.pack(fill=X, pady=20, padx=80)
            self.controls.append(choose_room)

        if players_count > 1:
            self.start_game_button = Button(self.root, text='Start Game', command=self.start_game, width=10, padx=10,
                                            pady=10)
            self.start_game_button.pack(fill=X, pady=20, padx=80)

        self.leave_room_button = Button(self.root, text='Leave Room', command=self.leave_room, width=10, padx=10,
                                        pady=10)
        self.leave_room_button.pack(fill=X, pady=20, padx=80)
        self.was_drawn = True

    def clear_room(self):
        """
        clear the room ui
        """
        for control in self.controls:
            control.destroy()

        if self.start_game_button:
            self.start_game_button.destroy()
        self.leave_room_button.destroy()
        self.room_label.destroy()

        self.controls = []

    def start_game(self):
        """
        send a message to the server to start the game
        """
        self.client.send('room:start_game')

    def leave_room(self):
        """
        leave the room
        """
        self.client.send('client_leave_room')

    def back(self):
        self.remove_server_listener()
        self.root.withdraw()
        RoomsPage.RoomsPage(self.client)

    def remove_server_listener(self):
        self.client.listeners.remove(self.handle_server_action)

