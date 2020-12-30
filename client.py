import socket
import uuid
import threading


class Client:
    def __init__(self, server_messages_handler):
        self.id = str(uuid.uuid4())
        self.client = None
        self.server_messages_handler = server_messages_handler

    def connect(self, ip, port):
        """
        connect to a remote socket server
        :param ip: the server's ip
        :param port: the server's port
        """
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((ip, port))
        self.client.send(bytes(f'{self.id},client_connect,\n', encoding='utf8'))
        threading.Thread(target=self.accept_server_message, args=()).start()

    def accept_server_message(self):
        """
        accepts a message from the server and sends it to the game's client messages handler
        :return:
        """
        try:
            leftovers_from_previous_message = ''
            while True:
                server_message = leftovers_from_previous_message + str(self.client.recv(4096), encoding='utf-8')
                leftovers_from_previous_message = ''
                if not server_message:
                    self.client.close()

                server_messages = list(filter(None, server_message.split('\n')))
                print(server_messages)

                for message in server_messages:
                    if len(message.split(',')) != 3:
                        leftovers_from_previous_message += message
                        continue

                    (origin, action, args) = message.split(',')
                    self.server_messages_handler(action, args)

        except ConnectionAbortedError:
            pass

    def send(self, action, args):
        """
        send a message with an action to the socket server
        :param action: action to send
        :param args: the action's arguments
        """
        self.client.send(bytes(f'{self.id},{action},{args}\n', encoding='utf8'))

    def close(self):
        """
        close the socket client
        """
        self.client.close()
