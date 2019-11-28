# Typed Switcher

Typed Switcher is a keyboard layout switcher for the text you've just typed. It works only on GNU/Linux.

If you typed a word or two and found out you've used the wrong keyboard layout - press the key and Typed Switcher will switch layout and retype the text for you.

Features:
- Works on kernel input interface level (evdev);
- Works everywhere: X Server, Wayland compositors, even virtual console (tty);
- Works on any desktop environment, with any layouts and any number of layouts; 
- Doesn't save or send anything, transparent Python script.

## Dependencies:

- [Python 3.6+](https://www.python.org) (pre-installed in most GNU/Linux distributions);
- [python3-evdev](https://python-evdev.readthedocs.io/en/latest/install.html#) (available in major GNU/Linux distributions repositories).

## Configuration 

The configuration is set inside `typed_switcher.py` file.

The key names for settings values can be found in `/usr/include/linux/input-event-codes.h`.

`next_layout_key_shortcut = (KEY_LEFTALT, KEY_LEFTSHIFT)` - your system's "switch to next keyboard layout" shortcut which will be emulated by Typed Switcher.  
Other values examples: `(KEY_LEFTCTRL, KEY_LEFTSHIFT)`, `(KEY_LEFTALT, KEY_SPACE)`, `KEY_CAPSLOCK` etc.

`switch_and_retype_key = KEY_PAUSE` - the key you want to use to switch keyboard layout and retype the text.  
Other values examples: `KEY_F12`, `KEY_RIGHTCTRL` etc.  
Switch key's original event is not suppressed, so don't set it to anything meaningful for the apps you use.

`verbose = False` - set to `True` for more output about input events and app state.

## Installation

Typed Switcher listens input events from `/dev/input/`, so it must be run as root to work.

To test the app:
1. Configure it by setting your system's next layout key shortcut and a switch key in `typed_switcher.py`;
2. Run `sudo python3 typed_switcher.py` in terminal from the path you've put it.

To run the app at system start-up with a systemd service:
1. Configure it;
1. Place `typed_switcher.py` to `/root/`, set its write permission to root only;
2. Place `typed-switcher.service` to `/etc/systemd/system/`, set its write permission to root only;
3. Run `sudo systemctl enable --now typed-switcher` in terminal to run service now and enable running it at start-up.

## Usage

Type the text into any app or even virtual console and press the "switch and retype" key you've set.

Typed Switcher will: 
1. Delete the characters you've typed;
2. Switch to the next keyboard layout;
3. Type in the text you've typed using that next layout.

You can press "switch and retype" key again to cycle the text through your system's layouts.

For example:
- English and Russian layouts: `test` -> `еуые` -> `test` -> `еуые` ...
- English, Russian, Japanese, Greek layouts: `test` -> `еуые` -> `カイトカ` -> `τεστ` -> `test` ...

The app sees any non-alphanumeric key presses (excluding space, backspace and shifts) or mouse clicks as a change on context.  
It will retype all the text typed after the last change of context.  

Don't run two instances of the app, they will interfere.