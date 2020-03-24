import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from ISIN_Validator import is_isin_valid
import DB_Communication
from PIL import ImageTk
import json
import pandas as pd
import datetime as dt

# Define some fonts
HEADING1_FONT = ("Open Sans", 16, "bold")
LARGE_FONT = ("Open Sans", 12)
NORMAL_FONT = ("Open Sans", 11)
SMALL_FONT = ("Open Sans", 8)


class AutocompleteCombobox(ttk.Combobox):
    """
        Class realizes an Combobox with autocomplete function
        reference to: https://mail.python.org/pipermail/tkinter-discuss/2012-January/003041.html
    """

    def __init__(self, *args, **kwargs):

        # call super constructor
        super().__init__(*args, **kwargs)

        self._completion_list = None
        self._hits = []
        self._hit_index = 0
        self.position = 0
        self.bind('<KeyRelease>', self.handle_keyrelease)

    def set_completion_list(self, completion_list):
        """
        Use completion list as drop down selection menu
        :param completion_list: list of all possible values
        :return: None
        """
        self._completion_list = sorted(completion_list, key=str.lower)
        self['values'] = self._completion_list  # set up the popup menu

    def autocomplete(self, delta=0):
        """
        Autocomplete the Combobox, delta may be -1/0/1 to cycle through possible hits.
        :param delta:
        :return: None
        """

        # need to delete selection otherwise current position would be fixed
        if delta:
            self.delete(self.position, tk.END)

        # set position to end, so selection starts where text entry ends
        else:
            self.position = len(self.get())

        # collect hits
        _hits = []

        for element in self._completion_list:
            # Match case insensitively
            if element.lower().startswith(self.get().lower()):
                _hits.append(element)

        # keep list only if it is different
        if _hits != self._hits:
            self._hit_index = 0
            self._hits = _hits

        # allow cycling only if the list is already known
        if _hits == self._hits and self._hits:
            self._hit_index = (self._hit_index + delta) % len(self._hits)
            # self.current(self._hit_index)

        # perform auto completion
        if self._hits:
            self.delete(0, tk.END)
            self.insert(0, self._hits[self._hit_index])
            self.select_range(self.position, tk.END)

    def handle_keyrelease(self, event):
        """
        Event handler for the key release event
        :param event: key release event
        :return: None
        """

        if event.keysym == "BackSpace":
            self.delete(self.index(tk.INSERT), tk.END)
            self.position = self.index(tk.END)

        if event.keysym == "Left":
            if self.position < self.index(tk.END):
                self.delete(self.position, tk.END)
            else:
                self.position = self.position - 1
                self.delete(self.position, tk.END)

        if event.keysym == "Right":
            self.position = self.index(tk.END)

        if len(event.keysym) == 1:
            self.autocomplete()

            # display all values that match the current input
            # self.config(values=list(self._hits))


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

        # create menu for new data entries
        self.menu_insert_data = tk.Menu(self.menubar, tearoff=0)
        self.menu_insert_data.add_command(label="Cashflow", command=self.menu_bar_open_create_cashflows)
        self.menu_insert_data.add_command(label='Leverages', command=self.menu_bar_open_create_leverages)
        self.menu_insert_data.add_command(label="Profits", command=self.menu_bar_open_create_profits)
        self.menu_insert_data.add_command(label="ROAs", command=self.menu_bar_open_create_roas)

        # create menu for new entries
        self.menu_new = tk.Menu(self.menubar, tearoff=0)
        self.menu_new.add_command(label="Entities", command=self.menu_bar_open_create_entities)
        self.menu_new.add_cascade(label="Data", menu=self.menu_insert_data)
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

    def get_db_connection(self):
        return self.db_connection

    def set_db_connection(self, con):
        self.db_connection = con

    def get_frames(self):
        return self.frames

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
        del (self.frames[old_page])

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

    def menu_bar_open_create_entities(self):
        """
        Opens a frame allowing the user to create new entities
        Creates page as well if required
        :return: None
        """

        # db_connection is prerequisite for this page
        if self.db_connection is None:
            messagebox.showinfo(title='Not possible yet!',
                                message="Please first ensure the database connection to be established")

        # check whether CreateEntitiesPage exists already
        elif CreateEntitiesPage in self.frames.keys():
            self.show_frame(CreateEntitiesPage)

        # create CreateEntitiesPage if not
        else:
            self.create_page(CreateEntitiesPage)
            self.show_frame(CreateEntitiesPage)

    def menu_bar_open_create_profits(self):
        """
        Opens a frame allowing the user to create new profit entries
        Creates page as well if required
        :return: None
        """

        # db_connection is prerequisite for this page
        if self.db_connection is None:
            messagebox.showinfo(title='Not possible yet!',
                                message="Please first ensure the database connection to be established")

        # check whether InsertProfitsPage exists already
        elif InsertProfitsPage in self.frames.keys():
            self.show_frame(InsertProfitsPage)

        # create InsertProfitsPage if not
        else:
            self.create_page(InsertProfitsPage)
            self.show_frame(InsertProfitsPage)

    def menu_bar_open_create_cashflows(self):
        """
        Opens a frame allowing the user to create new cashflow entries
        Creates page as well if required
        :return: None
        """

        # db_connection is prerequisite for this page
        if self.db_connection is None:
            messagebox.showinfo(title='Not possible yet!',
                                message="Please first ensure the database connection to be established")

        # check whether InsertCashflowPage exists already
        elif InsertCashflowPage in self.frames.keys():
            self.show_frame(InsertCashflowPage)

        # create InsertCashflowPage if not
        else:
            self.create_page(InsertCashflowPage)
            self.show_frame(InsertCashflowPage)

    def menu_bar_open_create_roas(self):
        """

        Opens a frame allowing the user to create new ROA entries
        Creates page as well if required
        :return: None
        """

        # db_connection is prerequisite for this page
        if self.db_connection is None:
            messagebox.showinfo(title='Not possible yet!',
                                message='Please first ensure the database connection to be established')

        # check whether InsertROAPage exists already
        elif InsertROAPage in self.frames.keys():
            self.show_frame(InsertROAPage)

        # create InsertROAPage if not
        else:
            self.create_page(InsertROAPage)
            self.show_frame(InsertROAPage)

    def menu_bar_open_create_leverages(self):
        """

        Opens a frame allowing the user to create new leverage entries
        Creates page as well if required
        :return: None
        """

        # db_connection is prerequisite for this page
        if self.db_connection is None:
            messagebox.showinfo(title='Not possible yet!',
                                message='Please first ensure the database connection to be established')

        # check whether InsertROAPage exists already
        elif InsertROAPage in self.frames.keys():
            self.show_frame(InsertLeveragePage)

        # create InsertROAPage if not
        else:
            self.create_page(InsertLeveragePage)
            self.show_frame(InsertLeveragePage)


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
        # get latest db_connection
        self.set_db_connection(self.get_controller().get_db_connection())

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


