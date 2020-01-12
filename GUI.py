import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import DB_Communication
from PIL import ImageTk
import json

# Define some fonts
HEADING1_FONT = ("Open Sans", 16, "bold")
LARGE_FONT = ("Open Sans", 12)
NORMAL_FONT = ("Open Sans", 11)
SMALL_FONT = ("Open Sans", 8)


class ShareToolGUI(tk.Tk):
    """
    Define the basic application.
    Depending on user interaction, show different frames (defined as own classes)
    """

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        # set title and icon
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
        # add optical separator
        self.menu_main.add_separator()

        # add option to customize db cofig
        self.menu_main.add_command(label="Customize DB Config",
                                   command=self.menu_bar_open_custom_db)
        # add optical separator
        self.menu_main.add_separator()

        # add exit command
        self.menu_main.add_command(label="Exit", command=quit)

        self.menubar.add_cascade(label="Main", menu=self.menu_main)

        # create menu for new entries
        self.menu_new = tk.Menu(self.menubar, tearoff=0)
        self.menu_new.add_command(label="Entities", command=self.depends_on_db)
        self.menu_new.add_command(label="Data", command=self.depends_on_db)
        self.menubar.add_cascade(label="New", menu=self.menu_new)

        # create menu for updating entries
        self.menu_update = tk.Menu(self.menubar, tearoff=0)
        self.menu_update.add_command(label="Entities", command=self.depends_on_db)
        self.menu_update.add_command(label="Data", command=self.depends_on_db)
        self.menubar.add_cascade(label="Update", menu=self.menu_update)

        # add menubar to frame
        tk.Tk.config(self, menu=self.menubar)

        # define dictionary for created frames to allow accessing them
        self.frames = {}

        # create one instance of the welcome page and show it
        self.frame_welcome_page = WelcomePage(self.container, self)
        self.frames[WelcomePage] = self.frame_welcome_page
        self.frame_welcome_page.grid(row=0, column=0, sticky='nsew')
        self.show_frame(WelcomePage)

    def show_frame(self, page):
        """
        Show the given page to the user
        :param page: class of page to be shown (page itself has to be in self.frames)
        :return: None
        """
        # get instance of page by class
        frame = self.frames[page]

        # update frame and show it to the user
        frame.update_frame()
        frame.tkraise()

    def show_frame_with_delete(self, page, old_page):
        """
        same as above, additionally delete the old_page
        :param page: class of page to be shown (page itself has to be in self.frames)
        :param old_page: class of page to be deleted (page itself has to be in self.frames)
        :return: None
        """

        # get instance of page by class
        frame = self.frames[page]

        # update frame and show it to the user
        frame.update_frame()
        frame.tkraise()

        # delete the old page
        del(self.frames[old_page])

    def get_db_connection(self):
        return self.db_connection

    def set_db_connection(self, con):
        self.db_connection = con

    def menu_bar_open_status_page(self):
        """
        Display status page in case it exists
        :return: None
        """

        # db_connection is prerequisite for this page
        if self.db_connection is None:
            messagebox.showinfo(title='Not possible yet!',
                                message="Please first ensure the database connection to be established")

        # check whether status page exists already
        elif StatusPage in self.frames.keys():
            self.show_frame(StatusPage)

        # create status page if not
        else:
            self.create_page(StatusPage)
            self.show_frame_with_delete(StatusPage, WelcomePage)

    def create_page(self, page):
        """
        Create a page and add it to self.frames
        :param page: class of page to be created
        :return: None
        """
        frame = page(self.container, self)
        self.frames[page] = frame
        frame.grid(row=0, column=0, sticky='nsew')

    # TODO: has to be replaced stepwise
    def depends_on_db(self):
        """
        ONLY FOR DEVELOPMENT
        """
        if self.db_connection is None:
            messagebox.showinfo(title='Configure DB',
                                message="Please ensure valid db connection before proceed")
        else:
            messagebox.showinfo(title='Stay tuned!',
                                message="Unfortunately not supported yet")

    def menu_bar_open_custom_db(self):
        """
        Opens a frame allowing the user to customize the DB configuration
        Creates page as well if required
        :return: None
        """

        if ConfigDBPage in self.frames.keys():
            self.show_frame(ConfigDBPage)
        else:
            self.create_page(ConfigDBPage)
            self.show_frame(ConfigDBPage)


