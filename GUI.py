import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from DB_Communication import connect_to_db

from PIL import ImageTk


HEADING1_FONT = ("Open Sans", 16, "bold")
LARGE_FONT = ("Open Sans", 12)
NORMAL_FONT = ("Open Sans", 10)
SMALL_FONT = ("Open Sans", 8)


class ShareToolGUI(tk.Tk):
    """

    """

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, "Share Management Tool")
        tk.Tk.iconbitmap(self, default='./data/img/ShareTool.ico')

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for each_frame in (StartPage, PageOne):

            frame = each_frame(container, self)

            self.frames[each_frame] = frame

            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame(StartPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Frame.config(self)

        # create canvas as container for the image
        canvas_image = tk.Canvas(self, width=500, height=700)

        # load and display the image
        photo_logo = ImageTk.PhotoImage(file="./data/img/ShareTool.ico")
        self.photo_logo = photo_logo
        canvas_image.create_image((250, 500), image=photo_logo, anchor='center')
        canvas_image.place(x=480, y=10, anchor='center')

        # create welcome Label
        label_heading = ttk.Label(self, text="Willkommen im Share Management Tool!", font=HEADING1_FONT)
        label_heading.place(x=480, y=350, anchor='center')

        # create label for connection check
        label_connection_check = ttk.Label(self, font=NORMAL_FONT)
        label_connection_check.place(x=480, y=390, anchor='center')

        # create button to proceed
        button_start_page = ttk.Button(self, text='Start',
                                       command=lambda: messagebox.showinfo("Stay tuned!", "Not implemented yet"))
        button_start_page.place(x=480, y=420, anchor='center')
        button_start_page['state'] = "disabled"

        # check for database connection
        is_connection_successful = change_label_according_to_db_availability(label_connection_check)

        if is_connection_successful:
            button_start_page['state'] = "normal"


class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = ttk.Label(self, text="Page One!", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        button2 = ttk.Button(self, text="Back to Home", command=lambda: controller.show_frame(StartPage))
        button2.pack()


def change_label_according_to_db_availability(label):
    """
    Check the connection to the database and change the label's text in case of success
    :param label: label whose label to be changed
    :return: True or False, depending on accessibility
    """

    db_connection = connect_to_db()

    if db_connection is not None:

        label.config(text="Connection to database successfully initiated!")
        return True
    else:
        messagebox.showerror("Connection Error", "The connection to the database could not be established. "
                                                 "Please check the configuration of the database in db_config.json")
        return False
