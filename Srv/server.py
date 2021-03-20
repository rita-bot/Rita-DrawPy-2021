import socket
import threading
import time

import TwoFactorAuth
from Database import DatabaseConnection
from Room import Room
from Server.EmailSender import send_email


class Server:
    PORT = 3000

    def __init__(self):
        self.clients_connections = {}
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
                client_message = str(client_socket.recv(4096), encoding='utf-8')
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
            self.clients_emails.pop(client_id)
            self.clients_rooms.pop(client_id)
        except:
            pass

        client_socket.close()
        print('Client disconnected')

    def send(self, client_socket, client_id, action, args=''):
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
        handle a Client's connection action
        :param client_socket: the Client socket
        :param client_id: the Client id
        """
        (email, password) = args.split(':')
        db_connection = DatabaseConnection()
        result = db_connection.validate_user(email, password)
        db_connection.close_connection()

        if result is True:
            code = TwoFactorAuth.generate_code()
            self.two_factor_codes[client_id] = code
            self.clients_emails[client_id] = email
            print(f"The code for user {client_id} - {email} is {code}")
            send_email(email, code)
            self.send(client_socket, client_id, 'login_success')
        else:
            self.send(client_socket, client_id, 'login_failure')

    def client_two_factor_code(self, client_socket, client_id, action, args):
        if self.two_factor_codes[client_id] == args:
            self.clients_connections[client_id] = client_socket
            self.send(client_socket, client_id, 'client_two_factor_code_success')
        else:
            self.send(client_socket, client_id, 'client_two_factor_code_failure')

    def client_create_room(self, client_socket, client_id, action, room_name):
        room = Room(room_name)
        self.clients_rooms[client_id] = room
        self.rooms[room.id] = room
        room.join(self.clients_emails[client_id], client_id, client_socket)
        self.send(client_socket, client_id, 'room_created')

    def client_join_room(self, client_socket, client_id, action, room_id):
        room = self.rooms[room_id]
        self.clients_rooms[client_id] = room
        room.join(self.clients_emails[client_id], client_id, client_socket)
        self.send(client_socket, client_id, 'joined_room')

    def client_leave_room(self, client_socket, client_id, action, args):
        room = self.clients_rooms[client_id]
        self.clients_rooms.pop(client_id)
        room.leave(client_id)
        if len(list(room.clients)) == 0:
            self.rooms.pop(room.id)

        self.send(client_socket, client_id, 'left_room')

    def get_rooms_list(self, client_socket, client_id, action, args):
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
        db_connection = DatabaseConnection()
        scores = db_connection.get_high_scores()
        db_connection.close_connection()
        response = ''

        index = 0
        for score_row in scores:
            (email, score, dt) = score_row
            date = dt if len(dt.split(' ')) == 1 else dt.split(' ')[0]
            response += f"{email} scored {score} at {date}"

            if index != len(scores) - 1:
                response += '|'

            index += 1

        self.send(client_socket, client_id, 'high_scores', response)


if __name__ == '__main__':
    Server()