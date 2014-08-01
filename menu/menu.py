from django.conf import settings
from .menu_item import MenuItem


class Menu(object):
    """
    Menu is a class that generates menus

    It allows for multiple named menus, which can be accessed in your templates
    using the generate_menu template tag.

    Menus are loaded from the INSTALLED_APPS, inside a file named menus.py.
    This file should import the Menu & MenuItem classes and then call add_item:

        Menu.add_item("main", MenuItem("My item",
                                       reverse("myapp.views.myview"),
                                       weight=10))

    Note: You cannot have the same URL in a MenuItem in different
    Menus, but it is not enforced. If you do submenus will not work
    properly.
    """
    items = {}
    sorted = set()
    processors = {}

    @classmethod
    def add_item(c, name, item):
        """
        add_item adds MenuItems to the menu identified by 'name'
        """
        if isinstance(item, MenuItem):
            if name not in c.items:
                c.items[name] = []
            c.items[name].append(item)
            c.sorted.add(name)

    @classmethod
    def add_pre_process(c, name, func, once=False):
        if callable(func):
            if name not in c.processors:
                c.processors[name] = []
            c.processors[name].append({ 'func': func, 'once': once })

    @classmethod
    def sort_menu(c, name):
        """
        sort_menus goes through the items and sorts them based on
        their weight
        """
        if name not in c.sorted:
            return
        c.items[name].sort(key=lambda x: x.weight)
        c.sorted.remove(name)

    @classmethod
    def pre_process(c, name):
        if name not in c.processors:
            return

        for idx, item in enumerate(c.processors[name]):
            item['func']()
            if item['once']:
                del c.processors[name][idx]

    @classmethod
    def process(c, request, name=None):
        """
        process uses the current request to determine which menus
        should be visible, which are selected, etc.
        """
        if name is None:
            # special case, process all menus
            items = {}
            for name in c.items:
                items[name] = c.process(request, name)
            return items

        c.pre_process(name)

        if name not in c.items:
            return []

        c.sort_menu(name)

        curitem = None
        for item in c.items[name]:
            item.process(request)
            if item.visible:
                item.selected = False
                if item.match_url(request):
                    if curitem is None or len(curitem.url) < len(item.url):
                        curitem = item

        if curitem is not None:
            curitem.selected = True

        # return only visible items
        visible = [
            item
            for item in c.items[name]
            if item.visible
        ]

        # determine if we should apply 'selected' to parents when one of their
        # children is the 'selected' menu
        if getattr(settings, 'MENU_SELECT_PARENTS', False):
            def is_child_selected(item):
                for child in item.children:
                    if child.selected or is_child_selected(child):
                        return True

            for item in visible:
                if is_child_selected(item):
                    item.selected = True

        return visible
