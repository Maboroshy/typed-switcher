#!/usr/bin/env python3

import time
import logging
import getpass
import selectors
import collections
from typing import Tuple, Union

import evdev
from evdev.ecodes import *  # For an easier configuration only


### Configuration: ###

# All key names are listed in /usr/include/linux/input-event-codes.h

# Your system's "switch to next keyboard layout" shortcut which will be emulated by Typed Switcher
next_layout_key_shortcut = (KEY_LEFTALT, KEY_LEFTSHIFT)

# The key you want to use to switch keyboard layout and retype the text
switch_and_retype_key = KEY_PAUSE

# Set to `True` for more output about input events and app state
verbose = False

### Configuration ends here ###


ecode = int  # type hint for evdev.ecodes which are variables with assigned int values


class Switcher:
    # All possible alphanumeric keys from '~' to '?'
    active_keycodes = set(range(2, 58))
    # Exclude Tab, Enter, L_Control, L_Alt. Keep shifts, space, backspace.
    active_keycodes.difference_update((15, 28, 29, 56))

    sleep_time_between_key_presses = 0.01
    keys_pressed = set()

    def __init__(self):
        self.fake_kb_name = 'Typed Switcher input emulator'
        self.fake_kb = evdev.UInput(name=self.fake_kb_name)

        self.event_buffer = collections.deque(maxlen=1000)  # ~ 500 characters max
        self.chars_in_buffer_count = 0

    def tap_keys(self, key_codes: Union[ecode, Tuple[ecode, ...]], n_times: int = 1) -> None:
        """ Press and release a multiple keys simultaneously """
        if type(key_codes) is not tuple:
            key_codes = (key_codes,)

        for _ in range(0, n_times):
            time.sleep(self.sleep_time_between_key_presses)
            for key_code in key_codes:
                self.fake_kb.write(evdev.ecodes.EV_KEY, key_code, 1)
            self.fake_kb.syn()
            time.sleep(self.sleep_time_between_key_presses)
            for key_code in key_codes:
                self.fake_kb.write(evdev.ecodes.EV_KEY, key_code, 0)
            self.fake_kb.syn()
            logging.debug(f'{[evdev.ecodes.keys[key_code] for key_code in key_codes]} tapped')

    def switch_and_retype(self) -> None:
        # Delete typed characters
        self.tap_keys(evdev.ecodes.KEY_BACKSPACE, self.chars_in_buffer_count)

        # Switch to next keyboard layout
        self.tap_keys(next_layout_key_shortcut)

        # Retype text by emulating buffered events
        for event in self.event_buffer:
            time.sleep(self.sleep_time_between_key_presses)
            self.fake_kb.write(evdev.ecodes.EV_KEY, event.code, event.value)
            self.fake_kb.syn()
            logging.debug(f'Fake kb: {evdev.categorize(event)}')

    def clear_buffer(self) -> None:
        """ Forget previous input events """
        self.event_buffer.clear()
        self.chars_in_buffer_count = 0
        logging.info('Buffer cleared')

    def handle_event(self, event: evdev.events.InputEvent) -> None:
        """ Main app logic. App reaction to input events. """
        if event.code in self.active_keycodes:
            # Active key events go to buffer to be emulated later for retyping text
            self.event_buffer.append(event)

            # Characters are counted to know how much times to press backspace before retyping
            if event.value == 0:
                if event.code == evdev.ecodes.KEY_BACKSPACE:
                    if self.chars_in_buffer_count > 0:
                        self.chars_in_buffer_count -= 1
                elif event.code not in (evdev.ecodes.KEY_LEFTSHIFT, evdev.ecodes.KEY_RIGHTSHIFT):
                    self.chars_in_buffer_count += 1

            logging.debug(f'{self.chars_in_buffer_count} characters in buffer')

        # Switch key release triggers the switch and retype
        elif event.code == switch_and_retype_key:
            if not event.value == 0:
                return

            logging.info('Switch key pressed')
            self.switch_and_retype()

        # Any other event including mouse/controller buttons clears the buffer
        else:
            self.clear_buffer()

    def listen_input(self) -> None:
        """ Reads events from all input devices and passes it to handle_event """
        device_selector = selectors.DefaultSelector()
        for device in [evdev.InputDevice(path) for path in evdev.list_devices()]:
            if device.name != self.fake_kb_name:
                device_selector.register(device, selectors.EVENT_READ)

        while True:
            for key, mask in device_selector.select():
                time.sleep(0.01)
                device = key.fileobj
                for event in device.read():
                    # Only keyboard key and mouse/controller button events are handled
                    if event.type == evdev.ecodes.EV_KEY:
                        logging.debug(f'Real kb: {evdev.categorize(event)}')
                        self.handle_event(event)


if __name__ == '__main__':
    if getpass.getuser() != 'root':
        print('Typed Switcher can only be run by root.\n'
              'Try running "sudo python3 typed_switcher.py" or set a systemd unit.')
        exit(126)

    if verbose:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO

    logging.basicConfig(level=logging_level, format='%(message)s')

    typed_switcher = Switcher()
    typed_switcher.listen_input()
