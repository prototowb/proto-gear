"""Unit tests for the pure navigation primitives (PROTO-096, §5.7).

The data model, breadcrumb, and choice builders in ``module_core.nav`` are
framework-free, so they test directly. ``run_menu`` is driven with a scripted
fake ``questionary`` (same convention as the browser tests) to prove the
back-stack, dispatch, and quit semantics without a TTY.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from proto_gear_pkg.module_core import nav


# --------------------------------------------------------------------------- #
# Pure builders
# --------------------------------------------------------------------------- #
class TestPureBuilders:
    def test_breadcrumb_joins_titles(self):
        assert nav.format_breadcrumb(["Home", "Tickets"]) == "Home › Tickets"

    def test_breadcrumb_skips_empty(self):
        assert nav.format_breadcrumb(["Home", "", "Update"]) == "Home › Update"

    def test_item_label_plain(self):
        item = nav.MenuItem("k", "Status", hint="current state")
        assert nav.format_item_label(item) == "Status   current state"

    def test_item_label_with_badge(self):
        item = nav.MenuItem("k", "Doctor", hint="drift audit", badge="2 warnings")
        assert nav.format_item_label(item).endswith("[2 warnings]")

    def test_item_label_padding_aligns(self):
        item = nav.MenuItem("k", "Go", hint="x")
        # ``label_width`` pads the label so hints line up in a column.
        assert nav.format_item_label(item, label_width=6) == "Go       x"

    def test_is_branch(self):
        leaf = nav.MenuItem("a", "A", action=lambda: None)
        branch = nav.MenuItem("b", "B", submenu=lambda: nav.MenuScreen("B"))
        assert not leaf.is_branch()
        assert branch.is_branch()

    def test_build_choices_root_has_quit_no_back(self):
        screen = nav.MenuScreen("Home", items=[nav.MenuItem("a", "A")])
        values = [v for _, v in nav.build_choices(screen, at_root=True)]
        assert values == ["a", nav.QUIT]

    def test_build_choices_child_has_back_then_quit(self):
        screen = nav.MenuScreen("Sub", items=[nav.MenuItem("a", "A")])
        values = [v for _, v in nav.build_choices(screen, at_root=False)]
        assert values == ["a", nav.BACK, nav.QUIT]

    def test_screen_item_lookup(self):
        screen = nav.MenuScreen("S", items=[nav.MenuItem("a", "A")])
        assert screen.item("a").label == "A"
        assert screen.item(nav.QUIT) is None


# --------------------------------------------------------------------------- #
# run_menu with a scripted fake questionary
# --------------------------------------------------------------------------- #
class _FakeChoice:
    def __init__(self, title, value):
        self.title = title
        self.value = value


class _FakePrompt:
    def __init__(self, answer):
        self._answer = answer

    def ask(self):
        return self._answer


class _FakeQuestionary:
    Choice = _FakeChoice

    def __init__(self, selects):
        self._selects = list(selects)
        self.select_calls = 0

    def select(self, *a, **k):
        self.select_calls += 1
        return _FakePrompt(self._selects.pop(0))


class TestRunMenu:
    def _run(self, monkeypatch, root, selects, headers=None):
        monkeypatch.setitem(sys.modules, "questionary", _FakeQuestionary(selects))
        cb = None
        if headers is not None:
            cb = lambda crumb: headers.append(crumb)
        return nav.run_menu(root, render_header=cb)

    def test_quit_immediately(self, monkeypatch):
        hits = []
        root = nav.MenuScreen(
            "Home", items=[nav.MenuItem("a", "A", action=lambda: hits.append("a"))]
        )
        assert self._run(monkeypatch, root, ["__quit__"]) == 0
        assert hits == []

    def test_none_selection_quits(self, monkeypatch):
        root = nav.MenuScreen("Home", items=[nav.MenuItem("a", "A")])
        assert self._run(monkeypatch, root, [None]) == 0

    def test_leaf_action_dispatched(self, monkeypatch):
        hits = []
        root = nav.MenuScreen(
            "Home", items=[nav.MenuItem("a", "A", action=lambda: hits.append("a"))]
        )
        assert self._run(monkeypatch, root, ["a", "__quit__"]) == 0
        assert hits == ["a"]

    def test_submenu_push_and_back(self, monkeypatch):
        hits = []
        child = nav.MenuScreen(
            "Sub", items=[nav.MenuItem("x", "X", action=lambda: hits.append("x"))]
        )
        root = nav.MenuScreen(
            "Home", items=[nav.MenuItem("s", "S", submenu=lambda: child)]
        )
        # Enter sub, run X, Back to root, quit.
        assert self._run(monkeypatch, root, ["s", "x", "__back__", "__quit__"]) == 0
        assert hits == ["x"]

    def test_breadcrumb_reflects_depth(self, monkeypatch):
        headers = []
        child = nav.MenuScreen("Tickets", items=[nav.MenuItem("x", "X")])
        root = nav.MenuScreen(
            "Home", items=[nav.MenuItem("s", "Tickets", submenu=lambda: child)]
        )
        self._run(monkeypatch, root, ["s", "__back__", "__quit__"], headers=headers)
        assert headers[0] == "Home"
        assert headers[1] == "Home › Tickets"
        assert headers[2] == "Home"


class TestSinglePage:
    """Optional clear-before-render / pause-after-action behaviour."""

    def _run(self, monkeypatch, root, selects, *, clear=None, pause=None):
        monkeypatch.setitem(sys.modules, "questionary", _FakeQuestionary(selects))
        return nav.run_menu(root, clear=clear, pause=pause)

    def test_clear_called_before_each_render(self, monkeypatch):
        clears = []
        child = nav.MenuScreen("Sub", items=[nav.MenuItem("x", "X")])
        root = nav.MenuScreen(
            "Home", items=[nav.MenuItem("s", "S", submenu=lambda: child)]
        )
        # root render, child render, root render again after Back = 3 clears.
        self._run(
            monkeypatch,
            root,
            ["s", "__back__", "__quit__"],
            clear=lambda: clears.append(1),
        )
        assert len(clears) == 3

    def test_pause_only_after_leaf_action(self, monkeypatch):
        pauses = []
        hits = []
        child = nav.MenuScreen(
            "Sub", items=[nav.MenuItem("x", "X", action=lambda: hits.append("x"))]
        )
        root = nav.MenuScreen(
            "Home", items=[nav.MenuItem("s", "S", submenu=lambda: child)]
        )
        # Enter sub (no pause), run X (pause once), Back (no pause), quit.
        self._run(
            monkeypatch,
            root,
            ["s", "x", "__back__", "__quit__"],
            pause=lambda: pauses.append(1),
        )
        assert hits == ["x"]
        assert len(pauses) == 1

    def test_no_clear_or_pause_by_default(self, monkeypatch):
        # Omitting both keeps the plain scrolling behaviour (no crash, runs action).
        hits = []
        root = nav.MenuScreen(
            "Home", items=[nav.MenuItem("a", "A", action=lambda: hits.append("a"))]
        )
        assert self._run(monkeypatch, root, ["a", "__quit__"]) == 0
        assert hits == ["a"]
