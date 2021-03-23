from tkinter import *
from tkinter.messagebox import showinfo

import RoomPage
import ScoresPage


class RoomsPage(object):
    def __init__(self, client):
        self.client = client
        self.root = Tk()

        self.root.eval('tk::PlaceWindow . center')

        self.root.title('DrawPy - Rooms')

        self.rooms_label = Label(self.root, text='Rooms:', width=25, padx=10, pady=10)
        self.rooms_label.pack(fill=X, pady=20, padx=80)

        self.draw_rooms()

        self.create_room_button = Button(self.root, text='Create Room', command=self.create_room, width=25, padx=10,
                                         pady=10)
        self.create_room_button.pack(fill=X, pady=20, padx=80)

        self.high_scores_button = Button(self.root, text='High Scores', command=self.high_scores, width=10, padx=10,
                                         pady=10)
        self.high_scores_button.pack(fill=X, pady=20, padx=80)

        self.root.resizable(False, False)
        self.root.mainloop()

    def draw_rooms(self):
        """
        draw the list of available rooms
        :return:
        """
        (origin, action, args) = self.client.send_and_wait('get_rooms_list')

        for room in args.split(':'):
            if len(room.split('|')) != 2:
                continue

            (room_id, room_name) = room.split('|')
            choose_room = Button(self.root, text=room_name, command=self.choose_room(room_id),
                                 width=25, padx=10,
                                 pady=10)
            choose_room.pack(fill=X, pady=20, padx=80)

    def choose_room(self, room_id):
        """
        choose a room to join
        :return:
        """
        def room_chosen():
            self.client.send_and_wait('client_join_room', room_id)
            self.root.withdraw()
            RoomPage.RoomPage(self.client)

        return room_chosen

    def create_room(self):
        """
        create a room with the players' name
        :return:
        """
        player_name = self.client.name.split('@')
        player_name = player_name[0]
        self.client.send_and_wait('client_create_room', f"{player_name}'s room")
        self.root.withdraw()
        self.client.current_page = RoomPage.RoomPage(self.client)

    def high_scores(self):
        """
        opens the high_scores page
        :return:
        """
        self.root.withdraw()
        ScoresPage.ScoresPage(self.client)
