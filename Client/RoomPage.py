from tkinter import *

import RoomsPage
import Game


class RoomPage(object):
    def __init__(self, client):
        self.client = client
        self.client.listeners.append(self.handle_server_action)
        self.start_game_button = None
        self.leave_room_button = None
        self.room_label = None
        self.controls = []
        self.root = Tk()

        self.root.eval('tk::PlaceWindow . center')

        self.root.title('DrawPy - Rooms')

        (origin, action, args) = self.client.send_and_wait('room:get_room_info')

        self.draw_room(action, args)

        self.client.start_listening(self)

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
            self.draw_room(action, args)

    def draw_room(self, action, args):
        """
        create a room ui
        :param action: action to send
        :param args: the action's arguments
        """
        (name, players) = args.split(':')
        self.room_label = Label(self.root, text=f"Room {name}:", width=30, padx=10, pady=10)
        self.room_label.pack(fill=X, pady=20, padx=80)
        self.controls.append(self.room_label)
        players_count = len(players.split('-'))

        for player in players.split('-'):
            player_name = player.split('@')
            player_name = player_name[0]
            choose_room = Label(self.root, text=player_name, width=20, padx=10, pady=10)
            choose_room.pack(fill=X, pady=20, padx=80)
            self.controls.append(choose_room)

        if players_count > 1:
            self.start_game_button = Button(self.root, text='Start Game', command=self.start_game, width=10, padx=10,
                                            pady=10)
            self.start_game_button.pack(fill=X, pady=20, padx=80)

        self.leave_room_button = Button(self.root, text='Leave Room', command=self.leave_room, width=10, padx=10,
                                        pady=10)
        self.leave_room_button.pack(fill=X, pady=20, padx=80)

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
        self.root.withdraw()
        self.client.send('client_leave_room')
        RoomsPage.RoomsPage(self.client)
