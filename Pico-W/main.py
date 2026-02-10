from machine import I2C, Pin
from DIYables_MicroPython_LCD_I2C import LCD_I2C
from time import sleep
import time
import sys
import json
import network
import socket

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

def html():
    with open('setup.html') as f:
        return f.read()

# Wifi Setup
try:
    with open('secrets.json') as f:
        wifi = json.load(f)

    ssid = wifi['ssid']
    password = wifi['password']
    

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)

    while not wlan.isconnected():
        time.sleep(0.5)
    println(f'connected: ip is:',0,0)
    println(f'{wlan.ifconfig()[0]}',0,1)

except OSError:
    
    println('No wifi found!',0,0)
    println('Add WIfi credent to',0,1)
    println('secrets.json',0,2)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 12345))

while True:
    data, addr = sock.recvfrom(1024)  # Wait for incoming packet
    message = data.decode('utf-8').strip()
    print("Received from", addr, ":", message)

    if message == 'Record_led_1':
        Rec_led.value(1)
    
    elif message == 'Record_led_0':
        Rec_led.value(0)
    
    elif message == 'Audio_playing_led_1':
        Audio_Playing_led.value(1)
    
    elif message == 'Audio_playing_led_0':
        Audio_Playing_led.value(0)
    
    elif message == 'clr':
        lcd.clear()
    
    elif message == 'bk_light_0':
        lcd.backlight_off()
    
    elif message == 'bk_light_1':
        lcd.backlight_on
    else:
        pass
    