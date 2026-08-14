# AFKing ☕

AFKing keeps your Teams/Slack status **green** while you're away from your desk — no more sneaky "Away" when you grab a coffee.<br>
It's a tiny Windows app that lives in your system tray: **download it, double-click it, forget it.** Perfect for "Work From Bali" energy.

> Use for fun. Don't get fired! You're technically not *lying*... just letting a 1-pixel wiggle do the talking 😏

## 🛠️ What It Does
- Lives quietly in the **system tray** (bottom-right, near the clock) — green mug = active.
- **Idle-aware:** while you're actually using your PC it does *nothing*. It only kicks in once you've genuinely stepped away, then nudges just enough to keep your status active.
- The "nudge" is invisible: a **1-pixel jiggle** (the cursor ends up exactly where it was) plus a harmless `F15` keypress that no app reacts to. It never fights your mouse or types into whatever's open.
- **One-click simple:** no Python, no install, no setup. Just one small `.exe`.
- Launch it twice by accident? No problem — it just points you back to the one already running instead of piling up icons.

## ⬇️ Get AFKing

Grab the latest ready-to-run app here — you only need the single `AFKing.exe` file, nothing else:

### 👉 **[Download AFKing.exe](https://github.com/JokesOnDrei/AFKing/releases/latest)**

(On the release page, click **`AFKing.exe`** under **Assets** to download.)

## ▶️ How to Use (no coding needed)

**1. Download & open it**

Download `AFKing.exe` from the link above and double-click it.

> 💡 First time only: Windows may show a blue **"Windows protected your PC"** box (because the app isn't code-signed — it's harmless). Just click **More info → Run anyway**.

<!-- 📸 TODO screenshot: the SmartScreen "More info / Run anyway" dialog.
     Save it as docs/step1-smartscreen.png, then uncomment the line below. -->
<!-- ![Click "More info" then "Run anyway"](docs/step1-smartscreen.png) -->

**2. Look for the green mug in your tray**

A green coffee-mug icon appears at the bottom-right, near the clock. That's it — you're covered! If you don't see it, click the little **`^` arrow** to show hidden icons.

<!-- 📸 TODO screenshot: the green mug icon in the system tray (maybe with the ^ arrow expanded).
     Save it as docs/step2-tray-icon.png, then uncomment the line below. -->
<!-- ![The green mug lives in your system tray](docs/step2-tray-icon.png) -->

**3. Pause or stop it anytime**

**Right-click** the mug icon:
- **Active** — click to *pause* (the mug turns gray). Click again to resume.
- **Quit** — stops it completely and closes the app.

<!-- 📸 TODO screenshot: the right-click tray menu showing "Active" and "Quit".
     Save it as docs/step3-menu.png, then uncomment the line below. -->
<!-- ![Right-click for Active / Quit](docs/step3-menu.png) -->

> Because AFKing goes quiet the instant you touch the mouse or keyboard, reaching the tray to stop it is always effortless — nothing to fight against. 👍

## ⚠️ Good to Know
- **Antivirus might flag it.** Any "keep-awake" tool can trip this; it's a false positive. This build keeps its dependencies minimal to reduce the chance, but it can't be fully avoided without a paid signing certificate.
- **Locking your PC (Win+L) defeats it.** When Windows is locked, Teams flips you to *Away* from the lock event itself — no tool can beat that. To stay green, leave the session unlocked (a personal screen-privacy filter is your friend 😉).

---

## 🧑‍💻 For Developers

### Build `AFKing.exe` from source
You need **Python 3** installed. Then, from the project folder:

```bat
build.bat
```

That installs the dependencies + PyInstaller, generates the icon, and produces a single standalone file at `dist\AFKing.exe`. Copy that one file anywhere — people running it need **nothing** installed.

### Run without building
```bash
pip install -r requirements.txt
python afking.py
```

The keep-awake engine ([afk_engine.py](afk_engine.py)) uses only the Python standard library (`ctypes` + Win32 `SendInput`/`GetLastInputInfo`). The extra dependencies (`pystray`, `Pillow`) are just for the tray icon UI.

### Project layout
| File | Purpose |
|------|---------|
| [afking.py](afking.py) | The tray app — entry point for the exe |
| [afk_engine.py](afk_engine.py) | Dependency-free idle-aware keep-awake engine |
| [icon.py](icon.py) | Draws the green/gray mug tray icon |
| [make_icon.py](make_icon.py) | Generates `afking.ico` for the exe |
| [build.bat](build.bat) | One-click build → `dist\AFKing.exe` |
| [away.py](away.py) | Legacy cross-platform console version (needs `pip install pyautogui pynput`) |

---
## ✋ One Last Thing
Use for fun. Don't get fired! 😏