class BasicPage(tk.Frame):
    """
    Super class for all pages
    """

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Frame.config(self)

        self.controller = controller
        self.parent = parent

        self.db_connection = controller.db_connection

    def get_controller(self):
        return self.controller

    def get_parent(self):
        return self.parent

    def get_db_connection(self):
        return self.db_connection

    def set_db_connection(self, con):
        self.db_connection = con

    def update_frame(self):
        pass


class WelcomePage(BasicPage):

    def __init__(self, parent, controller):

        # call constructor of superclass
        super().__init__(parent, controller)

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

    def change_label_according_to_db_availability(self):
        """
        Check the connection to the database, set the application's connection accordingly and
        change the label's text in case of success
        :return: True or False, depending on accessibility
        """

        self.set_db_connection(DB_Communication.connect_to_db())

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
        """
        Create status page and delete Welcome Page
        :return: None
        """
        self.controller.create_page(StatusPage)
        self.controller.show_frame_with_delete(StatusPage, WelcomePage)

    def update_frame(self):
        """
        Update the frame
        :return: None
        """

        is_connection_successful = self.change_label_according_to_db_availability()

        # button is only active in case of a active db connection
        if is_connection_successful:
            self.button_start_page['state'] = "normal"


class StatusPage(BasicPage):

    def __init__(self, parent, controller):

        # call constructor of superclass
        super().__init__(parent, controller)

        # create heading
        self.label_heading = ttk.Label(self, text="Status of the Share Management Tool", font=HEADING1_FONT)
        self.label_heading.place(x=480, y=50, anchor='center')

        # create heading number of shares
        self.label_heading_no_of_shares = ttk.Label(self, text="Number of managed shares", font=LARGE_FONT)
        self.label_heading_no_of_shares.place(x=200, y=125, anchor='center')

        # create label for number of shares
        self.label_no_of_shares = ttk.Label(self, text="150", font=NORMAL_FONT)
        self.label_no_of_shares.place(x=200, y=150, anchor='center')

        # create heading number of shares in backlog
        self.label_heading_no_of_shares_backlog = ttk.Label(self, text="Number of shares in backlog", font=LARGE_FONT)
        self.label_heading_no_of_shares_backlog.place(x=200, y=275, anchor='center')

        # create label for number of shares in backlog
        self.label_no_of_shares_backlog = ttk.Label(self, text="-", font=NORMAL_FONT)
        self.label_no_of_shares_backlog.place(x=200, y=300, anchor='center')
        # TODO: integrate in update Function

        # create heading for number of buy alarms
        self.label_heading_no_of_buy_alarms = ttk.Label(self, text="Number of buy alarms", font=LARGE_FONT)
        self.label_heading_no_of_buy_alarms.place(x=200, y=425, anchor='center')

        # create label for number of shares in backlog
        self.label_no_of_buy_alarms = ttk.Label(self, text="-", font=NORMAL_FONT)
        self.label_no_of_buy_alarms.place(x=200, y=450, anchor='center')
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
        # TODO: integrate in update Function

        # create label for number of incomplete instances
        self.label_no_of_incomplete_instances = ttk.Label(self, text="-", font=NORMAL_FONT)
        self.label_no_of_incomplete_instances.place(x=700, y=450, anchor='center')
        # TODO: integrate in update Function

    def update_frame(self):
        """
        Update all instaces using values from the db
        :return: None
        """

        # update number of shares
        self.change_label_number_of_shares()

    def change_label_number_of_shares(self):
        """
        Get the total number of shares that are currently in the database
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


class ConfigDBPage (BasicPage):
    """
    Page allows user to see the current values of the db configuration and change them if required
    """

    def __init__(self, parent, controller):

        # call constructor of superclass
        super().__init__(parent, controller)

        # create heading
        self.label_heading = ttk.Label(self, text="Customize DB Configuration", font=HEADING1_FONT)
        self.label_heading.place(x=480, y=50, anchor='center')

        # create label for db name
        self.label_db_name = ttk.Label(self, text="Database name", font=NORMAL_FONT)
        self.label_db_name.place(x=100, y=150, anchor='center')

        # create input field for db name
        self.entry_db_name = ttk.Entry(self)
        self.entry_db_name.place(x=300, y=150, anchor='center')

        # create label for host name
        self.label_hostname = ttk.Label(self, text="Hostname", font=NORMAL_FONT)
        self.label_hostname.place(x=100, y=250, anchor='center')

        # create input field for host name
        self.entry_hostname = ttk.Entry(self)
        self.entry_hostname.place(x=300, y=250, anchor='center')

        # create label for user name
        self.label_user_name = ttk.Label(self, text="User name", font=NORMAL_FONT)
        self.label_user_name.place(x=550, y=150, anchor='center')

        # create input field for user name
        self.entry_user_name = ttk.Entry(self)
        self.entry_user_name.place(x=750, y=150, anchor='center')

        # create label for password
        self.label_pw = ttk.Label(self, text="Password", font=NORMAL_FONT)
        self.label_pw.place(x=550, y=250, anchor='center')

        # create input field for user name
        self.entry_pw = ttk.Entry(self, show='*')
        self.entry_pw.place(x=750, y=250, anchor='center')

        # create button for connection check
        self.button_connection_check = ttk.Button(self, text="Connection Check", command=self.check_connection)
        self.button_connection_check.place(x=400, y=350, anchor='center')

        # create button for save configuration
        self.button_save_connection = ttk.Button(self, text="Save Configuration", command=self.save_config_to_file)
        self.button_save_connection.place(x=550, y=350, anchor='center')

        # create button for back to status page
        self.button_go_to_welcome_page = ttk.Button(self, text="Go Back to Welcome Page",
                                                    command=lambda: self.get_controller()
                                                    .show_frame_with_delete(WelcomePage, ConfigDBPage))
        self.button_go_to_welcome_page.place(x=475, y=425, anchor='center')

    def update_frame(self):
        """
        Update the frame
        :return: None
        """

        # read the cofig JSON and load it as JSON
        with open('./data/db_config.json', encoding='utf-8') as F:
            dict_db_params = json.load(F)
        F.close()

        # display values from config file in entries
        self.entry_db_name.insert(tk.END, dict_db_params["db_name"])
        self.entry_hostname.insert(tk.END, dict_db_params["host"])
        self.entry_user_name.insert(tk.END, dict_db_params["user"])
        self.entry_pw.insert(tk.END, dict_db_params["password"])

    def save_config_to_file(self):
        """
        save the current configuration specified in the UI to the config file
        :return: None
        """

        # get all connection parameters
        user_name = self.entry_user_name.get()
        password = self.entry_pw.get()
        hostname = self.entry_hostname.get()
        db_name = self.entry_db_name.get()

        # create a JSON string
        db_config = '{"db_name": "' + db_name + '", ' \
                    '"user" : "' + user_name + '", ' \
                    '"host" : "' + hostname + '", ' \
                    '"password": "' + password + '"}'

        # write the JSON to the config file
        with open('./data/db_config.json', 'w', encoding='utf-8') as F:
            F.write(str(db_config))
        F.close()

    def check_connection(self):
        """
        check whether the currently specified configuration gives access to the database
        and give visual feedback to the user.
        :return: None
        """

        db_connection = DB_Communication.connect_to_db_with_params(db_name=self.entry_db_name.get(),
                                                                   host=self.entry_hostname.get(),
                                                                   user=self.entry_user_name.get(),
                                                                   password=self.entry_pw.get())

        if db_connection is None:
            messagebox.showerror(title="No Connection",
                                 message="It's not possible to get a connection to the database"
                                         " with the chosen parameters. Please try again!")
        else:
            messagebox.showinfo(title="Connection initialized",
                                message="Connection to database is successfully initialized. \n"
                                        "You can now navigate back to the Welcome Page and start the application.")
