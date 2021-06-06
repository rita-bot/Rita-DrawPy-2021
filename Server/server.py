import socket
import threading
import time

import TwoFactorAuth
from Database import DatabaseConnection
from Room import Room
from EmailSender import send_email


class Server:
    PORT = 3000

    def __init__(self):
        self.clients_connections = {}
        self.connected_emails = {}
        self.rooms = {}
        self.clients_rooms = {}
        self.clients_emails = {}
        self.two_factor_codes = {}
        serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serv.bind(('0.0.0.0', self.PORT))
        serv.listen(5)
        print('Server listening on port ' + str(self.PORT))

        while True:
            conn, addr = serv.accept()
            threading.Thread(target=self.on_new_client, args=(conn, addr)).start()

    def on_new_client(self, client_socket, addr):
        """
        Called when a new Client is accepted on the bound socket (on a new thread)
        :param client_socket: the Client socket
        :param addr: the Client socket address
        """
        print('Client connected')
        client_id = ''
        try:
            while True:
                client_message = str(client_socket.recv(16384), encoding='utf-8')
                if not client_message:
                    break
                client_messages = list(filter(None, client_message.split('\n')))
                print(client_messages)

                for message in client_messages:
                    (client_id, action, args) = message.split(',')
                    self.handle_client_action(client_socket, client_id, action, args)
        except ConnectionResetError:
            pass

        try:
            self.clients_connections.pop(client_id)
            self.connected_emails.pop(self.clients_emails[client_id])
            self.clients_emails.pop(client_id)
            self.remove_client_from_room(client_id)
        except:
            pass

        client_socket.close()
        print('Client disconnected')

    def notify_other_clients(self, client_id, action, args=''):
        """
        notify all other clients besides client_id of an action
        :param client_id: the Client id
        :param action: the action to notify of
        :param args: the action's arguments
        """
        for id in self.clients_connections.keys():
            if id == client_id:
                continue

            client = self.clients_connections[id]
            self.send(client, client_id, action, args)

    def send(self, client_socket, client_id, action, args=''):
        """
        send clients' id
        :param client_socket: the Client socket
        :param client_id: the Client id
        :param action: the action to send a message
        :param args: the action's arguments
        """
        client_socket.send(bytes(f'{client_id},{action},{args}\n', encoding='utf8'))

    def handle_client_action(self, client_socket, client_id, action, args):
        """
        handles an action sent from the Client
        :param client_socket: the Client socket
        :param client_id: the Client's id
        :param action: the Client's action
        :param args: the Client's action's arguments
        """
        if action == 'client_login':
            self.client_login(client_socket, client_id, action, args)
        if action == 'client_two_factor_code':
            self.client_two_factor_code(client_socket, client_id, action, args)
        elif action == 'client_register':
            self.client_register(client_socket, client_id, action, args)
        elif action.startswith('room:'):
            room = self.clients_rooms[client_id]
            action = action.replace('room:', '')
            room.handle_client_action(client_socket, client_id, action, args)
        elif action == 'client_create_room':
            self.client_create_room(client_socket, client_id, action, args)
        elif action == 'client_join_room':
            self.client_join_room(client_socket, client_id, action, args)
        elif action == 'client_leave_room':
            self.client_leave_room(client_socket, client_id, action, args)
        elif action == 'get_rooms_list':
            self.get_rooms_list(client_socket, client_id, action, args)
        elif action == 'get_high_scores':
            self.get_high_scores(client_socket, client_id, action, args)
        elif action == 'empty':
            self.send(client_socket, client_id, 'empty')

    def client_register(self, client_socket, client_id, action, args):
        (email, password) = args.split(':')
        db_connection = DatabaseConnection()
        result = db_connection.add_user(email, password)
        db_connection.close_connection()

        if result is True:
            self.send(client_socket, client_id, 'client_register_success')
        else:
            self.send(client_socket, client_id, 'client_register_failure', result)

    def client_login(self, client_socket, client_id, action, args):
        """
        handle a Client's login action
        :param client_socket: the Client socket
        :param client_id: the Client id
        """
        (email, password) = args.split(':')
        if email in self.connected_emails:
            self.send(client_socket, client_id, 'login_failure_already_connected')
            return
        db_connection = DatabaseConnection()
        result = db_connection.validate_user(email, password)
        db_connection.close_connection()

        if result is True:
            code = TwoFactorAuth.generate_code()
            self.two_factor_codes[client_id] = code
            self.clients_emails[client_id] = email
            self.connected_emails[email] = True
            print(f"The code for user {client_id} - {email} is {code}")
            send_email(email, code)
            self.send(client_socket, client_id, 'login_success')
        else:
            self.send(client_socket, client_id, 'login_failure')

    def client_two_factor_code(self, client_socket, client_id, action, args):
        """
        check if code is correct and inform the client
        """
        if self.two_factor_codes[client_id] == args:
            self.clients_connections[client_id] = client_socket
            self.send(client_socket, client_id, 'client_two_factor_code_success')
        else:
            self.send(client_socket, client_id, 'client_two_factor_code_failure')

    def client_create_room(self, client_socket, client_id, action, room_name):
        """
        create a new room for other clients to join
        """
        room = Room(room_name)
        self.clients_rooms[client_id] = room
        self.rooms[room.id] = room
        room.join(self.clients_emails[client_id], client_id, client_socket)
        self.send(client_socket, client_id, 'room_created')
        self.notify_other_clients(client_id, 'room_list_refresh')

    def client_join_room(self, client_socket, client_id, action, room_id):
        """
        join an existing room
        """
        room = self.rooms[room_id]
        self.clients_rooms[client_id] = room
        room.join(self.clients_emails[client_id], client_id, client_socket)
        self.send(client_socket, client_id, 'joined_room')

    def remove_client_from_room(self, client_id):
        room = self.clients_rooms[client_id]
        self.clients_rooms.pop(client_id)
        room.leave(client_id)
        if len(list(room.clients)) == 0:
            self.rooms.pop(room.id)
            self.notify_other_clients(client_id, 'room_list_refresh')

    def client_leave_room(self, client_socket, client_id, action, args):
        """
        leave room and inform the client has left the room
        """
        self.remove_client_from_room(client_id)
        self.send(client_socket, client_id, 'left_room')

    def get_rooms_list(self, client_socket, client_id, action, args):
        """
        get the list of rooms existing
        """
        rooms = ''
        index = 0
        for room_id in self.rooms:
            room = self.rooms[room_id]
            rooms += f"{room_id}|{room.name}"

            if index != len(list(self.rooms)) - 1:
                rooms += ':'

            index += 1

        self.send(client_socket, client_id, "rooms_list", rooms)

    def get_high_scores(self, client_socket, client_id, action, args):
        """
        get the highest scores from all games
        """
        db_connection = DatabaseConnection()
        scores = db_connection.get_high_scores()
        db_connection.close_connection()
        response = ''

        index = 0
        for score_row in scores:
            (email, score, dt) = score_row
            parts = email.split('@')
            player_name = parts[0]
            date = dt if len(dt.split(' ')) == 1 else dt.split(' ')[0]
            response += f"{player_name} scored {score} at {date}"

            if index != len(scores) - 1:
                response += '|'

            index += 1

        self.send(client_socket, client_id, 'high_scores', response)


if __name__ == '__main__':
    Server()
