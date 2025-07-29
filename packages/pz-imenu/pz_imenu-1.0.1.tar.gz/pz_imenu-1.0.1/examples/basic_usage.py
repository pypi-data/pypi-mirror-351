from pz_imenu import IM

def hello_callback(menu):
    print("\nHello, world!")
    input("\nPress Enter to continue...")

def goodbye_callback(menu):
    print("\nGoodbye, world!")
    input("\nPress Enter to continue...")

if __name__ == "__main__":
    # Create the main menu
    menu = IM(header="Example Menu", footer="Select an option to continue")

    # Create groups
    menu.Group("main", title="Main Options")

    # Add options
    menu.Add("1", "Say Hello", hello_callback, group_id="main")
    menu.Add("2", "Say Goodbye", goodbye_callback, group_id="main")

    # Display the menu
    menu.Display()
