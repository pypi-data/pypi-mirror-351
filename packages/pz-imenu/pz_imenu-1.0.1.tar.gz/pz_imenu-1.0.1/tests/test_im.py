import pytest
from pz_imenu import IM

def test_im_initialization():
    menu = IM(header="Test Menu")
    assert menu.header == "Test Menu"
    assert isinstance(menu.choices, dict)
    assert isinstance(menu.groups, dict)

def test_group_addition():
    menu = IM()
    menu.Group("test_group", title="Test Group")
    assert "test_group" in menu.groups
    assert menu.groups["test_group"]["title"] == "Test Group"
    assert menu.groups["test_group"]["options"] == []

def test_add_option():
    menu = IM()
    menu.Group("test_group")
    callback = lambda im: None
    menu.Add("1", "Option 1", callback, group_id="test_group")
    assert "1" in menu.choices
    assert menu.choices["1"]["description"] == "Option 1"
    assert menu.choices["1"]["callback"] == callback
    assert ("1", "Option 1") in menu.groups["test_group"]["options"]

def test_children_menu_creation():
    menu = IM(header="Main Menu")
    child = menu.Children(header="Child Menu")
    assert child.header == "Child Menu"
    assert child.parent_menu_im == menu
    assert child.main_menu_im == menu

def dummy_callback(im):
    pass

def test_im_initialization_defaults():
    menu = IM()
    assert menu.header is None
    assert menu.footer is None
    assert menu.clear_console is True
    assert menu.header_color == "blue"
    assert menu.option_color == "cyan"
    assert menu.quit_color == "red"
    assert menu.main_menu_im is None
    assert menu.parent_menu_im is None

def test_group_addition_and_duplicate():
    menu = IM()
    menu.Group("test_group", title="Test Group")
    assert "test_group" in menu.groups

    # Duplicate group addition should raise ValueError
    with pytest.raises(ValueError):
        menu.Group("test_group")

def test_add_option_and_duplicate_key():
    menu = IM()
    menu.Group("test_group")
    menu.Add("1", "First Option", dummy_callback, group_id="test_group")
    assert "1" in menu.choices

    # Duplicate key addition should raise ValueError
    with pytest.raises(ValueError):
        menu.Add("1", "Duplicate Option", dummy_callback, group_id="test_group")

def test_add_invisible_option():
    menu = IM()
    menu.Add("2", "Invisible Option", dummy_callback, visible=False)
    assert "2" not in menu.choices  # Should not be in choices since visible=False

def test_children_menu_links():
    main_menu = IM(header="Main")
    child_menu = main_menu.Children(header="Child")
    subchild_menu = child_menu.Children(header="SubChild")

    assert child_menu.parent_menu_im == main_menu
    assert child_menu.main_menu_im == main_menu
    assert subchild_menu.parent_menu_im == child_menu
    assert subchild_menu.main_menu_im == main_menu

def test_display_options_visibility(monkeypatch):
    # We cannot run the Display loop directly in tests because it expects user input.
    # But we can inspect the menu’s groups and choice structure
    menu = IM(header="Main")
    menu.Group("group1", title="Group 1")
    menu.Add("a", "Option A", dummy_callback, group_id="group1")
    menu.Add("b", "Option B", dummy_callback, group_id="group1")
    menu.Add("c", "Option C", dummy_callback, group_id="group1", visible=False)

    # Invisible option should not be in menu.choices
    assert "c" not in menu.choices
    assert ("c", "Option C") not in menu.groups["group1"]["options"]

def test_quit_and_back_presence():
    # Quit option is always present in a root menu
    menu = IM(header="Root")
    assert menu.parent_menu_im is None

    # When a parent exists, 'Back' option should be available
    child = menu.Children(header="Child")
    assert child.parent_menu_im == menu