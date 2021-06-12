from tkinter import *
from tkinter.messagebox import showinfo

import threading
import RoomPage
import ScoresPage


class RoomsPage(object):
    def __init__(self, client):
        self.client = client
        self.client.listeners = list()
        self.client.listeners.append(self.handle_server_action)
        self.client.start_listening()
        self.rooms_label = None
        self.create_room_button = None
        self.high_scores_button = None
        self.root = Tk()
        self.root.eval('tk::PlaceWindow . center')
        self.root.title('DrawPy - Rooms')
        self.client.send('get_rooms_list')
        self.controls = []

        self.root.resizable(False, False)
        self.root.mainloop()

    def handle_server_action(self, action, args):
        """
        handles a message that was sent from the server
        :param action: action to send
        :param args: the action's arguments
        """
        if action == 'rooms_list':
            self.draw_rooms(args)
        elif action == 'room_list_refresh':
            self.clear_rooms()
            self.client.send('get_rooms_list')
        elif action == 'room_created' or action == 'joined_room':
            self.remove_server_listener()
            self.root.withdraw()
            threading.Thread(target=self.open_room).start()

    def open_room(self):
        RoomPage.RoomPage(self.client)

    def draw_rooms(self, args):
        """
        draw the list of available rooms
        :return:
        """
        self.rooms_label = Label(self.root, text='Rooms:', width=15, padx=10, pady=10)
        self.rooms_label.pack(fill=X, pady=20, padx=80)

        for room in args.split(':'):
            if len(room.split('|')) != 2:
                continue

            (room_id, room_name) = room.split('|')
            choose_room = Button(self.root, text=room_name, command=self.choose_room(room_id),
                                 width=25, padx=10,
                                 pady=10)
            choose_room.pack(fill=X, pady=20, padx=80)
            self.controls.append(choose_room)

        self.create_room_button = Button(self.root, text='Create Room', command=self.create_room, width=15, padx=10,
                                         pady=10)
        self.create_room_button.pack(fill=X, pady=20, padx=80)

        self.high_scores_button = Button(self.root, text='High Scores', command=self.high_scores, width=10, padx=10,
                                         pady=10)
        self.high_scores_button.pack(fill=X, pady=20, padx=80)

    def clear_rooms(self):
        """
        clear the rooms ui
        """
        for control in self.controls:
            control.destroy()

        self.rooms_label.destroy()
        self.create_room_button.destroy()
        self.high_scores_button.destroy()

        self.controls = []

    def choose_room(self, room_id):
        """
        choose a room to join
        :return:
        """
        def room_chosen():
            self.client.send('client_join_room', room_id)

        return room_chosen

    def create_room(self):
        """
        create a room with the players' name
        :return:
        """
        parts = self.client.name.split('@')
        player_name = parts[0]
        self.client.send('client_create_room', f"{player_name}'s room")

    def high_scores(self):
        """
        opens the high_scores page
        :return:
        """
        self.client.stop_listening()
        self.client.send('empty')
        self.remove_server_listener()
        self.root.withdraw()
        ScoresPage.ScoresPage(self.client)

    def remove_server_listener(self):
        self.client.listeners.remove(self.handle_server_action)