class ConfigDBPage(BasicPage):
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
        self.button_go_to_welcome_page = ttk.Button(self, text="Go Back",
                                                    command=self.show_available_frame)
        self.button_go_to_welcome_page.place(x=475, y=425, anchor='center')

    def update_frame(self):
        """
        Update the frame
        :return: None
        """

        # read the config JSON and load it as JSON
        with open('./data/db_config.json', encoding='utf-8') as F:
            dict_db_params = json.load(F)
        F.close()

        # reset entries in case frame gets reopened
        self.entry_db_name.delete(0, tk.END)
        self.entry_hostname.delete(0, tk.END)
        self.entry_user_name.delete(0, tk.END)
        self.entry_pw.delete(0, tk.END)

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
                                         " with the chosen parameters. \n The connection has not changed. \n"
                                         "Please try again!")
        else:
            messagebox.showinfo(title="Connection initialized",
                                message="Connection to database is successfully initialized. \n"
                                        "You can now navigate back to the Welcome Page and start the application.")
            self.db_connection = db_connection

            # pass db_connection to controller
            self.controller.set_db_connection(self.db_connection)

    def show_available_frame(self):
        """
        shows the WelcomePage if it's available, otherwise StatusPage is displayed (one of both is always available)
        available pages depend on user behavior
        :return: None
        """

        controller = self.get_controller()
        list_curr_frames = controller.get_frames()

        if WelcomePage in list_curr_frames:

            controller.show_frame_with_delete(WelcomePage, ConfigDBPage)
        else:
            controller.show_frame_with_delete(StatusPage, ConfigDBPage)


