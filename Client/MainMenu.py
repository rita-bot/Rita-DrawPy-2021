from tkinter import *
from tkinter.messagebox import showinfo

import LoginPage
import RegisterPage


class MainMenu(object):
    def __init__(self, client):
        self.client = client
        self.root = Tk()

        self.root.eval('tk::PlaceWindow . center')

        self.root.title('DrawPy')

        self.login_button = Button(self.root, text='Login', command=self.login, width=10, padx=10, pady=10)
        self.login_button.pack(fill=X, pady=20, padx=80)

        self.login_button = Button(self.root, text='Register', command=self.register, width=10, padx=10, pady=10)
        self.login_button.pack(fill=X, pady=20, padx=80)

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

    def login(self):
        """
        opens the login page
        :return:
        """
        self.root.withdraw()
        LoginPage.LoginPage(self.client)

    def register(self):
        """
        opens the register page
        :return:
        """
        self.root.withdraw()
        RegisterPage.RegisterPage(self.client)
