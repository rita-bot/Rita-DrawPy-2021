from tkinter import *
from tkinter.messagebox import showinfo
from Game import *


class MainMenu(object):
    def __init__(self):
        self.root = Tk()

        self.root.title('DrawPy')

        self.start_button = Button(self.root, text='Play', command=self.start, width=10, padx=10, pady=10)
        self.start_button.pack(fill=X, pady=20, padx=80)

        self.about_button = Button(self.root, text='About', command=self.about, width=10, padx=10, pady=10)
        self.about_button.pack(fill=X, pady=20, padx=80)

        self.quit_button = Button(self.root, text='Quit', command=self.quit, width=10, padx=10, pady=10)
        self.quit_button.pack(fill=X, pady=20, padx=80)

        self.root.resizable(False, False)
        self.root.mainloop()

    def about(self):
        """
        opens an about info messagebox
        :return:
        """
        showinfo("About Drawdipy", "Drawdipy is a multiplayer drawing game\n"
                                   "built with Python 3 (Tkinter + Sockets)\n"
                                   "Made by Rita Paripsky")

    def start(self):
        """
        starts the game
        :return:
        """
        self.root.withdraw()
        Game(self.show)

    def show(self):
        """
        shows the mainmenu window
        :return:
        """
        self.root.deiconify()

    def quit(self):
        """
        quits the program
        :return:
        """
        exit()