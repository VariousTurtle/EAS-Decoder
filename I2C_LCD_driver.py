import smbus
import time
from time import sleep
'''
This Code Was Sourced from: https://github.com/MrLaki5/RaspberryPi-lcd-i2c-driver
The Repository is licensed under GPL-3.0 but no copyright notice was included in its files
'''
### Clear whole display instruction
CLEAR_DISPLAY = 0x01

### Return cursor to start instruction
RETURN_HOME = 0x02

### Entry mode set instruction
ENTRYMODE_SET_MODE = 0x04
# After write of data to display move cursor left/right
MOVE_LEFT_AFTER_WRITE = 0x00
MOVE_RIGHT_AFTER_WRITE = 0x02
# Shift entire display after data write
ENTIRE_DISPLAY_SHIFT = 0x01
ENTIRE_DISPLAY_SHIFT_NOT = 0x00

### Control display state instruction
DISPLAY_CONTROL_MODE = 0x08
# Display turned ON/OFF
DISPLAY_ON = 0x04
DISPLAY_OFF = 0x00
# Cursor turned ON/OFF
DISPLAY_CURSOR_ON = 0x02
DISPLAY_CURSOR_OFF = 0x00
# Cursor position visible ON/OFF
DISPLAY_CURSOR_POS_ON = 0x01
DISPLAY_CURSOR_POS_OFF = 0x00

### Move display or cursor position instruction
SHIFT_MODE = 0x10
# Move display or cursor
DISPLAY_MOVE = 0x08
DISPLAY_CURSOR_MOVE = 0x00
# Move left or right
MOVE_LEFT = 0x00
MOVE_RIGHT = 0x04

### Function set instruction
FUNCTIONSET_MODE = 0x20
# Interface data len
EIGHT_BIT = 0x10
FOUR_BIT = 0x00
# Line number
TWO_LINE = 0x08
ONE_LINE = 0x00
# Char size
SIZE_5x10 = 0x04
SIZE_5x8 = 0x00

### Set write cursor address instruction
DDRAM_ADDRESS_SET_MODE = 0x80

### Backlight pins
BACKLIGHT_ON = 0x08
BACKLIGHT_OFF = 0x00

REGISTER_SELECT_BYTE = 0b00000001
READ_WRITE_BYTE = 0b00000010
ENABLE_BYTE = 0b00000100



class LcdDisplay:
    ### Constructor
    def __init__(self, address=0x27):
        self.running = True
        self.address = address
    
        self.bus = smbus.SMBus(1)
        self.backlight_mask = BACKLIGHT_ON
        self.row_offset = [0x00, 0x40, 0x14, 0x54]
        # Put display into 4bit mode (according to docs)
        self.write_lcd_byte(0x03)
        time.sleep(0.0045)
        self.write_lcd_byte(0x03)
        time.sleep(0.0045)
        self.write_lcd_byte(0x03)
        time.sleep(0.001)
        self.write_lcd_byte(0x02)
        # Set lines font size
        self.write_lcd_byte(FUNCTIONSET_MODE | FOUR_BIT | TWO_LINE | SIZE_5x8)
        # Turn display on with cursor turned off
        self.write_lcd_byte(DISPLAY_CONTROL_MODE | DISPLAY_ON | DISPLAY_CURSOR_OFF | DISPLAY_CURSOR_POS_OFF)
        # Clear display
        self.write_lcd_byte(CLEAR_DISPLAY)
        # Set entry mode for data that will be written fo siplay
        self.write_lcd_byte(ENTRYMODE_SET_MODE | MOVE_RIGHT_AFTER_WRITE | ENTIRE_DISPLAY_SHIFT_NOT)
        # Init wait time
        time.sleep(0.1)

    ### Internal write functions
    def write_bus_byte(self, data):
        self.bus.write_byte(self.address, data)
        # Data hold time
        time.sleep(0.0001)

    def write_lcd_four_bits(self, data):
        # Data
        self.write_bus_byte(data | self.backlight_mask)
        # Enable high
        self.write_bus_byte(data | ENABLE_BYTE | self.backlight_mask)
        time.sleep(.0005)
        # Enable low
        self.write_bus_byte((data & ~ENABLE_BYTE) | self.backlight_mask)
        time.sleep(.0001)
    
    def write_lcd_byte(self, data, mode=0b00000000):
        # Write upper 4 bits first
        self.write_lcd_four_bits((data & 0xF0) | mode)
        # Write lower 4 bits after
        self.write_lcd_four_bits(((data << 4) & 0xF0) | mode)

    ### External write functions
    def write_lcd_string(self, string_data, line=0):
        # Check if line number is supported
        if len(self.row_offset) <= line:
            print("LcdDisplay: Error: line " + str(line) + " not supported")
            return
        # Set line
        self.write_lcd_byte(DDRAM_ADDRESS_SET_MODE | self.row_offset[line])
        # Write string
        for character in string_data:
            self.write_lcd_byte(ord(character), REGISTER_SELECT_BYTE)
            
    def lcd_scroll_text(self, text, line=0, delay=0.1, wr_1=None, wr_2=None):
        for i in range(len(text) + 20):  # Assuming 16 characters on the display
            display_text = text[i:i + 20]
            self.write_lcd_string(display_text, line)
            sleep(float(delay))
            self.clear_lcd()
            if wr_1 != None:
                self.write_lcd_string(wr_1,1)
            if wr_2 != None:
                self.write_lcd_string(wr_2,2) 
            if self.running == False:
                break

    def stop_lcd(self):
        self.running = False

    ### External utility functions
    def clear_lcd(self):
        self.write_lcd_byte(CLEAR_DISPLAY)

    def set_lcd_backlight(self, turn_on=True):
        if turn_on:
            self.backlight_mask = BACKLIGHT_ON
        else:
            self.backlight_mask = BACKLIGHT_OFF
        self.write_bus_byte(self.backlight_mask)