class CreateEntitiesPage(BasicPage):
    """
    Page allows user to create new entries for company and share
    """

    def __init__(self, parent, controller):

        # call constructor of superclass
        super().__init__(parent, controller)

        # data frame of sectors
        self.df_sectors = pd.DataFrame(columns=['ID', 'sector_name'])

        # data frame of countries
        self.df_countries = pd.DataFrame(columns=['ID', 'country_name'])

        # data frame of categories
        self.df_categories = pd.DataFrame(columns=['ID', 'category_name'])

        # data frame of currencies
        self.df_currencies = pd.DataFrame(columns=['ID', 'currency_name'])

        # id of the created company (referenced from shares)
        self.new_company_id = None

        # comment for share
        self.comment = ""

        # create heading
        self.label_heading = ttk.Label(self, text="Create new entities", font=HEADING1_FONT)
        self.label_heading.place(x=480, y=50, anchor='center')

        # create heading New Company
        self.label_heading_new_company = ttk.Label(self, text="New Company", font=LARGE_FONT)
        self.label_heading_new_company.place(x=100, y=150, anchor='center')

        # create label for name of company
        self.label_company_name = ttk.Label(self, text="company name", font=NORMAL_FONT)
        self.label_company_name.place(x=125, y=200, anchor='center')

        # create entry for name of company
        self.entry_company_name = ttk.Entry(self)
        self.entry_company_name.place(x=250, y=200, anchor='center')

        # create label for country
        self.label_country = ttk.Label(self, text="country", font=NORMAL_FONT)
        self.label_country.place(x=350, y=200, anchor='center')

        # create combobox for country
        self.combobox_country = AutocompleteCombobox(self, width=25)
        self.combobox_country.place(x=475, y=200, anchor='center')

        # create label for sector
        self.label_sector = ttk.Label(self, text="sector", font=NORMAL_FONT)
        self.label_sector.place(x=625, y=200, anchor='center')

        # create label for combobox
        self.combobox_sector = AutocompleteCombobox(self, width=35)
        self.combobox_sector.place(x=775, y=200, anchor='center')

        # create button to create company in DB
        self.button_new_company = ttk.Button(self, text="Create company in DB", command=self.create_new_company_in_db)
        self.button_new_company.place(x=200, y=250, anchor='center')

        # create heading for new share
        self.label_heading_new_share = ttk.Label(self, text="New Share", font=LARGE_FONT)
        self.label_heading_new_share.place(x=100, y=350, anchor='center')

        # create label for isin
        self.label_isin = ttk.Label(self, text="ISIN", font=NORMAL_FONT)
        self.label_isin.place(x=145, y=400, anchor='center')

        # create entry for isin
        self.entry_isin = ttk.Entry(self)
        self.entry_isin.place(x=250, y=400, anchor='center')

        # create label for category
        self.label_category = ttk.Label(self, text="Category", font=NORMAL_FONT)
        self.label_category.place(x=375, y=400, anchor='center')

        # create combobox for category
        self.combobox_category = AutocompleteCombobox(self, width=15)
        self.combobox_category.place(x=475, y=400, anchor='center')

        # create label for currency
        self.label_currency = ttk.Label(self, text='Currency', font=NORMAL_FONT)
        self.label_currency.place(x=625, y=400, anchor='center')

        # create combobox for currency
        self.combobox_currency = AutocompleteCombobox(self, width=25)
        self.combobox_currency.place(x=775, y=400, anchor='center')

        # create button for adding a comment
        self.button_add_comment = ttk.Button(self, text="Add comment", command=self.create_comment_dialog)
        self.button_add_comment.place(x=200, y=450, anchor='center')

        # create button for inserting share into db
        self.button_new_share = ttk.Button(self, text="Create share in DB", command=self.create_new_share_in_db)
        self.button_new_share.place(x=200, y=500, anchor='center')

    def update_frame(self, shares_disabled=True, delete_entries=False):
        """
        update the frame's components
        :return: None
        """

        # update sector combobox
        self.df_sectors = DB_Communication.get_all_sectors(self.db_connection.cursor())
        self.combobox_sector.set_completion_list(self.df_sectors.sector_name)

        # update country combobox
        self.df_countries = DB_Communication.get_all_countries(self.db_connection.cursor())
        self.combobox_country.set_completion_list(self.df_countries.country_name)

        # update category combobox
        self.df_categories = DB_Communication.get_all_categories(self.db_connection.cursor())
        self.combobox_category.set_completion_list(self.df_categories.category_name)
        self.combobox_category.current(1)  # category 'value' is most common

        # update currency combobox
        self.df_currencies = DB_Communication.get_all_currencies(self.db_connection.cursor())
        self.combobox_currency.set_completion_list(self.df_currencies.currency_name)
        self.combobox_currency.current(0)

        if delete_entries:
            # clear isin input
            self.entry_isin.delete(0, tk.END)
            self.comment = ""

        # update visibility of components
        if shares_disabled:
            # set share elements disabled
            self.entry_isin["state"] = "disabled"
            self.combobox_category["state"] = "disabled"
            self.combobox_currency["state"] = "disabled"
            self.button_add_comment["state"] = "disabled"
            self.button_new_share["state"] = "disabled"
            self.entry_company_name["state"] = "normal"

            # set company elements normal
            self.combobox_sector["state"] = "normal"
            self.combobox_country["state"] = "normal"
            self.button_new_company["state"] = "normal"
            self.combobox_sector.current(0)
            self.combobox_country.current(0)

        else:
            # set share elements normal
            self.entry_isin["state"] = "normal"
            self.combobox_category["state"] = "normal"
            self.combobox_currency["state"] = "normal"
            self.button_add_comment["state"] = "normal"
            self.button_new_share["state"] = "normal"

            # set company elements disabled
            self.entry_company_name["state"] = "disabled"
            self.combobox_sector["state"] = "disabled"
            self.combobox_country["state"] = "disabled"
            self.button_new_company["state"] = "disabled"

        if delete_entries:
            # clear company name input
            self.entry_company_name.delete(0, tk.END)

    def create_new_company_in_db(self):
        """
        collects all inputs required to create a company entry and invokes corresponding method
        :return: None
        """

        # get company name
        company_name = self.entry_company_name.get()

        # determine IDs of selected values
        country_id = self.df_countries.ID[self.df_countries.country_name == self.combobox_country.get()].iloc[0]
        sector_id = self.df_sectors.ID[self.df_sectors.sector_name == self.combobox_sector.get()].iloc[0]

        # check for empty user input
        if company_name == "":
            messagebox.showinfo("Missing Company Name", "Please insert a company name!")
        else:
            self.new_company_id = DB_Communication.insert_company(self.db_connection,
                                                                  company_name,
                                                                  country_id,
                                                                  sector_id)
            self.update_frame(shares_disabled=False)

    def create_new_share_in_db(self):
        """
        collects all inputs required to create a company entry and invokes corresponding method
        :return: None
        """

        isin = self.entry_isin.get()
        comment = self.comment

        # determine IDs of selected values
        category_id = self.df_categories.ID[self.df_categories.category_name == self.combobox_category.get()].iloc[0]
        currency_id = self.df_currencies.ID[self.df_currencies.currency_name == self.combobox_currency.get()].iloc[0]

        if isin == "":
            messagebox.showinfo("Missing ISIN", "Please insert an ISIN!")
        elif is_isin_valid(isin):

            # get list of current isin
            list_isin = DB_Communication.get_all_isin(self.db_connection.cursor())

            # allow insert only for unique ISIN
            if isin in list_isin:
                messagebox.showerror("Duplicated ISIN", "The given ISIN does already exist.")
            else:
                dict_share_values = {"isin": isin,
                                     "category_id": category_id,
                                     "currency_id": currency_id,
                                     "comment": comment,
                                     "company_id": self.new_company_id}
                error = DB_Communication.insert_share(self.db_connection, dict_share_values)

                if error is None:
                    self.update_frame(shares_disabled=True, delete_entries=True)
                    messagebox.showinfo("Success!", "The configured has been successfully created in the database.")
                else:
                    messagebox.showerror("DB Error", "An error has occured. Please try again."
                                                     "In case the error remains, please restart the application")
        elif is_isin_valid(isin) is not None:
            messagebox.showerror("Invalid ISIN", "The entered ISIN is well-formated but invalid. \n"
                                                 "Please change it.")
        else:
            messagebox.showerror("Format Error ISIN", "The entered ISIN does not meet the expected format. \n"
                                                      "Please try again.")

    def create_comment_dialog(self):
        """
        create dialog window to enter a comment
        :return: None
        """

        def get_text(master, panel, text):
            """
            get input from scrolled text and pass it as comment to master frame
            :param master: master frame of the dialog window
            :param panel: dialog window instance
            :param text: scrolledText instance
            :return: None
            """
            master.set_comment(text.get("1.0", tk.END))
            panel.destroy()

        # create a dialog window
        top = tk.Toplevel()
        top.title("Insert comment here")
        top.geometry("400x200")
        top.resizable(0, 0)

        # allow user to input text
        edit_space = ScrolledText(top, width=45, height=8, wrap='word')
        edit_space.place(x=0, y=0, anchor='nw')

        # create button to save input and close dialog
        button_save_comment = ttk.Button(top, text="Save comment", command=lambda: get_text(self, top, edit_space))
        button_save_comment.place(x=200, y=180, anchor='center')

        top.mainloop()

    def set_comment(self, comm):
        self.comment = comm


