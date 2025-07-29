from rich.prompt import Prompt
from rich.panel import Panel
from rich.console import Console
from rich.prompt import Confirm

class IM:
    """
    IM (Interactive Menu) is a simple console-based menu system using the 'rich' library.
    It allows for adding multiple menu options with callbacks and provides a user-friendly
    interface to navigate these options.
    """
    def __init__(self, main_menu_im=None, parent_menu_im=None, header=None, footer=None, clear_console=True, header_color="blue", option_color="cyan", quit_color="red"):
        """
        Initializes the IM instance, setting up the console for output,
        initializing the choices dictionary, and line storage.
        :param main_menu_im: Reference to the main menu IM instance if this is a submenu.
        :param parent_menu_im: Reference to the immediate parent menu IM instance.
        :param header: The text to display at the top of the menu.
        :param footer: The text to display at the bottom of the menu.
        :param header_color: Color of the header text.
        :param option_color: Color of the menu options.
        :param quit_color: Color of the quit text.
        """
        self.console = Console()
        self.choices = {}
        self.groups = {}  # To hold groups of options by group ID
        self.header = header
        self.footer = footer
        self.clear_console = clear_console
        self.header_color = header_color
        self.option_color = option_color
        self.quit_color = quit_color
        self.main_menu_im = main_menu_im
        self.parent_menu_im = parent_menu_im

    def Group(self, group, title=None):
        """
        Adds a new group of menu options.

        :param group: The unique identifier for the group.
        :param title: An optional title for the group.
        """
        if group in self.groups:
            raise ValueError(f"Group '{group}' already exists. Please choose a unique group ID.")
        self.groups[group] = {'title': title, 'options': []}

    def Add(self, key, description, callback, group_id=None, visible=True):
        """
        Adds a new choice to the specified group or to the default group if none is specified.

        :param key: The key the user will press to select this option (e.g., '1', '2', '3').
        :param description: The description of the action.
        :param callback: The function to call when this option is selected.
        :param group_id: The group ID to add the choice to. If None, it will add to a default group.
        :param visible: Determines if the option should be visible in the menu.
        """
        key = key.strip().lower()
        if key in self.choices:
            raise ValueError(f"Key '{key}' already exists. Please choose a unique key.")
        if visible:
            self.choices[key] = {'description': description, 'callback': callback}
            if group_id is None:
                group_id = 'default'
            if group_id not in self.groups:
                self.Group(group_id)
            self.groups[group_id]['options'].append((key, description))

    def Display(self):
        """
        Displays the interactive menu, handles user input, and executes corresponding callbacks.
        It continues to prompt until the user chooses to quit.
        """
        while True:
          
            # Clear the console if specified
            if self.clear_console:
                self.console.clear()

            # Display the menu header if set
            if self.main_menu_im is None and self.header:
                self.console.print(Panel(f"[bold {self.header_color}]{self.header}[/bold {self.header_color}]", title="Main Menu", padding=1))
                self.console.print("")
            elif self.header:
                self.console.print(f"[bold {self.header_color}]{self.header}[/bold {self.header_color}]\n")

            # Display Main Menu options if applicable
            if self.main_menu_im:
                self.console.print(f"[{self.option_color}]M.[/{self.option_color}] Main Menu\n")

            # Display the menu options grouped by group ID
            for group_id, group_data in self.groups.items():
                if group_data['title']:
                    self.console.print(f"[bold {self.header_color}]{group_data['title']}[/bold {self.header_color}]")
                for key, description in group_data['options']:
                    self.console.print(f"[{self.option_color}]{key}.[/{self.option_color}] {description}")
                self.console.print("")  # Add line break between groups

            # Display Back or Quit options if applicable
            if self.parent_menu_im:
                self.console.print(f"[{self.option_color}]B.[/{self.option_color}] Back")
            else:
                self.console.print(f"[{self.quit_color}]Q.[/{self.quit_color}] Quit")

            # Display the footer if set
            if self.footer:
                self.console.print(f"\n[bold {self.header_color}]{self.footer}[/bold {self.header_color}]\n")

            # Prompt the user for input
            user_input = Prompt.ask("\n[bold yellow]Please select an option[/bold yellow]").strip().lower()
            self.console.print("\n")

            # Handle Back, Main Menu, and Quit options
            if user_input == 'b' and self.parent_menu_im:
                self.parent_menu_im.Display()
                break
            elif user_input == 'm' and self.main_menu_im:
                self.main_menu_im.Display()
                break
            elif user_input in ['q', 'quit', 'exit', 'void', 'escape', 'esc', 'x']:
                quit()
                break

            # Execute the corresponding callback if it exists
            if user_input in self.choices:
                callback = self.choices[user_input]['callback']
                callback(self)
            else:
                self.console.print("[bold red]Invalid option, please try again.[/bold red]")

    def Children(self, header=None, footer=None, clear_console=True, header_color="blue", option_color="cyan", quit_color="red"):
        '''
        '''
        mm = self if self.main_menu_im == None else self.main_menu_im
        return IM(mm, self, header, footer, clear_console, header_color, option_color, quit_color)