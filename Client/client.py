import socket
import time
import uuid
import threading
import configparser
import os.path

import MainMenu
import RoomPage
import Game

# load the server ip from the config.ini file
config = configparser.ConfigParser()

if os.path.isfile('config.ini') is not True:
    print('The config.ini file is missing, please create it')
    print('[server]')
    print('ip = <server-ip-get-from-ipconfig>')

config.read('config.ini')

server_ip = config['server']['ip'] or '127.0.0.1'

class Client:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.client = None
        self.connect(server_ip, 3000)
        self.name = ''
        self.listening_to_server = False
        self.game = None
        self.current_page = None
        self.listeners = list()
        MainMenu.MainMenu(self)
        self.disconnect()

    def connect(self, ip, port):
        """
        connect to a remote socket Server
        :param ip: the Server's ip
        :param port: the Server's port
        """
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((ip, port))

    def disconnect(self):
        self.client.close()

    def start_listening(self, current_page):
        self.current_page = current_page
        self.listening_to_server = True
        threading.Thread(target=self.accept_server_message, args=()).start()

    def stop_listening(self):
        self.listening_to_server = False

    def accept_server_message(self):
        """
        accepts a message from the Server and sends it to the game's Client messages handler
        :return:
        """
        try:
            leftovers_from_previous_message = ''
            while self.listening_to_server:
                server_message = leftovers_from_previous_message + str(self.client.recv(16384), encoding='utf-8')
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

    def start_game_loop(self, action, args):
        Game.Game(self)

    def notify_listeners(self, action, args):
        for listener in self.listeners:
            listener(action, args)

    def server_messages_handler(self, action, args):
        if action == 'game_ended':
            self.stop_listening()
            self.notify_listeners(action, args)
            self.current_page = RoomPage.RoomPage(self)
        elif action == 'left_room':
            self.stop_listening()
        elif action == 'game_starting':
            self.current_page.root.withdraw()
            threading.Thread(target=self.start_game_loop, args=(action, args)).start()
            time.sleep(2)
        else:
            self.notify_listeners(action, args)

    def send(self, action, args=''):
        """
        send a message with an action to the socket Server
        :param action: action to send
        :param args: the action's arguments
        """
        self.client.send(bytes(f'{self.id},{action},{args}\n', encoding='utf8'))

    def send_and_wait(self, action, args=''):
        """
        send a message with an action to the socket Server and wait for the server's response
        :param action: action to send
        :param args: the action's arguments
        """
        self.send(action, args)
        server_message = str(self.client.recv(4096), encoding='utf-8')
        if not server_message:
            self.client.close()
        print(server_message)

        return server_message.replace('\n', '').split(',')

    def close(self):
        """
        close the socket Client
        """
        self.client.close()


if __name__ == '__main__':
    Client()
