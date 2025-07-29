# pz-imenu

A simple, elegant Python interactive menu system using the **Rich** library, part of the **pz-** namespace.

## Features

✅ Create colorful and structured console menus  
✅ Support for nested submenus (children)  
✅ Group options for better organization  
✅ Dynamic addition of options and submenus at runtime  
✅ Powered by [Rich](https://github.com/Textualize/rich) for beautiful console output

## Installation

Install via pip (after publishing to PyPI):

```bash
pip install pz-imenu
```

Or for local development:

```bash
git clone https://github.com/poziel/imenu.git
cd imenu
pip install -e .
```

## Basic Usage

```python
from pz_imenu import IM

def hello_callback(menu):
    print("\\nHello, world!")

menu = IM(header="My Menu")
menu.Group("default", title="Options")
menu.Add("1", "Say Hello", hello_callback)
menu.Display()
```

## Advanced Usage

Submenus, dynamic options, and more!

```python
from pz_imenu import IM

def final_depth_action(menu):
    print("\\n[Action] You've reached the final depth! Well done!\\n")

def create_deep_child(menu, depth):
    if depth == 0:
        return final_depth_action

    def next_level_callback(inner_menu):
        next_child = inner_menu.Children(header=f"Level {depth} Menu")
        next_child.Group("deep_group", title=f"Level {depth} Options")
        next_child.Add("1", f"Go Deeper to Level {depth-1}", create_deep_child(next_child, depth - 1), group_id="deep_group")
        next_child.Display()
    
    return next_level_callback

if __name__ == "__main__":
    main_menu = IM(header="Infinite Depth Menu", footer="Start your journey!")
    main_menu.Group("root", title="Root Options")
    main_menu.Add("1", "Descend to Level 3", create_deep_child(main_menu, 3), group_id="root")
    main_menu.Display()
```

## Examples

Check out the `examples/` folder for:

- **basic_usage.py**: Simple menu with two actions  
- **advanced_usage.py**: Submenus and dynamic options  
- **nested_menus.py**: Deep nested menus showcasing the power of pz-imenu

Run them with:

```bash
python examples/basic_usage.py
python examples/advanced_usage.py
python examples/nested_menus.py
```

## Tests

Tests are written using **pytest**:

```bash
pytest tests
```

## License

MIT License

---

Enjoy exploring with **pz-imenu**! 🚀
