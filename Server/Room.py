import random
import uuid

import Database


class Room:
    def __init__(self, name):
        self.name = name
        self.id = str(uuid.uuid4())
        self.clients = {}
        self.clients_emails = {}
        self.score = {}
        self.round = 0
        self.rounds_until_finish = 2
        self.drawing_player = None
        self.words = self.read_words_from_file()
        self.word = None

    def join(self, client_email, client_id, client):
        """
        join room and refresh room info
        :param client_email: the Client email
        :param client_id: the Client's id
        """
        self.clients[client_id] = client
        self.clients_emails[client_id] = client_email
        self.notify_other_clients(client_id, 'refresh_room_info')

    def leave(self, client_id):
        """
        leave room
        :param client_id: the Client's id
        """
        self.clients.pop(client_id)
        self.clients_emails.pop(client_id)

    def handle_client_action(self, client_socket, client_id, action, args):
        """
        handles an action sent from the Client
        :param client_socket: the Client socket
        :param client_id: the Client's id
        :param action: the Client's action
        :param args: the Client's action's arguments
        """
        if action == 'start_game':
            self.start_game()
        elif action == 'player_guessed_word':
            self.player_guessed_word(client_socket, client_id, args)
        elif action == 'guess_time_is_up':
            self.next_turn()
        elif action == 'get_room_info':
            self.get_room_info(client_socket, client_id, args)
        else:
            self.notify_other_clients(client_id, action, args)

    def send(self, client_socket, client_id, action, args=''):
        """
        send clients' id
        :param client_socket: the Client socket
        :param client_id: the Client id
        :param action: the action to send a message
        :param args: the action's arguments
        """
        client_socket.send(bytes(f'{client_id},{action},{args}\n', encoding='utf8'))

    def notify_other_clients(self, client_id, action, args=''):
        """
        notify all other clients besides client_id of an action
        :param client_id: the Client id
        :param action: the action to notify of
        :param args: the action's arguments
        """
        for id in self.clients.keys():
            if id == client_id:
                continue

            client = self.clients[id]
            self.send(client, client_id, action, args)

    def read_words_from_file(self):
        """
        reads the word list from words.txt
        :return:
        """
        with open('./words.txt') as file:
            words = file.readlines()

        # remove whitespace characters like `\n` at the end of each line
        return [x.strip() for x in words]

    def start_game(self):
        """
        starts the game in the Server - resets score and rounds
        :return:
        """
        self.round = 0
        self.drawing_player = None
        self.score = {}

        for client_id in self.clients:
            self.score[client_id] = 0

        self.notify_all('game_starting')
        self.next_turn()

    def notify_all(self, action, args=''):
        """
        notify all the clients the game has started
        :return:
        """
        for client_id in self.clients:
            client = self.clients[client_id]
            self.send(client, client_id, action, args)

    def set_next_drawing(self):
        """
        sets the next player
        :return:
        """
        clients_list = list(self.clients)
        if self.drawing_player is None:
            self.drawing_player = clients_list[0]
        else:
            drawing_index = clients_list.index(self.drawing_player)

            # if it's the last index, it means we finished a round and need to start from the first Client
            if drawing_index == len(clients_list) - 1:
                self.drawing_player = clients_list[0]
                self.round += 1
            else:
                self.drawing_player = clients_list[drawing_index + 1]

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

        self.word = self.get_word()

        for client_id in self.clients:
            client = self.clients[client_id]
            if client_id == self.drawing_player:
                client.send(bytes(f'{client_id},start_turn_drawing,{self.word}\n', encoding='utf8'))
            else:
                client.send(
                    bytes(f'{client_id},start_turn_guessing,{self.word_to_underscores(self.word)}\n', encoding='utf8'))

    def word_to_underscores(self, word):
        """
        converts a word to underscores - hello turns to _ _ _ _ _
        :param word: the word to convert
        :return:
        """
        new_word = ''

        for (index, letter) in enumerate(word):
            if letter == ' ':
                new_word += ' '
            elif index == len(word) - 1:
                new_word += '_'
            else:
                new_word += '_ '

        return new_word

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
        emails = []
        scores = []
        for client_id in self.clients:
            emails.append(self.clients_emails[client_id])
            scores.append(self.score[client_id])

        db_connection = Database.DatabaseConnection()
        db_connection.add_scores(emails, scores)
        db_connection.close_connection()
        winner = self.get_winner()

        if winner == 'tie':
            self.notify_other_clients('', 'game_ended', 'tie')
            return

        for client_id in self.clients:
            client = self.clients[client_id]
            score = self.score[client_id]
            if client_id == winner:
                client.send(bytes(f'{client_id},game_ended,you won! your score was: {score}\n', encoding='utf8'))
            else:
                client.send(bytes(f'{client_id},game_ended,you lost :( your score was: {score}\n', encoding='utf8'))

    def player_guessed_word(self, client_socket, player_id, args):
        """
        called when a 'player_guessed_word' message is sent from the Client
        :param client_socket: the Client socket
        :param player_id: sender(player) id
        :param args: the score to add (time left on the countdown)
        :return:
        """
        (guess, score_to_add) = args.split(':')
        if self.word == guess:
            self.score[player_id] += int(score_to_add)
            self.next_turn()

    def get_room_info(self, client_socket, client_id, args):
        """
        after the game has finished get the room info +++++++
        :return:
        """
        room_info = f"{self.name}:"
        index = 0
        for id in self.clients:
            room_info += self.clients_emails[id]

            if id == client_id:
                room_info += ' (You)'

            if len(list(self.clients)) - 1 != index:
                room_info += "-"

            index += 1

        self.send(client_socket, client_id, 'room_info', room_info)
