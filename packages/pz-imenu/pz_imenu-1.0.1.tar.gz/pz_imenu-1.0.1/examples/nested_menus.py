from pz_imenu import IM

def final_depth_action(menu):
    print("\n[Action] You've reached the final depth! Well done, explorer!\n")

def create_deep_child(menu, depth):
    if depth == 0:
        return final_depth_action

    def next_level_callback(inner_menu):
        # Create a child for the next depth level
        next_child = inner_menu.Children(header=f"Level {depth} Menu")
        next_child.Group("deep_group", title=f"Level {depth} Options")
        next_child.Add("1", f"Go Deeper to Level {depth-1}", create_deep_child(next_child, depth - 1), group_id="deep_group")
        next_child.Display()
    
    return next_level_callback

if __name__ == "__main__":
    # Create the main menu
    main_menu = IM(header="Infinite Depth Menu", footer="Start your journey to the deepest level!")

    # Create groups and add the first entry point
    main_menu.Group("root", title="Root Options")
    main_menu.Add("1", "Descend to Level 10", create_deep_child(main_menu, 10), group_id="root")

    # Display the menu
    main_menu.Display()
