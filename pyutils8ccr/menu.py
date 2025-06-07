from typing import Any

class MenuItem:
    """
    Represents an item in a menu. Menu item consists of a value, a display name, and an unique identifier (id).

    value is the value returned when the item is selected. Name is displayed in the menu. Id is used to uniquely identify items where needed (e.g. recency-based sorting when the menu is shown / updated multiple times).

    Attributes:
        value: The value associated with the menu item.
        name: The display name of the menu item. Defaults to `str(value)`.
        id: Unique identifier for the menu item. Defaults to `hash(value)`.
    """
    def __init__(
        self,
        value: Any,
        name: str | None = None,
        id: Any | None = None,
    ):
        self.value = value
        self.name = (
            name
            if name is not None
            else str(value)
        )
        self.id = (
            id
            if id is not None
            else hash(value)
        )


class InvalidMenuKeyError(Exception):
    def __init__(self, key: str):
        super().__init__(f"Invalid menu key: {key}")
        self.key = key

class PagedMenu:

    def __init__(
        self,
        menu_items: list[MenuItem] | None = None,
        value_items: list[Any] | None = None,
        named_items: list[tuple[str, Any]] | None = None,
        id_items: list[tuple[Any, Any, str]] | None = None,
        page_size: int = 10,
        keys: str = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
        next_page_key: str = '.',
        previous_page_key: str = ',',
        first_page_key: str | None = '<',
        last_page_key: str | None = '>',
        default: str | None = None
    ):
        """
        Initialize a paged menu.

        Args:
            menu_items: List of MenuItem objects (optional).
            value_items: List of values to select from (optional).
            named_items: List of values with associated names (optional) to select from. See `MenuItem`.
            id_items: List of tuples with (value, name, id) to select from (optional). See `MenuItem`.
            page_size: Number of items per page.
            keys: String of keys to use for navigation.
            next_page_key: Key to go to the next page.
            previous_page_key: Key to go to the previous page.
            first_page_key: Key to go to the first page (optional).
            last_page_key: Key to go to the last page (optional).
            default: Default value if no item is selected (optional).
        """
        self.items = self.parse_items(menu_items, value_items, named_items, id_items)
        if page_size < 2:
            raise ValueError("Page size less than 2")
        if not keys or len(keys) < 2:
            raise ValueError("Less than 2 keys defined")
        if len(keys) < page_size:
            raise ValueError("Not enough keys for the page size")
        if next_page_key in keys:
            raise ValueError("Next page key cannot be used as menu key")
        if previous_page_key in keys:
            raise ValueError("Previous page key cannot be used as menu key")
        if first_page_key and first_page_key in keys:
            raise ValueError("First page key cannot be used as menu key")
        if last_page_key and last_page_key in keys:
            raise ValueError("Last page key cannot be used as menu key")
        self.page_size = min(page_size, len(keys))
        self.current_page = 0
        self.keys = keys[:self.page_size]
        self.next_page_key = next_page_key
        self.previous_page_key = previous_page_key
        self.first_page_key = first_page_key
        self.last_page_key = last_page_key
        self.default = default
        self.total_pages = (len(self.items) + self.page_size - 1) // self.page_size
        self.status = ""

    def parse_items(
        self,
        menu_items: list[MenuItem] | None = None,
        value_items: list[Any] | None = None,
        named_items: list[tuple[str, Any]] | None = None,
        id_items: list[tuple[Any, Any, str]] | None = None
    ) -> list[MenuItem]:
        """
        Parse items from different formats into a list of MenuItem objects.
        
        Args:
            menu_items: List of MenuItem objects (optional).
            value_items: List of values to select from (optional).
            named_items: List of tuples with (name, value) to select from (optional).
            id_items: List of tuples with (value, name, id) to select from (optional).
        
        Returns:
            List of MenuItem objects.
        """
        items = []
        if menu_items:
            items.extend(menu_items)
        if value_items:
            items.extend(MenuItem(value) for value in value_items)
        if named_items:
            items.extend(MenuItem(value, name) for name, value in named_items)
        if id_items:
            items.extend(MenuItem(value, name, id) for value, name, id in id_items)
        return items

    def get_page_items(self, page: int) -> list[MenuItem]:
        start = page * self.page_size
        end = start + self.page_size
        return self.items[start:end]

    def display_page(self, page: int) -> str:
        items = self.get_page_items(page)
        if not items:
            return "No items to display."
        
        display = []
        for i, item in enumerate(items):
            display.append(f"{self.keys[i]}: {item.name} ({item.value})")
        nav_display = []
        if self.first_page_key:
            nav_display.append(f"{self.first_page_key}: First")
        if self.previous_page_key:
            nav_display.append(f"{self.previous_page_key}: Previous")
        if self.next_page_key:
            nav_display.append(f"{self.next_page_key}: Next")
        if self.last_page_key:
            nav_display.append(f"{self.last_page_key}: Last")
        display.append(" ".join(nav_display))
        display.append(f"{page + 1}/{self.total_pages}")
        if self.status:
            display.append(f"{self.status}")
        return "\n".join(display)

    def navigate(self, command: str) -> str:
        if command == '':
            self.selected = True
            self.selected_value = self.default
        if command == self.next_page_key:
            if self.current_page < self.total_pages - 1:
                self.current_page += 1
        elif command == self.previous_page_key:
            if self.current_page > 0:
                self.current_page -= 1
        elif command == self.first_page_key and self.first_page_key:
            self.current_page = 0
        elif command == self.last_page_key and self.last_page_key:
            self.current_page = self.total_pages - 1
        elif command in self.keys:
            index = self.keys.index(command)
            if index < len(self.get_page_items(self.current_page)):
                self.selected = True
                self.selected_value = self.get_page_items(self.current_page)[index].value
            else:
                raise InvalidMenuKeyError(command)
        else:
            raise InvalidMenuKeyError(command)

    def run(self) -> str:
        """
        Run interactive menu.
        """
        self.selected = False
        self.selected_value = self.default
        while True:
            print(self.display_page(self.current_page))
            command = input(">> ").strip()
            try:
                self.navigate(command)
                if self.selected:
                    return self.selected_value
            except InvalidMenuKeyError as e:
                self.status = f"Error: {e.key} is not a valid menu key."
