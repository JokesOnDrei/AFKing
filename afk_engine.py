"""AFKing input engine (Windows, dependency-free).

Keeps the Windows idle timer from advancing so Teams/Slack/etc. stay
"green" instead of flipping to Away. It does this with real, injected
input via the Win32 SendInput API:

  * a 1-pixel relative mouse jiggle (moves +1 then -1, so the cursor
    ends up where it started), and
  * a press of F15 -- a key that exists in the keycode space but that no
    physical keyboard sends and virtually nothing binds, so it has no
    side effect on whatever app is focused.

Why SendInput instead of pyautogui's moveTo(): absolute cursor moves can
go through SetCursorPos, which repositions the pointer WITHOUT reliably
resetting the idle timer (GetLastInputInfo). Injected SendInput events --
mouse or keyboard -- always reset it. That is the whole trick.
"""

import ctypes
import random
import threading
from ctypes import wintypes

user32 = ctypes.WinDLL("user32", use_last_error=True)

# --- Win32 SendInput plumbing -------------------------------------------------

ULONG_PTR = wintypes.WPARAM  # pointer-sized integer (correct on 32- and 64-bit)

INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
MOUSEEVENTF_MOVE = 0x0001
KEYEVENTF_KEYUP = 0x0002
VK_F15 = 0x7E  # no keyboard sends this; the classic "no-op" keep-awake key


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class _INPUTunion(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("u", _INPUTunion)]


user32.SendInput.argtypes = (wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int)
user32.SendInput.restype = wintypes.UINT


def _send(*inputs):
    n = len(inputs)
    arr = (INPUT * n)(*inputs)
    user32.SendInput(n, arr, ctypes.sizeof(INPUT))


def _mouse_move(dx, dy):
    mi = MOUSEINPUT(dx, dy, 0, MOUSEEVENTF_MOVE, 0, 0)
    return INPUT(type=INPUT_MOUSE, u=_INPUTunion(mi=mi))


def _key(vk, up=False):
    flags = KEYEVENTF_KEYUP if up else 0
    ki = KEYBDINPUT(vk, 0, flags, 0, 0)
    return INPUT(type=INPUT_KEYBOARD, u=_INPUTunion(ki=ki))


def nudge():
    """Emit one round of harmless input that resets the idle timer."""
    _send(_mouse_move(1, 0))
    _send(_mouse_move(-1, 0))
    _send(_key(VK_F15), _key(VK_F15, up=True))


# --- Idle detection -----------------------------------------------------------

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.UINT), ("dwTime", wintypes.DWORD)]


def idle_ms():
    """Milliseconds since the last real OR injected input, system-wide.

    Reads Win32 GetLastInputInfo. Note our own nudge() counts as input and
    resets this to ~0, which is exactly what the idle-aware loop relies on.
    """
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    user32.GetLastInputInfo(ctypes.byref(lii))
    # GetTickCount() (32-bit) to stay in the same domain as dwTime; the
    # ~49.7-day wrap is irrelevant for this tool (at worst one extra nudge).
    return ctypes.c_uint32(kernel32.GetTickCount() - lii.dwTime).value


# --- Single-instance guard ----------------------------------------------------

_ERROR_ALREADY_EXISTS = 183
_MUTEX_NAME = "AFKing-SingleInstance-6f1c9d2a"
_mutex_handle = None  # kept alive for the whole process lifetime (see below)


def already_running():
    """Return True if another AFKing instance is already running.

    Creates a named Win32 mutex. If the mutex already exists, another
    instance holds it and we're the duplicate. The handle is intentionally
    parked in a module global so the OS keeps the lock for as long as this
    process lives, and releases it automatically on exit or crash -- so
    there are no stale lock files to clean up.
    """
    global _mutex_handle
    kernel32.CreateMutexW.restype = wintypes.HANDLE
    kernel32.CreateMutexW.argtypes = (
        wintypes.LPVOID,
        wintypes.BOOL,
        wintypes.LPCWSTR,
    )
    _mutex_handle = kernel32.CreateMutexW(None, False, _MUTEX_NAME)
    return ctypes.get_last_error() == _ERROR_ALREADY_EXISTS


# --- Background jiggler --------------------------------------------------------

class Jiggler:
    """Idle-aware background jiggler.

    Every ``check_interval`` seconds it looks at how long the user has been
    inactive and only calls nudge() once they've been idle for at least
    ``idle_threshold`` seconds. So while the user is actually at the desk
    the jiggler does nothing (zero cursor interference, tray stays instantly
    clickable); it only kicks in once they've genuinely stepped away.

    Because our own nudge resets the idle timer, idle_ms() drops back below
    the threshold right after we fire, so we hold off until it climbs again
    -- netting roughly one nudge per idle_threshold while away. 60s is well
    under the ~5-minute Teams "Away" cutoff, so status never drops.

    start()/stop() are safe to call repeatedly.
    """

    def __init__(self, idle_threshold=60.0, check_interval=5.0):
        self.idle_threshold = idle_threshold
        self.check_interval = check_interval
        self._active = False
        self._stop = threading.Event()
        self._thread = None

    @property
    def active(self):
        return self._active

    def start(self):
        if self._active:
            return
        self._active = True
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._active = False
        self._stop.set()

    def _run(self):
        threshold_ms = self.idle_threshold * 1000
        while not self._stop.is_set():
            if idle_ms() >= threshold_ms:
                nudge()
            # A little jitter keeps the cadence from looking mechanical.
            # wait() wakes immediately on stop(), so quitting is instant.
            self._stop.wait(self.check_interval + random.uniform(0, 1.0))
