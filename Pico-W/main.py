from machine import I2C, Pin
from DIYables_MicroPython_LCD_I2C import LCD_I2C
from time import sleep
import time
import sys

I2C_ADDR = 0x27  
LCD_ROWS = 4
LCD_COLS = 20

i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400000)
lcd = LCD_I2C(i2c, I2C_ADDR, LCD_ROWS, LCD_COLS)

lcd.backlight_on()
lcd.clear()

Rec_led = Pin(0, Pin.OUT)
Audio_Playing_led = Pin(1,Pin.OUT)

def println(string,col,ln):
    lcd.set_cursor(col,ln)
    lcd.print(string)

println('hello world', 0,2)
