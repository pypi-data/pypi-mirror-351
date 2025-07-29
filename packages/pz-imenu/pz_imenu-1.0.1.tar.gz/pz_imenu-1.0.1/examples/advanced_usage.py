from pz_imenu import IM

def show_greeting(menu):
    print("\n[Action] You selected to see a greeting! Hello, adventurer!\n")
    input("\nPress Enter to continue...")

def show_farewell(menu):
    print("\n[Action] Farewell, brave soul. Until next time!\n")
    input("\nPress Enter to continue...")

def dynamic_option_show(menu):
    print("\n[Action] Dynamically added option activated!")
    input("\nPress Enter to continue...")

def enter_submenu(menu):
    submenu = menu.Children(header="Submenu", footer="Select an option in the submenu")
    submenu.Group("subgroup", title="Submenu Options")
    submenu.Add("1", "Show greeting", show_greeting, group_id="subgroup")
    submenu.Add("2", "Show farewell", show_farewell, group_id="subgroup")
    submenu.Display()

def dynamic_option(menu):
    # Dynamically add a new option to the main menu
    try:
        menu.Add("3", "Newly Added Option", dynamic_option_show, group_id="main")
        print("\n[Action] You discovered a secret dynamic option!\n")
    except ValueError as e:
        print(f"\n[Error] {e}")
    input("\nPress Enter to continue...")


if __name__ == "__main__":
    # Create the main menu
    main_menu = IM(header="Advanced Menu Example", footer="Choose an option to explore")

    # Create groups
    main_menu.Group("main", title="Main Options")

    # Add main options
    main_menu.Add("1", "Enter Submenu", enter_submenu, group_id="main")
    main_menu.Add("2", "Discover a Dynamic Option", dynamic_option, group_id="main")

    # Display the menu
    main_menu.Display()
