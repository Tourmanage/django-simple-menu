import re
from django.conf import settings


class MenuItem(object):
    """
    MenuItem represents an item in a menu, possibly one that has a sub-
    menu (children).
    """

    def __init__(self, title, url, children=None, weight=1, check=None, visible=True, slug=None, exact_url=False,
                 **kwargs):
        """
        MenuItem constructor

        title       either a string or a callable to be used for the title
        url         the url of the item
        children    an array of MenuItems that are sub menus to this item
                    this can also be a callable that generates an array
        weight      used to sort adjacent MenuItems
        check       a callable to determine if this item is visible
        slug        used to generate id's in the HTML, auto generated from
                    the title if left as None
        exact_url   normally we check if the url matches the request prefix
                    this requires an exact match if set

        All other keyword arguments passed into the MenuItem constructor are
        assigned to the MenuItem object as attributes so that they may be used
        in your templates. This allows you to attach arbitrary data and use it
        in which ever way suits your menus the best.
        """

        self.url = url
        self.title = title
        self._title = None
        self.visible = visible
        self.children = children if children else []
        self.children_sorted = False
        self.weight = weight
        self.check = check
        self.slug = slug
        self.exact_url = exact_url
        self.selected = False
        self.parent = None

        # merge our kwargs into our self
        for k in kwargs:
            setattr(self, k, kwargs[k])

        # if title is a callable store a reference to it for later
        # then we'll process it at runtime
        if callable(title):
            self.title = ""
            self._title = title

    def process(self, request):
        """
        process determines if this item should visible, if its selected, etc...
        """
        self.check_check(request)
        if not self.visible:
            return

        # evaluate title
        self.check_title(request)

        # evaluate children
        visible_children = []
        self.check_children(request)
        for child in self.children:
            child.process(request)
            if child.visible:
                visible_children.append(child)

        hide_empty = getattr(settings, 'MENU_HIDE_EMPTY', False)
        if hide_empty and not self.check and not len(visible_children):
            self.visible = False
            return

        curitem = None
        for item in visible_children:
            item.selected = False

            if item.match_url(request):
                if curitem is None or len(curitem.url) < len(item.url):
                    curitem = item

        if curitem is not None:
            curitem.selected = True

    def match_url(self, request):
        """
        match url determines if this is selected
        """
        matched = False
        if self.exact_url:
            if re.match("%s$" % (self.url,), request.path):
                matched = True
        elif re.match("%s" % self.url, request.path):
            matched = True
        return matched

    def check_children(self, request):
        if hasattr(self, '_children'):
            self.children = self._children(request)
        if callable(self.children):
            kids = self.children(request)
            self._children = self.children
            self.children = kids

        for kid in self.children:
            kid.parent = self

    def check_check(self, request):
        if callable(self.check):
            self.visible = self.check(request)

    def check_title(self, request):
        if callable(self._title):
            self.title = self._title(request)
        if self.slug is None:
            self.slug = re.sub(r'[^a-zA-Z0-9\-]+', '_',
                               self.title.lower()).strip('_')
