#!/usr/bin/env python3
"""Navigation primitives for the interactive home-menu shell (§5.7 / PROTO-096).

The human surface of Proto Gear is UI-first: you *navigate and pick*, you don't
memorise a command palette. This module is the framework-free core of that
shell — a small, testable data model plus one interactive loop.

A :class:`MenuScreen` is a titled list of :class:`MenuItem`. An item is either a
**leaf** (carries an ``action`` callable) or a **branch** (carries a ``submenu``
factory that returns the child screen when entered). :func:`run_menu` drives a
stack of screens with ``questionary`` and a caller-supplied header renderer,
giving breadcrumbs and back-navigation for free.

Everything except :func:`run_menu` is pure — no TTY, no ``questionary`` — so the
data model, breadcrumb, and choice builders unit-test directly. The loop itself
mirrors the repo's other interactive surfaces: import ``questionary`` lazily,
let a scripted fake stand in under test.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple

# Sentinel values the select prompt returns for the navigation controls. Kept
# distinct from any real item key so a screen can never collide with them.
BACK = "__back__"
QUIT = "__quit__"

CRUMB_SEP = " › "


@dataclass
class MenuItem:
    """One selectable row.

    A *leaf* sets ``action`` (called when chosen); a *branch* sets ``submenu``
    (a zero-arg factory returning the child :class:`MenuScreen`, resolved lazily
    on entry so badges/contents stay fresh). Setting neither makes the row a
    no-op label; setting both is a programming error (``action`` is ignored).
    """

    key: str
    label: str
    hint: str = ""
    badge: str = ""
    action: Optional[Callable[[], object]] = None
    submenu: Optional[Callable[[], "MenuScreen"]] = None

    def is_branch(self) -> bool:
        return self.submenu is not None


@dataclass
class MenuScreen:
    """A titled list of items. ``title`` is the breadcrumb segment."""

    title: str
    items: List[MenuItem] = field(default_factory=list)
    prompt: str = "Where to?"

    def item(self, key: str) -> Optional[MenuItem]:
        """The item with ``key``, or ``None`` (nav sentinels never match)."""
        return next((it for it in self.items if it.key == key), None)


def format_breadcrumb(titles: List[str]) -> str:
    """Join screen titles into a trail: ``["Home", "Tickets"]`` → ``Home › Tickets``."""
    return CRUMB_SEP.join(t for t in titles if t)


def format_item_label(item: MenuItem, *, label_width: int = 0) -> str:
    """Plain one-line label: ``Label   hint  [badge]``.

    ``label_width`` left-pads the label so a column's hints line up. Rich markup
    (colour) is the renderer's job — this stays plain so it is assertable.
    """
    label = item.label.ljust(label_width) if label_width else item.label
    parts = [label.rstrip() if not item.hint else label]
    if item.hint:
        parts.append(item.hint)
    text = "   ".join(p for p in parts if p)
    if item.badge:
        text = f"{text}  [{item.badge}]"
    return text


def build_choices(screen: MenuScreen, *, at_root: bool) -> List[Tuple[str, str]]:
    """Return ``[(label, value)]`` for a screen plus its nav controls.

    Non-root screens get a ``← Back`` control; every screen gets ``Quit``. Pure:
    the caller wraps each pair in ``questionary.Choice``.
    """
    width = max((len(it.label) for it in screen.items), default=0)
    pairs: List[Tuple[str, str]] = [
        (format_item_label(it, label_width=width), it.key) for it in screen.items
    ]
    if not at_root:
        pairs.append(("← Back", BACK))
    pairs.append(("Quit", QUIT))
    return pairs


def run_menu(
    root: MenuScreen,
    *,
    render_header: Optional[Callable[[str], None]] = None,
) -> int:
    """Drive a stack of screens until the user quits. Returns ``0``.

    Maintains a breadcrumb stack starting at ``root``. Each turn: render the
    header (if given) with the current trail, present the screen's choices, then
    dispatch — a branch pushes its child, a leaf runs its action, ``Back`` pops,
    ``Quit`` (or an aborted prompt) exits. ``Back`` is only offered off the root,
    so the stack never underflows.
    """
    import questionary  # caller guarantees this import succeeds

    stack: List[MenuScreen] = [root]
    while stack:
        screen = stack[-1]
        if render_header is not None:
            render_header(format_breadcrumb([s.title for s in stack]))

        choices = [
            questionary.Choice(label, value=value)
            for label, value in build_choices(screen, at_root=len(stack) == 1)
        ]
        selection = questionary.select(screen.prompt, choices=choices).ask()

        if selection is None or selection == QUIT:
            return 0
        if selection == BACK:
            stack.pop()
            continue

        item = screen.item(selection)
        if item is None:
            continue
        if item.is_branch():
            child = item.submenu()  # type: ignore[misc]
            if child is not None:
                stack.append(child)
        elif item.action is not None:
            item.action()
    return 0
