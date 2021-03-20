from tkinter import *

import RoomsPage


class ScoresPage(object):
    def __init__(self, client):
        self.client = client
        self.root = Tk()

        self.root.eval('tk::PlaceWindow . center')

        self.root.title('DrawPy - Scores')

        self.rooms_label = Label(self.root, text='Scores:', width=25, padx=10, pady=10)
        self.rooms_label.pack(fill=X, pady=20, padx=80)

        self.draw_scores()

        self.back_button = Button(self.root, text='Back', command=self.back, width=25, padx=10,
                                  pady=10)
        self.back_button.pack(fill=X, pady=20, padx=80)

        self.root.resizable(False, False)
        self.root.mainloop()

    def draw_scores(self):
        (origin, action, args) = self.client.send_and_wait('get_high_scores')

        if args == '':
            empty_label = Label(self.root, text='No scores yet',
                                width=25, padx=10,
                                pady=10)
            empty_label.pack(fill=X, pady=20, padx=80)
            return

        for score in args.split('|'):
            score_label = Label(self.root, text=score,
                                width=25, padx=10,
                                pady=5)
            score_label.pack(fill=X, pady=5, padx=80)

    def back(self):
        """
        goes back
        :return:
        """
        self.root.withdraw()
        RoomsPage.RoomsPage(self.client)
