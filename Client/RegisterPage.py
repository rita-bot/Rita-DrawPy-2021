from tkinter import *
from tkinter.messagebox import showinfo

import MainMenu
import LoginPage


class RegisterPage(object):
    def __init__(self, client):
        self.client = client

        self.root = Tk()

        self.root.eval('tk::PlaceWindow . center')
        self.root.title('Register')

        self.email_label = Label(self.root, text='Email:')
        self.email_label.grid(row=0, column=0, columnspan=1, padx=10, pady=10)
        self.email_input = Entry(self.root, text='Email')
        self.email_input.grid(row=0, column=1, columnspan=1, padx=10)

        self.password_label = Label(self.root, text='Password:')
        self.password_label.grid(row=1, column=0, columnspan=1, padx=10, pady=10)
        self.password_input = Entry(self.root, text='Password')
        self.password_input.grid(row=1, column=1, columnspan=1, padx=10)

        self.login_button = Button(self.root, text='Register', command=self.register, width=10, padx=10, pady=10)
        self.login_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.about_button = Button(self.root, text='Back', command=self.back, width=10, padx=10, pady=10)
        self.about_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.root.resizable(False, False)
        self.root.mainloop()

    def back(self):
        """
        goes back
        :return:
        """
        self.root.withdraw()
        MainMenu.MainMenu(self.client)

    def register(self):
        """
        Tries to register a user in the server, if it succeeds - goes to the login page
        :return:
        """
        print("Registering as " + self.email_input.get())
        email = self.email_input.get()
        password = self.password_input.get()
        (origin, action, args) = self.client.send_and_wait('client_register', f"{email}:{password}")

        if action == 'client_register_success':
            self.root.withdraw()
            LoginPage.LoginPage(self.client)
        else:
            showinfo("Registration failed", args)
