from tkinter import *
from tkinter.messagebox import showinfo

import RoomsPage


class EnterCodePage(object):
    def __init__(self, client):
        self.client = client

        self.root = Tk()

        self.root.eval('tk::PlaceWindow . center')
        self.root.title('Enter two factor auth code')

        self.title_label = Label(self.root, text='A two factor auth code was sent to your email')
        self.title_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self.code_label = Label(self.root, text='Code:')
        self.code_label.grid(row=1, column=0, columnspan=1, padx=10, pady=10)
        self.code_input = Entry(self.root)
        self.code_input.grid(row=1, column=1, columnspan=1, padx=10)

        self.submit_code_button = Button(self.root, text='Submit', command=self.submit_code, width=10, padx=10, pady=10)
        self.submit_code_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.root.resizable(False, False)
        self.root.mainloop()

    def submit_code(self):
        """
        submit the code and check if it's correct
        """
        submitted_code = self.code_input.get()
        (origin, action, args) = self.client.send_and_wait('client_two_factor_code', submitted_code)

        if action == 'client_two_factor_code_success':
            self.root.withdraw()
            RoomsPage.RoomsPage(self.client)
        else:
            showinfo("Wrong code", "The code you entered is incorrect")