class ParentInsertPage(BasicPage):
    """
    Parent Page for all insert pages
    """

    def __init__(self, parent, controller, insert_type=""):

        super().__init__(parent, controller)

        # id of modified share
        self.current_share_id = 0

        # type of insert
        self.insert_type = insert_type

        # data frame for shares
        self.df_shares = pd.DataFrame(columns=['ID', 'company_name'])

        # create heading
        self.label_heading = ttk.Label(self, text="Insert " + self.insert_type, font=HEADING1_FONT)
        self.label_heading.place(x=480, y=50, anchor='center')

        # crate label for choosing share
        self.label_choose_share = ttk.Label(self, text="Pick a share", font=NORMAL_FONT)
        self.label_choose_share.place(x=350, y=100, anchor='center')

        # create combobox for shares
        self.combobox_shares = AutocompleteCombobox(self, width=30)
        self.combobox_shares.place(x=525, y=100, anchor='center')

        # create label for insert
        self.label_heading_insert_profit = ttk.Label(self, text="Insert " + self.insert_type + "s", font=LARGE_FONT)
        self.label_heading_insert_profit.place(x=100, y=150, anchor='center')

        # create button for existing data
        self.button_existing_data = ttk.Button(self, text="Show existing " + self.insert_type + "s",
                                               command=self.collect_existing_data)
        self.button_existing_data.place(x=750, y=100, anchor='center')

        # create insert button
        self.button_insert_data = ttk.Button(self, text="Insert " + self.insert_type + "s",
                                             command=self.insert_data_in_db)
        self.button_insert_data.place(x=480, y=475, anchor='center')

        # create text box for existing data
        self.heading_existing_data = ttk.Label(self, text="Existing " + self.insert_type + "s", font=LARGE_FONT)
        self.heading_existing_data.place(x=700, y=175, anchor='center')
        self.scrolledtext_data = ScrolledText(self, width=25, height=11, wrap='word')
        self.scrolledtext_data.place(x=750, y=300, anchor='center')

        # create list for all entry elements
        self.list_entries = []

        # create list for all checkbox elements
        self.list_checkboxes = []
        self.list_checkboxes_vars = []

        # create list for all spinbox elements
        self.list_spinboxes = []
        self.list_spinboxes_vars = []

    def update_frame(self):
        """
           update the frame's components
           :return: None
        """
        pass

    def update_parent_elements_on_frame(self):
        """
        update all elements owned by parent class
        :return: None
        """

        # reset combobox selection
        self.combobox_shares.delete(0, tk.END)

        # reset scrolledtext
        self.scrolledtext_data.delete('1.0', tk.END)

    @staticmethod
    def create_five_year_range():
        # TODO: sinnvollen Ort dafür finden
        return list(range(dt.datetime.now().year - 5, dt.datetime.now().year))

    def collect_existing_data(self):
        """
        Get existing profit instances for the current share and display it in the corresponding scrolled text
        :return: None
        """

        # clear text
        self.scrolledtext_data.delete('1.0', tk.END)

        errors_detected = False

        # get current share id from combobox
        try:
            self.current_share_id = self.df_shares.ID[self.df_shares.company_name == self.combobox_shares.get()].iloc[0]
        except IndexError:
            messagebox.showerror("No selection", "No combobox item selected! \n"
                                                 "Please select a share to which the " + self.insert_type +
                                 "s should refer.")
            errors_detected = True

        if not errors_detected:

            existing_data = ""

            # get tuples for year and profit for the current share as a list
            list_data = DB_Communication.get_data_for_specific_share(self.db_connection.cursor(),
                                                                     self.current_share_id,
                                                                     self.insert_type + "s")
            # create text according to query results
            if len(list_data) > 0:
                for each_datum in list_data:
                    year, profit = each_datum

                    existing_data += str(year) + ": " + str(profit) + "\n"
            else:
                existing_data = "No " + self.insert_type + "s available so far"

            # display text in text box
            self.scrolledtext_data.insert(tk.INSERT, existing_data)

    def insert_data_in_db(self):
        """
        Placeholder method
        :return: None
        """

        errors_detected = False

        # get the current share ID selected in the combobox
        try:
            self.current_share_id = self.df_shares.ID[self.df_shares.company_name == self.combobox_shares.get()].iloc[0]
        except IndexError:
            messagebox.showerror(title="No selection",
                                 message="No combobox item selected! \n"
                                         "Please select a share to which the " + self.insert_type +
                                         " value should refer.")
            errors_detected = True

        # get the inserted data values
        list_data_values = []
        for each_entry in self.list_entries:
            list_data_values.append(each_entry.get())

        values_to_be_inserted = []

        # control for each checkbox whether inputs are valid and consistent
        # - if a checkbox is selected the corresponding value has to be inserted
        # - the inserted value has to be a float

        for each_checkbox_var, each_value, i in zip(self.list_checkboxes_vars, list_data_values,
                                                    range(len(list_data_values))):

            if not errors_detected:

                if each_checkbox_var.get() and each_value == '':
                    messagebox.showerror(title="Missing " + self.insert_type + "s",
                                         message=self.insert_type + " input is empty, \n"
                                                 "Please specify a " + self.insert_type + " value or toggle a checkbox.")
                    errors_detected = True

                if each_checkbox_var.get() and each_value != '':
                    try:
                        values_to_be_inserted.append((self.list_spinboxes_vars[i].get(), float(each_value)))
                    except ValueError:
                        messagebox.showerror(title="Value Error",
                                             message="Please insert a number as " + self.insert_type + "value.")
                        errors_detected = True

        # show a message if none of the checkboxes are selected
        for idx, each_checkbox_var in enumerate(self.list_checkboxes_vars):
            if not errors_detected and not each_checkbox_var.get():
                messagebox.showerror(title="Empty Statement",
                                     message="None of the checkboxes are selected. \n"
                                             "Accordingly, no values will be inserted. \n"
                                             "Please select at least one combobox.")
                errors_detected = True

        # get a list of years for which values are already in the database (only for current insert type)
        list_existing_years = DB_Communication.get_years_for_specific_share(self.db_connection.cursor(),
                                                                            self.insert_type + "s",
                                                                            self.current_share_id)

        list_duplicated_years = []

        # catch each year which has already a value of the insert type
        for y, p in values_to_be_inserted:
            if y in list_existing_years:
                list_duplicated_years.append(y)

        # show message which years are already existent
        if len(list_duplicated_years) > 0 and not errors_detected:
            message_text = self.insert_type + "(s) for "

            for each_year in list_duplicated_years:
                message_text += str(each_year) + " "

            message_text += "already exist(s). \nPlease use Update section to change the values."
            messagebox.showerror(title="Year(s) exist already",
                                 message=message_text)
            errors_detected = True

        values_per_entry = {}

        # if no errors are found so far, we can insert the values in the database
        if not errors_detected:

            ts_current_time = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # create a dictionary with all values for each year
            values_per_entry.update({"year": list([y  for y,p in values_to_be_inserted])})
            values_per_entry.update({"share_ID": list([self.current_share_id for i in range(len(values_to_be_inserted))
                                                       ])})
            values_per_entry.update({self.insert_type: list([p for y,p in values_to_be_inserted])})
            values_per_entry.update({"valid_from": list([ts_current_time for i in range(len(values_to_be_inserted))])})
            values_per_entry.update({"valid_to": list(['9999-12-31 23:59:59' for i in range(len(values_to_be_inserted))
                                                       ])})

            # finally perform insert into db
            error = DB_Communication.insert_into_data_table(self.db_connection, self.insert_type, values_per_entry)

            if error is None:
                self.update_frame()
                messagebox.showinfo(title="Success!",
                                    message="The configured data has been successfully created in the database.")
            else:
                messagebox.showerror(title="DB Error",
                                     message="An error has occurred. Please try again."
                                             "In case the error remains, please restart the application.")


