"""
This MicroPython library is designed for any hardware plaform that supports MicroPython such as Raspberry Pi Pico, ESP32, Micro:bit... to work with the LCD I2C. It is created by DIYables to work with DIYables LCD I2C, but also work with other brand LCD I2C. Please consider purchasing products from DIYables to support our work.

Product Link:
- [LCD I2C 16x2](https://diyables.io/products/lcd-i2c-16x2-blue-background)
- [LCD I2C 20x4](https://diyables.io/products/lcd-20x4-display-i2c-interface)


Copyright (c) 2024, DIYables.io. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

- Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.

- Redistributions in binary form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in the
  documentation and/or other materials provided with the distribution.

- Neither the name of the DIYables.io nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY DIYABLES.IO "AS IS" AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL DIYABLES.IO BE LIABLE FOR ANY DIRECT,
INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

from machine import I2C, Pin
from time import sleep_ms

class LCD_I2C:
    # LCD Commands
    LCD_CLR = 0x01
    LCD_HOME = 0x02

    LCD_ENTRY_MODE = 0x04
    LCD_ENTRY_INC = 0x02
    LCD_ENTRY_SHIFT = 0x01

    LCD_ON_CTRL = 0x08
    LCD_ON_DISPLAY = 0x04
    LCD_ON_CURSOR = 0x02
    LCD_ON_BLINK = 0x01

    LCD_MOVE = 0x10
    LCD_MOVE_DISP = 0x08
    LCD_MOVE_RIGHT = 0x04

    LCD_FUNCTION = 0x20
    LCD_FUNCTION_8BIT = 0x10
    LCD_FUNCTION_2LINES = 0x08
    LCD_FUNCTION_10DOTS = 0x04
    LCD_FUNCTION_RESET = 0x30

    LCD_CGRAM = 0x40
    LCD_DDRAM = 0x80

    LCD_RS_CMD = 0
    LCD_RS_DATA = 1

    LCD_RW_WRITE = 0
    LCD_RW_READ = 1

    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.num_lines = num_lines
        self.num_columns = num_columns
        self._current_state = 0x00
        self._backlight = 0x08

        sleep_ms(20)
        self.hal_write_init_nibble(self.LCD_FUNCTION_RESET)
        sleep_ms(5)
        self.hal_write_init_nibble(self.LCD_FUNCTION_RESET)
        sleep_ms(1)
        self.hal_write_init_nibble(self.LCD_FUNCTION_RESET)
        sleep_ms(1)
        self.hal_write_init_nibble(self.LCD_FUNCTION)
        sleep_ms(1)

        self.init_lcd()

    def hal_write_init_nibble(self, nibble):
        byte = ((nibble >> 4) & 0x0F) << 4
        self.i2c.writeto(self.i2c_addr, bytes([byte | self.LCD_RS_CMD | self._backlight]))
        self.hal_pulse_enable(byte)

    def hal_backlight_on(self):
        self._backlight = 0x08
        self.i2c.writeto(self.i2c_addr, bytes([self._current_state | self._backlight]))

    def hal_backlight_off(self):
        self._backlight = 0x00
        self.i2c.writeto(self.i2c_addr, bytes([self._current_state | self._backlight]))

    def hal_write_command(self, cmd):
        self._write_byte((cmd & 0xF0) | self.LCD_RS_CMD)
        self._write_byte(((cmd << 4) & 0xF0) | self.LCD_RS_CMD)
        if cmd <= 3:
            sleep_ms(5)

    def hal_write_data(self, data):
        self._write_byte((data & 0xF0) | self.LCD_RS_DATA)
        self._write_byte(((data << 4) & 0xF0) | self.LCD_RS_DATA)

    def _write_byte(self, byte):
        self.i2c.writeto(self.i2c_addr, bytes([byte | self._backlight]))
        self.hal_pulse_enable(byte)

    def hal_pulse_enable(self, byte):
        self.i2c.writeto(self.i2c_addr, bytes([byte | 0x04 | self._backlight]))
        self.i2c.writeto(self.i2c_addr, bytes([byte & ~0x04 | self._backlight]))

    def init_lcd(self):
        self.display_on()
        self.clear()
        self.set_entry_mode()

    def clear(self):
        self.hal_write_command(self.LCD_CLR)
        self.hal_sleep(3)

    def show_cursor(self):
        self.hal_write_command(self.LCD_ON_CTRL | self.LCD_ON_DISPLAY | self.LCD_ON_CURSOR)

    def hide_cursor(self):
        self.hal_write_command(self.LCD_ON_CTRL | self.LCD_ON_DISPLAY)

    def blink_cursor_on(self):
        self.hal_write_command(self.LCD_ON_CTRL | self.LCD_ON_DISPLAY | self.LCD_ON_CURSOR | self.LCD_ON_BLINK)

    def blink_cursor_off(self):
        self.hal_write_command(self.LCD_ON_CTRL | self.LCD_ON_DISPLAY | self.LCD_ON_CURSOR)

    def display_on(self):
        self.hal_write_command(self.LCD_ON_CTRL | self.LCD_ON_DISPLAY)

    def display_off(self):
        self.hal_write_command(self.LCD_ON_CTRL)

    def set_entry_mode(self, inc=True, shift=False):
        entry_mode = self.LCD_ENTRY_MODE
        if inc:
            entry_mode |= self.LCD_ENTRY_INC
        if shift:
            entry_mode |= self.LCD_ENTRY_SHIFT
        self.hal_write_command(entry_mode)

    def backlight_off(self):
        self.hal_backlight_off()

    def backlight_on(self):
        self.hal_backlight_on()

    def home(self):
        self.hal_write_command(self.LCD_HOME)
        self.hal_sleep(3)

    def set_cursor(self, col, line):
        addr = col & 0x3F
        if line & 1:
            addr += 0x40
        if line & 2:
            addr += 0x14
        self.hal_write_command(self.LCD_DDRAM | addr)

    def print(self, string):
        for char in string:
            self.hal_write_data(ord(char))

    def custom_char(self, location, charmap):
        self.hal_write_command(self.LCD_CGRAM | ((location & 7) << 3))
        self.hal_sleep(5)
        for i in range(8):
            self.hal_write_data(charmap[i])
        self.home()

    def print_custom_char(self, location):
        self.hal_write_data(location)

    def hal_sleep(self, time_ms):
        sleep_ms(time_ms)
