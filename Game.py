from tkinter import *
from tkinter.colorchooser import askcolor
from tkinter.messagebox import showinfo
from client import *


class Game(object):
    DEFAULT_PEN_SIZE = 5.0
    DEFAULT_COLOR = 'blue'

    def __init__(self, on_game_over):
        self.root = Tk()
        self.on_game_over = on_game_over
        self.client = Client(self.handle_server_action)
        self.client.connect('127.0.0.1', 3000)

        self.root.title('Drawdipy')

        self.guessing = False
        self.drawing = False
        self.word = None
        self.remaining = 0
        self.previous_after = None
        self.round_time_in_seconds = 60

        self.guessing_word_label = Label(self.root, text='guessing_word_label')
        self.guessing_word_label.grid(row=0, column=1, columnspan=1)
        self.guessing_word_label.grid_remove()
        self.guessing_word_input = Entry(self.root, text='guessing_word_input')
        self.guessing_word_input.grid(row=0, column=2, columnspan=1)
        self.guessing_word_input.grid_remove()
        self.guessing_submit_button = Button(self.root, text='Submit', width=10, command=self.submit_guess)
        self.guessing_submit_button.grid(row=0, column=3, columnspan=1)
        self.guessing_submit_button.grid_remove()
        self.guessing_word_input_visible = False

        self.drawing_word_label = Label(self.root, text='drawing_word_label')
        self.drawing_word_label.grid(row=0, column=2, columnspan=1)
        self.drawing_word_label.grid_remove()
        self.drawing_word_label_visible = False

        self.countdown_label = Label(self.root, text='Time Left:')
        self.countdown_label.grid(row=0, column=4, columnspan=1)

        self.canvas = Canvas(self.root, bg='white', width=600, height=600)
        self.canvas.grid(row=1, columnspan=6)

        self.pen_button = Button(self.root, text='Draw', command=self.use_pen, width=10)
        self.pen_button.grid(row=2, column=0)

        self.color_button = Button(self.root, text='Pick Color', command=self.choose_color, width=10)
        self.color_button.grid(row=2, column=1)

        self.eraser_button = Button(self.root, text='Eraser', command=self.use_eraser, width=10)
        self.eraser_button.grid(row=2, column=3)

        self.clear_canvas_button = Button(self.root, text='Clear', command=self.clear_canvas, width=10)
        self.clear_canvas_button.grid(row=2, column=4)

        self.choose_size_button = Scale(self.root, from_=1, to=20, orient=HORIZONTAL)
        self.choose_size_button.grid(row=2, column=5)

        self.pen_button.grid_remove()
        self.color_button.grid_remove()
        self.eraser_button.grid_remove()
        self.clear_canvas_button.grid_remove()
        self.choose_size_button.grid_remove()

        self.old_x = None
        self.old_y = None
        self.line_width = self.choose_size_button.get()
        self.color = self.DEFAULT_COLOR
        self.eraser_on = False
        self.active_button = self.pen_button
        self.canvas.bind('<B1-Motion>', self.paint)
        self.canvas.bind('<ButtonRelease-1>', self.reset)
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_closing)
        self.root.resizable(False, False)
        self.root.mainloop()

    def on_window_closing(self):
        """
        a tkinter window event called when the window is about to close
        :return:
        """
        self.client.close()
        self.root.destroy()
        self.on_game_over()

    def handle_server_action(self, action, args):
        """
        handles a message from the server
        :param action: the action sent from the server
        :param args: the action's arguments
        :return:
        """
        if action == 'canvas_create_line':
            (old_x, old_y, x, y,
             line_width, paint_color,
             capstyle, smooth, splinesteps) = args.split(':')
            self.canvas.create_line(old_x, old_y, x, y,
                                    width=line_width, fill=paint_color,
                                    capstyle=capstyle, smooth=smooth, splinesteps=splinesteps)
        elif action == 'canvas_clear':
            self.canvas.delete("all")
        elif action == 'start_turn_drawing':
            self.init_drawing_turn(args)
        elif action == 'start_turn_guessing':
            self.init_guessing_turn(args)
        elif action == 'game_ended':
            self.game_ended(args)

    def init_guessing_turn(self, word):
        """
        initializes a guessing turn
        :param word: the word to guess
        :return:
        """
        self.word = word
        self.drawing = False
        self.guessing = True
        self.canvas.delete("all")
        self.countdown(self.round_time_in_seconds)
        if self.drawing_word_label_visible:
            self.drawing_word_label_visible = False
            self.drawing_word_label.grid_remove()
            self.pen_button.grid_remove()
            self.color_button.grid_remove()
            self.eraser_button.grid_remove()
            self.clear_canvas_button.grid_remove()
            self.choose_size_button.grid_remove()
        if not self.guessing_word_input_visible:
            self.guessing_word_input_visible = True
            self.guessing_word_input.grid()
            self.guessing_word_label.grid()
            self.guessing_submit_button.grid()

        self.guessing_word_input.delete(0, 'end')
        self.guessing_word_label['text'] = self.word_to_underscores(word)

    def init_drawing_turn(self, word):
        """
        initializes a drawing turn
        :param word: the word to guess
        :return:
        """
        self.drawing = True
        self.guessing = False
        self.canvas.delete("all")
        self.countdown(self.round_time_in_seconds)
        if not self.drawing_word_label_visible:
            self.drawing_word_label_visible = True
            self.drawing_word_label.grid()
            self.pen_button.grid()
            self.color_button.grid()
            self.eraser_button.grid()
            self.clear_canvas_button.grid()
            self.choose_size_button.grid()
        if self.guessing_word_input_visible:
            self.guessing_word_input_visible = False
            self.guessing_word_input.grid_remove()
            self.guessing_word_label.grid_remove()
            self.guessing_submit_button.grid_remove()

        self.drawing_word_label['text'] = word

    def game_ended(self, message):
        """
        ends the game with a win/lose message from the server
        :param message:
        :return:
        """
        self.client.close()
        showinfo('The Game Ended', message)
        self.root.destroy()
        self.on_game_over()

    def submit_guess(self):
        """
        checks the guessers guess and handles success/failure
        :return:
        """
        if self.word == self.guessing_word_input.get():
            self.client.send('player_guessed_word', str(self.remaining))
        else:
            self.guessing_word_input.delete(0, 'end')

    def countdown(self, remaining=None):
        """
        counts down the remaining time for the current turn
        :param remaining: the remaining time for the turn
        :return:
        """
        if remaining is not None:
            # try canceling the previous after call if it exists
            try:
                self.root.after_cancel(self.previous_after)
            except:
                pass
            self.remaining = remaining

        if self.remaining <= 0:
            self.countdown_label.configure(text="time's up!")
            if self.guessing:
                self.client.send('player_guessed_word', '0')
        else:
            self.countdown_label.configure(text="Time Left: %d" % self.remaining)
            self.remaining = self.remaining - 1
            # call countdown again after 1 second
            self.previous_after = self.root.after(1000, self.countdown)

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

    def use_pen(self):
        """
        activates the pen
        :return:
        """
        self.activate_button(self.pen_button)

    def choose_color(self):
        """
        allows choosing a different color using a color picker dialog
        :return:
        """
        self.eraser_on = False
        color = askcolor(color=self.color)[1]

        if color is not None:
            self.color = color

    def use_eraser(self):
        """
        activates the eraser (same as pen but with white color)
        :return:
        """
        self.activate_button(self.eraser_button, eraser_mode=True)

    def clear_canvas(self):
        """
        clears the canvas and notifies the server about the clear
        :return:
        """
        self.canvas.delete("all")
        self.client.send('canvas_clear', '')

    def activate_button(self, some_button, eraser_mode=False):
        """
        activates a button
        :param some_button: the button name
        :param eraser_mode: is it eraser mode
        :return:
        """
        self.active_button.config(relief=RAISED)
        some_button.config(relief=SUNKEN)
        self.active_button = some_button
        self.eraser_on = eraser_mode

    def paint(self, event):
        """
        draw to the canvas
        :param event: the mouse event
        :return:
        """
        if not self.drawing:
            return

        self.line_width = self.choose_size_button.get()
        paint_color = 'white' if self.eraser_on else self.color
        if self.old_x and self.old_y:
            self.canvas.create_line(self.old_x, self.old_y, event.x, event.y,
                                    width=self.line_width, fill=paint_color,
                                    capstyle=ROUND, smooth=TRUE, splinesteps=36)
            self.client.send('canvas_create_line',
                             f'{self.old_x}:{self.old_y}:{event.x}:{event.y}:{self.line_width}:{paint_color}:'
                             f'{ROUND}:{TRUE}:{36}')
        self.old_x = event.x
        self.old_y = event.y

    def reset(self, event):
        """
        resets the x and y values
        :param event:
        :return:
        """
        self.old_x, self.old_y = None, None