class InsertProfitsPage(ParentInsertPage):
    """
    Page allows user to create new profit entries for a specific share
    based on ParentInsertPage
    """

    def __init__(self, parent, controller):

        super().__init__(parent, controller, insert_type="profit")

        # create checkbox for first year
        self.checkbox_1_selected = tk.BooleanVar()
        self.checkbox_year_1 = ttk.Checkbutton(self, var=self.checkbox_1_selected)
        self.checkbox_year_1.place(x=125, y=200, anchor='center')

        # create input box for year 1
        self.spinbox_var_1 = tk.IntVar(value=self.create_five_year_range()[-1])
        self.spinbox_year_1 = ttk.Spinbox(self, values=self.create_five_year_range(), width=8,
                                          textvariable=self.spinbox_var_1)
        self.spinbox_year_1.place(x=225, y=200, anchor='center')

        # create input for profit 1
        self.entry_profit_1 = ttk.Entry(self)
        self.entry_profit_1.place(x=425, y=200, anchor='center')

        # create checkbox for year 2
        self.checkbox_2_selected = tk.BooleanVar()
        self.checkbox_year_2 = ttk.Checkbutton(self, var=self.checkbox_2_selected)
        self.checkbox_year_2.place(x=125, y=250, anchor='center')

        # create input box for year 2
        self.spinbox_var_2 = tk.IntVar(value=self.create_five_year_range()[-2])
        self.spinbox_year_2 = ttk.Spinbox(self, values=self.create_five_year_range(), width=8,
                                          textvariable=self.spinbox_var_2)
        self.spinbox_year_2.place(x=225, y=250, anchor='center')

        # create input for profit 2
        self.entry_profit_2 = ttk.Entry(self)
        self.entry_profit_2.place(x=425, y=250, anchor='center')

        # create checkbox for year 3
        self.checkbox_3_selected = tk.BooleanVar()
        self.checkbox_year_3 = ttk.Checkbutton(self, var=self.checkbox_3_selected)
        self.checkbox_year_3.place(x=125, y=300, anchor='center')

        # create input box for year 3
        self.spinbox_var_3 = tk.IntVar(value=self.create_five_year_range()[-3])
        self.spinbox_year_3 = ttk.Spinbox(self, values=self.create_five_year_range(), width=8,
                                          textvariable=self.spinbox_var_3)
        self.spinbox_year_3.place(x=225, y=300, anchor='center')

        # create input for profit 3
        self.entry_profit_3 = ttk.Entry(self)
        self.entry_profit_3.place(x=425, y=300, anchor='center')

        # create checkbox for year 4
        self.checkbox_4_selected = tk.BooleanVar()
        self.checkbox_year_4 = ttk.Checkbutton(self, var=self.checkbox_4_selected)
        self.checkbox_year_4.place(x=125, y=350, anchor='center')

        # create input box for year 4
        self.spinbox_var_4 = tk.IntVar(value=self.create_five_year_range()[-4])
        self.spinbox_year_4 = ttk.Spinbox(self, values=self.create_five_year_range(), width=8,
                                          textvariable=self.spinbox_var_4)
        self.spinbox_year_4.place(x=225, y=350, anchor='center')

        # create input for profit 4
        self.entry_profit_4 = ttk.Entry(self)
        self.entry_profit_4.place(x=425, y=350, anchor='center')

        # create checkbox for year 5
        self.checkbox_5_selected = tk.BooleanVar()
        self.checkbox_year_5 = ttk.Checkbutton(self, var=self.checkbox_5_selected)
        self.checkbox_year_5.place(x=125, y=400, anchor='center')

        # create input box for year 5
        self.spinbox_var_5 = tk.IntVar(value=self.create_five_year_range()[-5])
        self.spinbox_year_5 = ttk.Spinbox(self, values=self.create_five_year_range(), width=8,
                                          textvariable=self.spinbox_var_5)
        self.spinbox_year_5.place(x=225, y=400, anchor='center')

        # create input for profit 5
        self.entry_profit_5 = ttk.Entry(self)
        self.entry_profit_5.place(x=425, y=400, anchor='center')

    def update_frame(self):
        """
           update the frame's components
           :return: None
        """

        self.update_parent_elements_on_frame()

        # update sector combobox
        self.df_shares = DB_Communication.get_all_shares(self.db_connection.cursor())
        self.combobox_shares.set_completion_list(self.df_shares.company_name)

        # set all checkboxes to be not selected
        self.checkbox_1_selected.set(True)
        self.checkbox_2_selected.set(True)
        self.checkbox_3_selected.set(True)
        self.checkbox_4_selected.set(True)
        self.checkbox_5_selected.set(True)

        # clear all entries
        self.entry_profit_1.delete(0, tk.END)
        self.entry_profit_2.delete(0, tk.END)
        self.entry_profit_3.delete(0, tk.END)
        self.entry_profit_4.delete(0, tk.END)
        self.entry_profit_5.delete(0, tk.END)

        # reset all spinboxes
        self.spinbox_var_1.set(value=self.create_five_year_range()[-1])
        self.spinbox_var_2.set(value=self.create_five_year_range()[-2])
        self.spinbox_var_3.set(value=self.create_five_year_range()[-3])
        self.spinbox_year_4.set(value=self.create_five_year_range()[-4])
        self.spinbox_year_5.set(value=self.create_five_year_range()[-5])

    def insert_data_in_db(self):
        """
                Perform several validity checks for the user input.
                If no errors are detected, create the inserted profit values in the database
                :return: None
                """

        errors_detected = False

        # get current share id from combobox
        try:
            self.current_share_id = self.df_shares.ID[self.df_shares.company_name == self.combobox_shares.get()].iloc[0]
        except IndexError:
            messagebox.showerror("No selection", "No combobox item selected! \n"
                                                 "Please select a share to which the profits should refer.")
            errors_detected = True

        # get all inserted profit values
        profit_1 = self.entry_profit_1.get()
        profit_2 = self.entry_profit_2.get()
        profit_3 = self.entry_profit_3.get()
        profit_4 = self.entry_profit_4.get()
        profit_5 = self.entry_profit_5.get()

        values_to_be_inserted = []

        # control for each checkbox whether inputs are valid and consistent
        # - if a checkbox is selected, the corresponding profit have to be stated
        # - the inserted profit has to be a float
        if self.checkbox_1_selected.get() and profit_1 == "" and not errors_detected:
            messagebox.showerror("Missing Profit", "First profit input is empty. \n"
                                                   "Please specify the corresponding profit value or "
                                                   "toggle the checkbox.")
            errors_detected = True

        if self.checkbox_1_selected.get() and profit_1 != "" and not errors_detected:
            try:
                values_to_be_inserted.append((self.spinbox_var_1.get(), float(profit_1)))
            except ValueError:
                messagebox.showerror("Value Error", "Please insert a number as profit.")
                errors_detected = True

        if self.checkbox_2_selected.get() and profit_2 == "" and not errors_detected:
            messagebox.showerror("Missing Profit", "Second profit input is empty. \n"
                                                   "Please specify the corresponding profit value or "
                                                   "toggle the checkbox.")
            errors_detected = True

        if self.checkbox_2_selected.get() and profit_2 != "" and not errors_detected:
            try:
                values_to_be_inserted.append((self.spinbox_var_2.get(), float(profit_2)))
            except ValueError:
                messagebox.showerror("Value Error", "Please insert a number as profit.")
                errors_detected = True

        if self.checkbox_3_selected.get() and profit_3 == "" and not errors_detected:
            messagebox.showerror("Missing Profit", "Third profit input is empty. \n"
                                                   "Please specify the corresponding profit value or "
                                                   "toggle the checkbox.")
            errors_detected = True

        if self.checkbox_3_selected.get() and profit_3 != "" and not errors_detected:
            try:
                values_to_be_inserted.append((self.spinbox_var_3.get(), float(profit_3)))
            except ValueError:
                messagebox.showerror("Value Error", "Please insert a number as profit.")
                errors_detected = True
        if self.checkbox_4_selected.get() and profit_4 == "" and not errors_detected:
            messagebox.showerror("Missing Profit", "Fourth profit input is empty. \n"
                                                   "Please specify the corresponding profit value or "
                                                   "toggle the checkbox.")
            errors_detected = True

        if self.checkbox_4_selected.get() and profit_4 != "" and not errors_detected:
            try:
                values_to_be_inserted.append((self.spinbox_var_4.get(), float(profit_4)))
            except ValueError:
                messagebox.showerror("Value Error", "Please insert a number as profit.")
                errors_detected = True

        if self.checkbox_5_selected.get() and profit_5 == "" and not errors_detected:
            messagebox.showerror("Missing Profit", "Fifth profit input is empty. \n"
                                                   "Please specify the corresponding profit value or "
                                                   "toggle the checkbox.")
            errors_detected = True

        if self.checkbox_5_selected.get() and profit_5 != "" and not errors_detected:
            try:
                values_to_be_inserted.append((self.spinbox_var_5.get(), float(profit_5)))
            except ValueError:
                messagebox.showerror("Value Error", "Please insert a number as profit.")
                errors_detected = True

        # show message if none of the checkboxes is selected
        if not self.checkbox_5_selected.get() and \
                not self.checkbox_4_selected.get() and \
                not self.checkbox_3_selected.get() and \
                not self.checkbox_2_selected.get() and \
                not self.checkbox_1_selected.get() and \
                not errors_detected:
            messagebox.showerror("Empty Statement", "None of the checkboxes are selected.\n"
                                                    "Accordingly, no values will be inserted.\n"
                                                    "Please select at least once.")
            errors_detected = True

        # get list of years for which profit values are already in the database
        list_existing_years = DB_Communication.get_years_for_specific_share(self.db_connection.cursor(), "profits",
                                                                            self.current_share_id)

        list_duplicated_years = []

        # catch each year which has already a profit value
        for y, p in values_to_be_inserted:
            if y in list_existing_years:
                list_duplicated_years.append(y)

        # show message which years are already existent
        if len(list_duplicated_years) > 0 and not errors_detected:
            message_text = "Profits for "

            for each_year in list_duplicated_years:
                message_text += str(each_year) + " "

            message_text += "already exist. \nPlease use Update section to change the values."
            messagebox.showerror("Year(s) exist already", message_text)
            errors_detected = True

        values_per_entry = {}

        # if so far no errors are found, we can insert the values in the database
        if not errors_detected:

            ts_curr_time = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # create a dictionary with all values for each year
            values_per_entry.update({"year": list([y for y, p in values_to_be_inserted])})
            values_per_entry.update({"share_ID": list([self.current_share_id for i in range(len(values_to_be_inserted))
                                                       ])})
            values_per_entry.update({"profit": list([p for y, p in values_to_be_inserted])})
            values_per_entry.update({"valid_from": list([ts_curr_time for i in range(len(values_to_be_inserted))])})
            values_per_entry.update({"valid_to": list(['9999-12-31 23:59:59' for i in range(len(values_to_be_inserted))
                                                       ])})

            # finally perform insert into db
            error = DB_Communication.insert_into_data_table(self.db_connection, self.insert_type, values_per_entry)

            if error is None:
                self.update_frame()
                messagebox.showinfo("Success!", "The configured has been successfully created in the database.")
            else:
                messagebox.showerror("DB Error", "An error has occured. Please try again."
                                                 "In case the error remains, please restart the application")


