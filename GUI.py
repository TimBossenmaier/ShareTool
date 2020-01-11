import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import DB_Communication

from PIL import ImageTk


HEADING1_FONT = ("Open Sans", 16, "bold")
LARGE_FONT = ("Open Sans", 12)
NORMAL_FONT = ("Open Sans", 11)
SMALL_FONT = ("Open Sans", 8)


class ShareToolGUI(tk.Tk):
    """

    """

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, "Share Management Tool")
        tk.Tk.iconbitmap(self, default='./data/img/ShareTool.ico')

        self.db_connection = None

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # create container for the menu bar
        self.menubar = tk.Menu(self.container)

        # create the main menu with its entries
        self.menu_main = tk.Menu(self.menubar, tearoff=0)
        self.menu_main.add_command(label="Status page", command=self.menu_bar_open_status_page)
        self.menu_main.add_command(label="Help",
                                   command=lambda: messagebox.showinfo(title='Stay tuned!',
                                                                       message="Unfortunately not supported yet"))
        # add optical seperator
        self.menu_main.add_separator()

        # add option to check connectivity
        self.menu_main.add_command(label="Check Connection to DB",
                                   command=lambda: messagebox.showinfo(title='Stay tuned!',
                                                                       message="Unfortunately not supported yet"))

        # add option to customize db cofig
        self.menu_main.add_command(label="Customize DB Config",
                                   command=lambda: messagebox.showinfo(title='Stay tuned!',
                                                                       message="Unfortunately not supported yet"))
        # add optical seperator
        self.menu_main.add_separator()

        # add exit command
        self.menu_main.add_command(label="Exit", command=quit)

        self.menubar.add_cascade(label="Main", menu=self.menu_main)

        # create menu for new entries
        self.menu_new = tk.Menu(self.menubar, tearoff=0)
        self.menu_new.add_command(label="Entities",
                                  command=lambda: messagebox.showinfo(title='Stay tuned!',
                                                                      message="Unfortunately not supported yet"))
        self.menu_new.add_command(label="Data",
                                  command=lambda: messagebox.showinfo(title='Stay tuned!',
                                                                      message="Unfortunately not supported yet"))
        self.menubar.add_cascade(label="New", menu=self.menu_new)

        # create menu for updating entries
        self.menu_update = tk.Menu(self.menubar, tearoff=0)
        self.menu_update.add_command(label="Entities",
                                     command=lambda: messagebox.showinfo(title='Stay tuned!',
                                                                         message="Unfortunately not supported yet"))
        self.menu_update.add_command(label="Data",
                                     command=lambda: messagebox.showinfo(title='Stay tuned!',
                                                                         message="Unfortunately not supported yet"))
        self.menubar.add_cascade(label="Update", menu=self.menu_update)

        # add menubar to frame
        tk.Tk.config(self, menu=self.menubar)

        self.frames = {}

        self.frame_welcome_page = WelcomePage(self.container, self)

        self.frames[WelcomePage] = self.frame_welcome_page

        self.frame_welcome_page.grid(row=0, column=0, sticky='nsew')

        self.show_frame(WelcomePage)

    def show_frame(self, page):
        frame = self.frames[page]
        if page is not WelcomePage and self.db_connection is not None:
            frame.update_frame(controller=self)
        frame.tkraise()

    def show_frame_with_delete(self, page, old_page):

        frame = self.frames[page]
        if page is not WelcomePage:
            frame.update_frame()
        frame.tkraise()
        del(self.frames[old_page])

    def get_db_connection(self):
        return self.db_connection

    def set_db_connection(self, con):
        self.db_connection = con

    def menu_bar_open_status_page(self):
        if self.db_connection is None:
            messagebox.showinfo(title='Not possible yet!',
                                message="Please ensure first the database connection to be established")
        else:
            self.show_frame(StatusPage)

    def create_page(self, page):
        frame = page(self.container, self)
        self.frames[page] = frame
        frame.grid(row=0, column=0, sticky='nsew')


