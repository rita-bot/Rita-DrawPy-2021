import socket
import threading
import random
import time


class Server:
    PORT = 3000

    def __init__(self):
        self.clients = {}
        self.score = {}
        self.round = 0
        self.rounds_until_finish = 2
        self.drawing = None
        self.words = self.read_words_from_file()
        serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serv.bind(('0.0.0.0', self.PORT))
        serv.listen(5)
        print('server listening on port ' + str(self.PORT))

        while True:
            conn, addr = serv.accept()
            threading.Thread(target=self.on_new_client, args=(conn, addr)).start()

    def on_new_client(self, client_socket, addr):
        """
        Called when a new client is accepted on the bound socket (on a new thread)
        :param client_socket: the client socket
        :param addr: the client socket address
        """
        print('client connected')
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

        self.clients.pop(client_id)
        client_socket.close()
        print('client disconnected')

    def handle_client_action(self, client_socket, client_id, action, args):
        """
        handles an action sent from the client
        :param client_socket: the client socket
        :param client_id: the client's id
        :param action: the client's action
        :param args: the client's action's arguments
        """
        if action == 'client_connect':
            self.client_connected_action(client_socket, client_id)
        elif action == 'player_guessed_word':
            self.player_guessed_word(client_id, args)
        else:
            self.notify_other_client(client_id, action, args)

    def client_connected_action(self, client_socket, client_id):
        """
        handle a client's connection action
        :param client_socket: the client socket
        :param client_id: the client id
        """
        client_socket.send(bytes(f'accepted_connection,{client_id},\n', encoding='utf8'))
        self.clients[client_id] = client_socket

        # start the game if there are enough players
        if len(self.clients.keys()) > 1:
            time.sleep(0.1)
            self.start_game()

    def notify_other_client(self, client_id, action, args):
        """
        notify all other clients besides client_id of an action
        :param client_id: the client id
        :param action: the action to notify of
        :param args: the action's arguments
        """
        for id in self.clients.keys():
            if id == client_id:
                continue

            client = self.clients[id]
            client.send(bytes(f'{client_id},{action},{args}\n', encoding='utf8'))

    def start_game(self):
        """
        starts the game in the server - resets score and rounds
        :return:
        """
        self.round = 0
        self.drawing = None
        self.score = {}

        for client_id in self.clients:
            self.score[client_id] = 0

        self.next_turn()

    def set_next_drawing(self):
        """
        sets the next player
        :return:
        """
        clients_list = list(self.clients)
        if self.drawing is None:
            self.drawing = clients_list[0]
        else:
            drawing_index = clients_list.index(self.drawing)

            # if it's the last index, it means we finished a round and need to start from the first client
            if drawing_index == len(clients_list) - 1:
                self.drawing = clients_list[0]
                self.round += 1
            else:
                self.drawing = clients_list[drawing_index + 1]

    def get_word(self):
        """
        gets a random word from the words list
        :return:
        """
        return random.choice(self.words)

    def next_turn(self):
        """
        handles the next turn - gets a words and sends to all clients
        :return:
        """
        self.set_next_drawing()

        if self.round == self.rounds_until_finish:
            self.finish_game()
            return

        word = self.get_word()

        for client_id in self.clients:
            client = self.clients[client_id]
            if client_id == self.drawing:
                client.send(bytes(f'{client_id},start_turn_drawing,{word}\n', encoding='utf8'))
            else:
                client.send(bytes(f'{client_id},start_turn_guessing,{word}\n', encoding='utf8'))

    def get_winner(self):
        """
        gets the winner of the game or 'tie' if there was a tie
        :return: winner of the game or 'tie'
        """
        highest_score_player = None
        highest_score = None
        all_scores_are_the_same = True

        for client_id in self.clients:
            if highest_score_player is None:
                highest_score_player = client_id
                highest_score = self.score[client_id]
                continue

            if self.score[client_id] != highest_score:
                all_scores_are_the_same = False

            if self.score[client_id] > highest_score:
                highest_score_player = client_id
                highest_score = self.score[client_id]

        if all_scores_are_the_same:
            return 'tie'

        return highest_score_player

    def finish_game(self):
        """
        notifies the players about the game ending with their score and win/lose status
        :return:
        """
        winner = self.get_winner()

        if winner == 'tie':
            self.notify_other_client('', 'game_ended', 'tie')
            return

        for client_id in self.clients:
            client = self.clients[client_id]
            score = self.score[client_id]
            if client_id == winner:
                client.send(bytes(f'{client_id},game_ended,you won! your score was: {score}\n', encoding='utf8'))
            else:
                client.send(bytes(f'{client_id},game_ended,you lost :( your score was: {score}\n', encoding='utf8'))

    def player_guessed_word(self, player_id, args):
        """
        called when a 'player_guessed_word' message is sent from the client
        :param player_id: sender(player) id
        :param args: the score to add (time left on the countdown)
        :return:
        """
        self.score[player_id] += int(args)
        self.next_turn()

    def read_words_from_file(self):
        """
        reads the word list from words.txt
        :return:
        """
        with open('words.txt') as file:
            words = file.readlines()

        # remove whitespace characters like `\n` at the end of each line
        return [x.strip() for x in words]


if __name__ == '__main__':
    Server()