class InsertCashflowPage(ParentInsertPage):
    """
    Page allows user to create a new cashflow entry for a specific share
    based on ParentInsertPage
    """

    def __init__(self, parent, controller):

        # write insert type in small letters
        super().__init__(parent, controller, insert_type="cashflow")

        # create checkbox for first year
        self.checkbox_1_selected = tk.BooleanVar()
        self.checkbox_year_1 = ttk.Checkbutton(self, var=self.checkbox_1_selected)
        self.checkbox_year_1.place(x=125, y=200, anchor='center')

        # create input box for year 1
        self.spinbox_var_1 = tk.IntVar(value=self.create_five_year_range()[-1])
        self.spinbox_year_1 = ttk.Spinbox(self, values=self.create_five_year_range(), width=8,
                                          textvariable=self.spinbox_var_1)
        self.spinbox_year_1.place(x=225, y=200, anchor='center')

        # create input for cashflow 1
        self.entry_cashflow_1 = ttk.Entry(self)
        self.entry_cashflow_1.place(x=425, y=200, anchor='center')

        # rearrange insert button
        self.button_insert_data.place(x=480, y=325, anchor='center')

    def update_frame(self):
        """
           update the frame's components
           :return: None
        """

        self.update_parent_elements_on_frame()

        # update sector combobox
        self.df_shares = DB_Communication.get_all_shares(self.db_connection.cursor())
        self.combobox_shares.set_completion_list(self.df_shares.company_name)

        # set all checkboxes to be not selected
        self.checkbox_1_selected.set(True)

        # clear all entries
        self.entry_cashflow_1.delete(0, tk.END)

        # reset all spinboxes
        self.spinbox_var_1.set(value=self.create_five_year_range()[-1])

    def insert_data_in_db(self):
        """
        Perform several validity checks for the user input.
        If no errors are detected, create the inserted cashflow value in the database
        :return: None
        """

        errors_detected = False

        # get current share id from combobox
        try:
            self.current_share_id = self.df_shares.ID[self.df_shares.company_name == self.combobox_shares.get()].iloc[0]
        except IndexError:
            messagebox.showerror("No selection", "No combobox item selected! \n"
                                                 "Please select a share to which the cashflows should refer.")
            errors_detected = True

        # get the inserted cashflow value
        cashflow = self.entry_cashflow_1.get()

        values_to_be_inserted = []

        # control for each checkbox whether inputs are valid and consistent
        # - if a checkbox is selected, the corresponding profit have to be started
        # - the inserted chasflow has to be a float
        if self.checkbox_1_selected.get() and cashflow == "" and not errors_detected:
            messagebox.showerror("Missing Cashflow", "Cashflow input is empty. \n"
                                                     "Please specify the cashflow value or toggle the checkbox.")
            errors_detected = True

        if self.checkbox_1_selected.get() and cashflow != "" and not errors_detected:
            try:
                values_to_be_inserted.append((self.spinbox_var_1.get(), float(cashflow)))
            except ValueError:
                messagebox.showerror("Value Error", "Please insert a number as profit.")
                errors_detected = True

        # show message if the checkbox is not selected
        if not self.checkbox_1_selected and not errors_detected:
            messagebox.showerror("Empty Statement", "The checkbox is not selected. \n" 
                                                    "Accordingly, no values will be inserted. \n" 
                                                    "Please select the checkbox.")
            errors_detected = True

        # get list of years for which cashflow values are already in the database
        list_existing_years = DB_Communication.get_years_for_specific_share(self.db_connection.cursor(),
                                                                            self.insert_type + "s",
                                                                            self.current_share_id)

        list_duplicated_years = []

        # catch each year which has already a cashflow value
        for y, p in values_to_be_inserted:
            if y in list_existing_years:
                list_duplicated_years.append(y)

        # show message which years are already existent
        if len(list_duplicated_years) > 0 and not errors_detected:
            message_text = "Cahsflows for "

            for each_year in list_duplicated_years:
                message_text += str(each_year) + " "

            message_text += "already exist. \nPlease use Update section to change the values."
            messagebox.showerror("Year(s) exist already", message_text)
            errors_detected = True

        values_per_entry = {}

        # if no errors are found so far, we can insert the values in the database
        if not errors_detected:

            ts_curr_time = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # create a dictionary with all values for each year
            values_per_entry.update({"year": list([y for y, p in values_to_be_inserted])})
            values_per_entry.update({"share_ID": list([self.current_share_id for i in range(len(values_to_be_inserted))
                                                       ])})
            values_per_entry.update({self.insert_type: list([p for y, p in values_to_be_inserted])})
            values_per_entry.update({"valid_from": list([ts_curr_time for i in range(len(values_to_be_inserted))])})
            values_per_entry.update({"valid_to": list(['9999-12-31 23:59:59' for i in range(len(values_to_be_inserted))
                                                       ])})

            # finally perform insert into db
            error = DB_Communication.insert_into_data_table(self.db_connection, self.insert_type, values_per_entry)

            if error is None:
                self.update_frame()
                messagebox.showinfo("Success!", "The configured has been successfully created in the database.")
            else:
                messagebox.showerror("DB Error", "An error has occurred. Please try again."
                                     "In case the error remains, please restart the application")


