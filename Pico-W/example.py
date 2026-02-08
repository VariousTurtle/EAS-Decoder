'''
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
'''

"""
Tutorials
- Raspberry Pi Pico - LCD I2C 16x2: https://newbiely.com/tutorials/raspberry-pico/raspberry-pi-pico-lcd-i2c
- Raspberry Pi Pico - LCD I2C 20x4: https://newbiely.com/tutorials/raspberry-pico/raspberry-pi-pico-lcd-20x4
- ESP32 MicroPython - LCD I2C 16x2: https://newbiely.com/tutorials/esp32-micropython/esp32-micropython-lcd-i2c
- ESP32 MicroPython - LCD I2C 20x4: https://newbiely.com/tutorials/esp32-micropython/esp32-micropython-lcd-20x4
"""

from machine import I2C, Pin
from DIYables_MicroPython_LCD_I2C import LCD_I2C
import utime

# The I2C address of your LCD (Update if different)
I2C_ADDR = 0x27  # Use the address found using the I2C scanner

# Define the number of rows and columns on your LCD
LCD_ROWS = 4
LCD_COLS = 20

# Initialize I2C
i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400000)

# Initialize LCD
lcd = LCD_I2C(i2c, I2C_ADDR, LCD_ROWS, LCD_COLS)

# Setup function
lcd.backlight_on()
lcd.clear()

# Main loop function
while True:
    lcd.clear()
    lcd.set_cursor(3, 0) # Move the cursor to column 3, row 0 (first row)
    lcd.print("DIYables")
    lcd.set_cursor(0, 1) # Move the cursor to column 0, row 1 (second row)
    lcd.print("www.diyables.io")
    utime.sleep(2)
    
    lcd.clear()
    lcd.set_cursor(0, 0) # Move to the beginning of the first row
    lcd.print("Int: ")
    lcd.print(str(1234))  # Print integer
    lcd.set_cursor(0, 1)  # Move to the beginning of the second row
    lcd.print("Float: ")
    lcd.print(str(56.78))  # Print float
    utime.sleep(2)