class WelcomePage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Frame.config(self)

        self.controller = controller
        self.parent = parent

        self.db_connection = controller.get_db_connection

        # create canvas as container for the image
        self.canvas_image = tk.Canvas(self, width=500, height=700)

        # load and display the image
        self.photo_logo = ImageTk.PhotoImage(file="./data/img/ShareTool.ico")
        self.canvas_image.create_image((250, 500), image=self.photo_logo, anchor='center')
        self.canvas_image.place(x=480, y=10, anchor='center')

        # create welcome Label
        self.label_heading = ttk.Label(self, text="Welcome to the Share Management Tool!", font=HEADING1_FONT)
        self.label_heading.place(x=480, y=350, anchor='center')

        # create label for connection check
        self.label_connection_check = ttk.Label(self, font=NORMAL_FONT)
        self.label_connection_check.place(x=480, y=390, anchor='center')

        # create button to proceed
        self.button_start_page = ttk.Button(self, text='Start', command=self.command_start_button)
        self.button_start_page.place(x=480, y=420, anchor='center')
        self.button_start_page['state'] = "disabled"

        # check for database connection
        self.is_connection_successful = self.change_label_according_to_db_availability()

        # button is only active in case of a active db connection
        if self.is_connection_successful:
            self.button_start_page['state'] = "normal"

    def change_label_according_to_db_availability(self):
        """
        Check the connection to the database, set the application's connection accordingly and
        change the label's text in case of success
        :param controller: reference to application
        :param label: label whose label to be changed
        :return: True or False, depending on accessibility
        """

        self.db_connection = DB_Communication.connect_to_db()

        if self.controller.get_db_connection() is None:
            self.controller.set_db_connection(self.db_connection)

        if self.controller.get_db_connection() is not None:

            self.label_connection_check.config(text="Connection to database successfully initiated!")
            return True
        else:
            messagebox.showerror("Connection Error", "The connection to the database could not be established. "
                                                     "Please check the configuration under Main -> Customize DB Config")
            self.label_connection_check.config(text="Please check the configuration under Main -> Customize DB Config")
            return False

    def command_start_button(self):
        self.controller.create_page(StatusPage)
        self.controller.show_frame_with_delete(StatusPage,WelcomePage)


class StatusPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.controller = controller
        self.parent = parent

        self.db_connection = controller.get_db_connection()

        # create heading
        self.label_heading = ttk.Label(self, text="Status of the Share Management Tool", font=HEADING1_FONT)
        self.label_heading.place(x=480, y=50, anchor='center')

        # create heading number of shares
        self.label_heading_no_of_shares = ttk.Label(self, text="Number of managed shares", font=LARGE_FONT)
        self.label_heading_no_of_shares.place(x=200, y=125, anchor='center')

        # create label for number of shares
        self.label_no_of_shares = ttk.Label(self, text="150", font=NORMAL_FONT)
        self.label_no_of_shares.place(x=200, y=150, anchor='center')

        # create heading number of shares
        self.label_heading_no_of_shares_backlog = ttk.Label(self, text="Number of shares in backlog", font=LARGE_FONT)
        self.label_heading_no_of_shares_backlog.place(x=200, y=425, anchor='center')

        # create label for number of shares
        self.label_no_of_shares_backlog = ttk.Label(self, text="-", font=NORMAL_FONT)
        self.label_no_of_shares_backlog.place(x=200, y=450, anchor='center')

        # TODO: integrate in update Function

        # create heading number of incomplete instances
        self.label_heading_last_update = ttk.Label(self, text="Last automatic update", font=LARGE_FONT)
        self.label_heading_last_update.place(x=700, y=125, anchor='center')

        # create label for number of incomplete instances
        self.label_last_update = ttk.Label(self, text="-", font=NORMAL_FONT)
        self.label_last_update.place(x=700, y=150, anchor='center')

        # TODO: integrate in update Function

        # create heading number of incomplete instances
        self.label_heading_no_of_incomplete_instances = ttk.Label(self, text="Number of incomplete instances",
                                                                  font=LARGE_FONT)
        self.label_heading_no_of_incomplete_instances.place(x=700, y=425, anchor='center')

        # create label for number of incomplete instances
        self.label_no_of_incomplete_instances = ttk.Label(self, text="-", font=NORMAL_FONT)
        self.label_no_of_incomplete_instances.place(x=700, y=450, anchor='center')

        # TODO: integrate in update Function

    def change_label_number_of_shares(self):
        """
        Get the total number of shares that are currently in the database
        :param label: label whose label to be changed
        :return: True or False, depending on the query's success
        """

        db_connection = self.db_connection

        if db_connection is not None:

            sql_cursor = db_connection.cursor()

            number_of_shares = DB_Communication.get_total_number_of_shares(sql_cursor)

            if number_of_shares is not None:
                self.label_no_of_shares.config(text=number_of_shares)
                return True
        else:
            messagebox.showerror("Query Error", "The query could not be performed successfully. "
                                                "Please check the connection and the query code.")
            return False

    def update_frame(self):
        # update number of shares
        # TODO: Remove if clause after development
        self.db_connection = self.controller.get_db_connection()

        if self.db_connection is not None:
            self.change_label_number_of_shares()
        else:
            print("No DB")