class InsertROAPage(ParentInsertPage):
    """
    Page allows user to create new ROA entries for a specific share
    based on ParentInsertPage
    """

    def __init__(self, parent, controller):

        super().__init__(parent, controller, insert_type="ROA")

        # create checkbox for first year
        self.checkbox_1_selected = tk.BooleanVar()
        self.checkbox_year_1 = ttk.Checkbutton(self, var=self.checkbox_1_selected)
        self.checkbox_year_1.place(x=125, y=200, anchor='center')

        # create input box for year 1
        self.spinbox_var_1 = tk.IntVar(value=self.create_five_year_range()[-1])
        self.spinbox_year_1 = ttk.Spinbox(self, values=self.create_five_year_range(), width=8,
                                          textvariable=self.spinbox_var_1)
        self.spinbox_year_1.place(x=225, y=200, anchor='center')

        # create input for ROA 1
        self.entry_roa_1 = ttk.Entry(self)
        self.entry_roa_1.place(x=425, y=200, anchor='center')

        # create checkbox for second year
        self.checkbox_2_selected = tk.BooleanVar()
        self.checkbox_year_2 = ttk.Checkbutton(self, var=self.checkbox_2_selected)
        self.checkbox_year_2.place(x=125, y=250, anchor='center')

        # create input box for year 2
        self.spinbox_var_2 = tk.IntVar(value=self.create_five_year_range()[-2])
        self.spinbox_year_2 = ttk.Spinbox(self, values=self.create_five_year_range(), width=8,
                                          textvariable=self.spinbox_var_2)
        self.spinbox_year_2.place(x=225, y=250, anchor='center')

        # create input for ROA 2
        self.entry_roa_2 = ttk.Entry(self)
        self.entry_roa_2.place(x=425, y=250, anchor='center')

        # rearrange insert button
        self.button_insert_data.place(x=480, y=375, anchor='center')

    def update_frame(self):
        """
           update the frame's components
           :return: None
        """

        self.update_parent_elements_on_frame()

        # update sector combobox
        self.df_shares = DB_Communication.get_all_shares(self.db_connection.cursor())
        self.combobox_shares.set_completion_list(self.df_shares.company_name)

        # set all checkboxes to be not selected
        self.checkbox_1_selected.set(True)
        self.checkbox_2_selected.set(True)

        # clear all entries
        self.entry_roa_1.delete(0, tk.END)
        self.entry_roa_2.delete(0, tk.END)

        # reset all spinboxes
        self.spinbox_var_1.set(value=self.create_five_year_range()[-1])
        self.spinbox_var_2.set(value=self.create_five_year_range()[-2])

    def insert_data_in_db(self):
        """
        Perform several validity checks for the user input.
        If no errors are detected, create the inserted ROA values in the database
        :return: None
        """

        errors_detected = False

        # get current share id selected in combobox
        try:
            self.current_share_id = self.df_shares.ID[self.df_shares.company_name == self.combobox_shares.get()].iloc[0]
        except IndexError:
            messagebox.showerror(title="No selection",
                                 message="No combobox item selected! \n"
                                         "Please select a share to which the ROA should refer.")
            errors_detected = True

        # get the inserted ROA values
        roa_1 = self.entry_roa_1.get()
        roa_2 = self.entry_roa_2.get()

        values_to_be_inserted = []

        # control for each checkbox whether inputs are valid and consistent
        # - if a checkbox is selected the corresponding ROA has to be
        # - the inserted ROA has to be a float
        if self.checkbox_1_selected.get() and roa_1 == '' and not errors_detected:
            messagebox.showerror(title="Missing ROAs",
                                 message="ROA input is empty. \n"
                                         "Please specify a ROA value or toggle a checkbox.")
            errors_detected = True

        if self.checkbox_1_selected.get() and roa_1 != "" and not errors_detected:
            try:
                values_to_be_inserted.append((self.spinbox_var_1.get(), float(roa_1)))
            except ValueError:
                messagebox.showerror(title="Value Error",
                                     message="Please insert a number as ROA")
                errors_detected = True

        if self.checkbox_2_selected.get() and roa_2 == "" and not errors_detected:
            messagebox.showerror(title="Missing ROAs",
                                 message="ROA input is empty. \n"
                                         "Please specify a ROA value or toggle a checkbox.")
            errors_detected = True

        if self.checkbox_2_selected.get() and roa_2 != "" and not errors_detected:
            try:
                values_to_be_inserted.append((self.spinbox_var_2.get(), float(roa_2)))
            except ValueError:
                messagebox.showerror(title="Value Error",
                                     message="Please insert a number as ROA")
                errors_detected = True

        # show message if none of the checkboxes are selected
        if not self.checkbox_1_selected and \
           not self.checkbox_2_selected and \
           not errors_detected:
            messagebox.showerror(title="Empty Statement",
                                 message="None of the checkboxes are selected. \n"
                                         "Accordingly, no values will be inserted. \n"
                                         "Please select at least one combobox.")
            errors_detected = True

        # get list of years for which ROA values are already in the database
        list_existing_years = DB_Communication.get_years_for_specific_share(self.db_connection.cursor(),
                                                                            self.insert_type + "s",
                                                                            self.current_share_id)
        list_duplicated_years = []

        # catch each year which has already a ROA value
        for y, p in values_to_be_inserted:
            if y in list_existing_years:
                list_duplicated_years.append(y)

        # show message which years are already existent
        if len(list_duplicated_years) > 0 and not errors_detected:
            message_text = "ROA(s) for "

            for each_year in list_duplicated_years:
                message_text += str(each_year) + " "

            message_text += "already exist(s). \nPlease use Update section to change the values."
            messagebox.showerror(title="Year(s) exist already",
                                 message=message_text)
            errors_detected = True

        values_per_entry = {}

        # if no errors are found so far, we can insert the values in the database
        if not errors_detected:

            ts_current_time = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # create a dictionary with all values for each year
            values_per_entry.update({"year": list([y for y, p in values_to_be_inserted])})
            values_per_entry.update({"share_ID": list([self.current_share_id for i in range(len(values_to_be_inserted))
                                                       ])})
            values_per_entry.update({self.insert_type: list([p for y, p in values_to_be_inserted])})
            values_per_entry.update({"valid_from": list([ts_current_time for i in range(len(values_to_be_inserted))])})
            values_per_entry.update({"valid_to": list(['9999-12-31 23:59:59' for i in range(len(values_to_be_inserted))
                                                       ])})

            # finally perform insert into db
            error = DB_Communication.insert_into_data_table(self.db_connection, self.insert_type, values_per_entry)

            if error is None:
                self.update_frame()
                messagebox.showinfo(title="Success!",
                                    message="The configured has been successfully created in the database.")
            else:
                messagebox.showerror(title="DB Error",
                                     message="An error has occurred. Please try again."
                                             "In case the error remains, please restart the application")


