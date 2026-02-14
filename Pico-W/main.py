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
    println('Waiting For Data....',0,3)

except OSError:
    
    println('No wifi found!',0,0)
    println('Add WIfi credent to',0,1)
    println('secrets.json',0,2)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 12345))

while True:
    data, addr = sock.recvfrom(1024)
    message = data.decode('utf-8').strip()
    print("Received from", addr, ":", message)

    json_message = json.loads(message)

    if json_message['Clear_Lcd'] != 'None':
        lcd.clear()

    if json_message['Audio_Playing'] != 'None':
        Audio_Playing_led.value(json_message["Audio_Playing"])
    
    if json_message['Recording'] != 'None':
        Rec_led.value(json_message["Recording"])
    
    if json_message['Screen'] != 'None':
            screen_data = json_message["Screen"]
            x = 0
            for i in screen_data:
                println(i,0,x)
                x +=1 