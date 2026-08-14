"""AFKing -- system-tray app.

Double-click AFKing.exe and it starts keeping you "online" right away,
living quietly in the system tray (bottom-right, by the clock).

Right-click the tray icon to:
  * toggle Active on/off (the check mark shows the current state)
  * Quit

Only one instance can run at a time: launching a second copy just points
you to the one already in the tray instead of stacking up duplicate icons.

This module is the exe entry point. All the actual keep-awake logic
lives in afk_engine.py; the icon drawing lives in icon.py.
"""

import ctypes

import pystray
from pystray import Menu, MenuItem

from afk_engine import Jiggler, already_running
from icon import make_image

jiggler = Jiggler()

# MessageBox flags: info icon, bring to front, stay on top.
_MB_INFO = 0x40 | 0x10000 | 0x40000

_ALREADY_RUNNING_TEXT = (
    "AFKing is already running.\n\n"
    "Look for the green coffee-mug icon in your system tray "
    "(bottom-right, next to the clock). If you don't see it, click the "
    "^ arrow to show hidden icons.\n\n"
    "Right-click the mug to pause or quit."
)


def _message_box(text, title="AFKing"):
    ctypes.windll.user32.MessageBoxW(0, text, title, _MB_INFO)


def _refresh(icon):
    icon.icon = make_image(jiggler.active)
    icon.title = "AFKing — active" if jiggler.active else "AFKing — paused"
    icon.update_menu()


def on_toggle(icon, _item):
    if jiggler.active:
        jiggler.stop()
    else:
        jiggler.start()
    _refresh(icon)


def on_quit(icon, _item):
    jiggler.stop()
    icon.stop()


def _on_ready(icon):
    # Called once the tray loop has started: show the icon and let the user
    # know it's up, so they don't assume nothing happened and relaunch it.
    icon.visible = True
    try:
        icon.notify(
            "AFKing is active — right-click the mug to pause or quit.",
            "AFKing",
        )
    except Exception:
        pass  # notifications are best-effort (Focus Assist, unsupported, etc.)


def main():
    # One instance only. A second launch just points the user to the first.
    if already_running():
        _message_box(_ALREADY_RUNNING_TEXT)
        return

    # Start protecting the user the moment the app opens.
    jiggler.start()

    menu = Menu(
        MenuItem(
            "Active",
            on_toggle,
            checked=lambda _item: jiggler.active,
        ),
        Menu.SEPARATOR,
        MenuItem("Quit", on_quit),
    )

    icon = pystray.Icon(
        "AFKing",
        make_image(jiggler.active),
        "AFKing — active",
        menu,
    )
    icon.run(setup=_on_ready)


if __name__ == "__main__":
    main()