class InsertLeveragePage(ParentInsertPage):
    """
    Page allows user to create new Leverage entries for a specific share
    based on ParentInsertPage
    """

    def __init__(self, parent, controller):

        super().__init__(parent, controller, insert_type="leverage")

        # create checkbox for first year
        self.checkbox_1_selected = tk.BooleanVar()
        self.list_checkboxes_vars.append(self.checkbox_1_selected)
        self.checkbox_year_1 = ttk.Checkbutton(self, var=self.checkbox_1_selected)
        self.checkbox_year_1.place(x=125, y=200, anchor='center')
        self.list_checkboxes.append(self.checkbox_year_1)

        # create input box for year 1
        self.spinbox_var_1 = tk.IntVar(value=self.create_five_year_range()[-1])
        self.list_spinboxes_vars.append(self.spinbox_var_1)
        self.spinbox_year_1 = ttk.Spinbox(self, values=self.create_five_year_range(), width=8,
                                          textvariable=self.spinbox_var_1)
        self.spinbox_year_1.place(x=225, y=200, anchor='center')
        self.list_spinboxes.append(self.spinbox_year_1)

        # create input for leverage 1
        self.entry_leverage_1 = ttk.Entry(self)
        self.entry_leverage_1.place(x=425, y=200, anchor='center')
        self.list_entries.append(self.entry_leverage_1)

        # create checkbox for second year
        self.checkbox_2_selected = tk.BooleanVar()
        self.list_checkboxes_vars.append(self.checkbox_2_selected)
        self.checkbox_year_2 = ttk.Checkbutton(self, var=self.checkbox_2_selected)
        self.checkbox_year_2.place(x=125, y=250, anchor='center')
        self.list_checkboxes.append(self.checkbox_year_2)

        # create input box for year 2
        self.spinbox_var_2 = tk.IntVar(value=self.create_five_year_range()[-2])
        self.list_spinboxes_vars.append(self.spinbox_var_2)
        self.spinbox_year_2 = ttk.Spinbox(self, values=self.create_five_year_range(), width=8,
                                          textvariable=self.spinbox_var_2)
        self.spinbox_year_2.place(x=225, y=250, anchor='center')
        self.list_checkboxes.append(self.spinbox_year_2)

        # create input for leverage 2
        self.entry_leverage_2 = ttk.Entry(self)
        self.entry_leverage_2.place(x=425, y=250, anchor='center')
        self.list_entries.append(self.entry_leverage_2)

        # rearrange insert button
        self.button_insert_data.place(x=480, y=375, anchor='center')

    def update_frame(self):
        """
        update the frame's components
        :return: None
        """

        self.update_parent_elements_on_frame()

        # update sector combobox
        self.df_shares = DB_Communication.get_all_shares(self.db_connection.cursor())
        self.combobox_shares.set_completion_list(self.df_shares.company_name)

        # set all checkboxes to be not selected
        self.checkbox_1_selected.set(True)
        self.checkbox_2_selected.set(True)

        # clear all entries
        self.entry_leverage_1.delete(0, tk.END)
        self.entry_leverage_2.delete(0, tk.END)

        # reset all spinboxes
        self.spinbox_var_1.set(value=self.create_five_year_range()[-1])
        self.spinbox_var_2.set(value=self.create_five_year_range()[-2])
