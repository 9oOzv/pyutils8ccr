import curses
from math import ceil
from typing import Any, List, Optional, Sequence, Tuple, Union


MenuItem = Union[str, Tuple[str, Any]]


def menu(
    items: Sequence[MenuItem],
    title: Optional[str] = "Select an option",
    multi_select: bool = False,
    page_size: Optional[int] = None,
) -> Union[Any, List[Any], None]:
    """
    Display an interactive menu in the terminal.

    Args:
        items:
            A sequence of items where each item is one of the following: 1) a
            string (displayed and returned), 2) a tuple (display_text,
            value_to_return).
        title: Optional title displayed at the top of the menu.
        multi_select:
            If True, allows selecting multiple items with Space; Enter confirms
            selections.
        page_size:
            Optional maximum number of items displayed per page. If None, fits
            the screen.

    Returns:
        If multi_select is False: The value of the chosen item, or None if
        cancelled. If multi_select is True: A list of values for selected items
        (possibly empty), or [] if cancelled.

    Navigation:
        - Up/Down arrows or k/j: move selection
        - PageUp/PageDown or Left/Right or h/l: change pages
        - Home/End: jump to first/last item
        - Space: toggle selection (multi-select only)
        - a: select/deselect all (multi-select only)
        - Enter: confirm
        - q or Esc: cancel
    """

    normalized: List[Tuple[str, Any]] = []
    for it in items:
        if isinstance(it, tuple) and len(it) >= 2:
            label = str(it[0])
            value = it[1]
        else:
            label = str(it)
            value = it
        normalized.append((label, value))

    if not normalized:
        return [] if multi_select else None

    def run(stdscr):
        curses.curs_set(0)
        stdscr.keypad(True)
        try:
            curses.start_color()
            curses.use_default_colors()
        except Exception:
            pass

        selected = set()  # indices
        highlight_idx = 0

        def help_text():
            if multi_select:
                return (
                    "Arrows/kj: Move"
                    "  PgUp/PgDn/hl: Page"
                    "  Space: Toggle"
                    "  a: All"
                    "  Enter: Confirm"
                    "  q/Esc: Cancel"
                )
            else:
                return (
                    "Arrows/kj: Move"
                    "  PgUp/PgDn/hl: Page"
                    "  Enter: Select"
                    "  q/Esc: Cancel"
                )

        def compute_effective_page_size() -> int:
            h, _ = stdscr.getmaxyx()
            reserved_lines = 2  # footer + help
            if title:
                reserved_lines += 1
            # Ensure at least one line for items
            max_items = max(1, h - reserved_lines)
            if page_size is None:
                return max_items
            return max(1, min(page_size, max_items))

        ps = compute_effective_page_size()
        total = len(normalized)
        pages = max(1, ceil(total / ps))
        page = 0

        def clamp_index(idx: int) -> int:
            return max(0, min(idx, total - 1))

        def goto_index(idx: int):
            nonlocal highlight_idx, page
            highlight_idx = clamp_index(idx)
            page = highlight_idx // ps

        goto_index(0)

        while True:
            # recompute page size and pages on resize or dynamically if
            # page_size not fixed
            if page_size is None:
                new_ps = compute_effective_page_size()
                if new_ps != ps:
                    ps = new_ps
                    pages = max(1, ceil(total / ps))
                    page = min(page, pages - 1)
                    goto_index(page * ps)

            stdscr.erase()
            h, w = stdscr.getmaxyx()

            # Title
            y = 0
            if title:
                try:
                    stdscr.addnstr(
                        y,
                        0,
                        str(title),
                        max(0, w - 1),
                        curses.A_BOLD
                    )
                except curses.error:
                    pass
                y += 1

            # Render items for current page
            # recompute after possible title draw
            ps = compute_effective_page_size()
            pages = max(1, ceil(total / ps))
            start = page * ps
            end = min(start + ps, total)

            # Ensure highlight index stays within the visible items when
            # shrinking
            if not (start <= highlight_idx < end):
                goto_index(start)

            for i in range(start, end):
                is_current = (i == highlight_idx)
                label, _ = normalized[i]
                cursor = "> " if is_current else "  "
                sel_prefix = ""
                if multi_select:
                    sel_prefix = "[x] " if i in selected else "[ ] "
                line = cursor + sel_prefix + label
                attr = curses.A_REVERSE if is_current else curses.A_NORMAL
                try:
                    stdscr.addnstr(y, 0, line, max(0, w - 1), attr)
                except curses.error:
                    pass
                y += 1

            # Footer: page info
            footer_y = h - 2
            if footer_y >= 0:
                page_info = f"Page {page + 1}/{pages}  Items {total}"
                try:
                    stdscr.addnstr(
                        footer_y,
                        0,
                        page_info.ljust(max(0, w - 1)),
                        max(0, w - 1),
                        curses.A_DIM
                    )
                except curses.error:
                    pass

            # Help line
            help_y = h - 1
            if help_y >= 0:
                try:
                    stdscr.addnstr(
                        help_y,
                        0,
                        help_text()[: max(0, w - 1)],
                        max(0, w - 1),
                        curses.A_DIM
                    )
                except curses.error:
                    pass

            stdscr.refresh()

            ch = stdscr.getch()

            if ch in (curses.KEY_UP, ord('k')):
                goto_index(
                    highlight_idx - 1
                    if highlight_idx > 0
                    else total - 1
                )
            elif ch in (curses.KEY_DOWN, ord('j')):
                goto_index(
                    highlight_idx + 1
                    if highlight_idx < total - 1
                    else 0
                )
            elif ch in (curses.KEY_PPAGE, curses.KEY_LEFT, ord('h')):
                if page > 0:
                    goto_index((page - 1) * ps)
                else:
                    goto_index((pages - 1) * ps)
            elif ch in (curses.KEY_NPAGE, curses.KEY_RIGHT, ord('l')):
                if page < pages - 1:
                    goto_index((page + 1) * ps)
                else:
                    goto_index(0)
            elif ch == curses.KEY_HOME:
                goto_index(0)
            elif ch == curses.KEY_END:
                goto_index(total - 1)
            elif ch == curses.KEY_RESIZE:
                # loop will recalc sizes
                pass
            elif ch in (ord(' '),):
                if multi_select:
                    if highlight_idx in selected:
                        selected.remove(highlight_idx)
                    else:
                        selected.add(highlight_idx)
            elif ch in (ord('a'), ord('A')):
                if multi_select:
                    if len(selected) < total:
                        selected.clear()
                        selected.update(range(total))
                    else:
                        selected.clear()
            elif ch in (curses.KEY_ENTER, 10, 13):
                if multi_select:
                    return [normalized[i][1] for i in sorted(selected)]
                else:
                    return normalized[highlight_idx][1]
            elif ch in (27, ord('q'), ord('Q')):  # ESC or q/Q
                return [] if multi_select else None
            else:
                # ignore unhandled keys
                pass

    return curses.wrapper(run)


if __name__ == "__main__":
    demo_items = [
        "Apple",
        "Banana",
        ("Cherry (value=3)", 3),
        "Date",
        "Elderberry",
        "Fig",
        "Grape",
        "Honeydew",
        "Indian Fig",
        "Jackfruit",
        "Kiwi",
        "Lemon",
        "Mango",
        "Nectarine",
        "Orange",
        "Papaya",
        "Quince",
        "Raspberry",
        "Strawberry",
        "Tangerine",
        "Ugli Fruit",
        "Voavanga",
        "Watermelon",
        "Xigua",
        "Yellow Passion Fruit",
        "Zucchini",
    ]

    # Single-select example
    result_single = menu(
        demo_items,
        title="Pick one fruit",
        multi_select=False
    )
    print("Single result:", result_single)

    # Multi-select example
    result_multi = menu(
        demo_items,
        title="Pick multiple fruits",
        multi_select=True
    )
    print("Multi result:", result_multi)
