'''
Copyright (C) 2025  VariousTurtle

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 3
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, see
<https://www.gnu.org/licenses/>.

'''

import argparse 
from QtPy_EqualizerBar import *
import subprocess
import traceback
from qtpy.QtCore import *
from qtpy.QtWidgets import QMainWindow, QPushButton, QTextEdit, QApplication, QVBoxLayout
from qtpy import uic
from EAS2Text import EAS2Text
import pyaudio
import wave
import sounddevice as sd
import numpy as np
from os import system
import os
import I2C_LCD_driver
from gpiozero import Button, LED
import time
import socket
from socket import gethostname, gethostbyname
import sys
from termcolor import cprint
import json 


FORMAT = pyaudio.paInt16  
RATE = 44100
CHUNK = 1024
# Argparse Arguments
parser = argparse.ArgumentParser(prog='EAS-Decoder', description='EAS-Decoder: A program to Record Emergency Alerts (Decodes With Multimon-ng)')

parser.add_argument('-i', '--ip', default=None, help='Explcitly define the ip addr for the webserver ')
parser.add_argument('-l','--lcd',action='store_false', help='Run Without LCD screen')
parser.add_argument('-s', '--speed',default=0.1, help='Sets the text scroll speed of the LCD screen, Defalut is 0.1')
parser.add_argument('--Headless',action='store_true',help='Run the program in an headless state in the terminal with output to a pico-w')
parser.add_argument('-p',default=None,help='Sets the ip addr of your pico')
parser.add_argument('-a','--Audio', default=None, help='Play an online audio stream from url with mpv.')

args = parser.parse_args()

if args.Headless == True:
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    if args.p != None:
        PICO_IP = args.p
    else:
        PICO_IP = '0.0.0.0'
    PICO_PORT = 12345

    socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

alerts_buffer = {}

File_made = False
New_alert = True
Eom_count = 0
msg_to_save = ''
save_buffer = ''
header_to_buffer = ''

screen = r"""
  _____    _    ____        ____  _____ ____ ___  ____  _____ ____  _ 
 | ____|  / \  / ___|      |  _ \| ____/ ___/ _ \|  _ \| ____|  _ \| |
 |  _|   / _ \ \___ \ _____| | | |  _|| |  | | | | | | |  _| | |_) | |
 | |___ / ___ \ ___) |_____| |_| | |__| |__| |_| | |_| | |___|  _ <|_|
 |_____/_/   \_\____/      |____/|_____\____\___/|____/|_____|_| \_(_)
"""

class hardware(QObject):

    def __init__(self):
        super(hardware, self).__init__()
        global alerts_buffer
        
        self.lcd = I2C_LCD_driver.LcdDisplay()

        # Buttons
        self.btn1 = Button(12)   # Right
        self.btn2 = Button(20)   # Middle
        self.btn3 = Button(23)   # Left
        self.switch = Button(21) # LCD toggle switch

        self.audio_led = LED(17)
        self.alert_led = LED(27)
        
        self.alert_displaying = False
        self.button_pressed = False
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_buttons)
        self.timer.start(550)
        
        self.buffer_number = -1
    
    # displays text on the LCD display
    @Slot(str,str,str)
    def lcd_text(self, string, wr_1, wr_2):
        
            self.alert_displaying = True
            
            if self.switch.is_pressed:
                self.lcd.clear_lcd()
                
                # checks if the lingth of the text excedes the size display
                if len(string) > 16:
                    
                    # scrolls the message if its larger than 16 characters
                    self.lcd.lcd_scroll_text(string, delay=lcd_speed, wr_1=wr_1, wr_2=wr_2)
                
                else:
                    # if the lingth of the text is less than 16 it displays it without scrolling it
                    self.lcd.write_lcd_string(string)
            
            self.alert_displaying = False
    
    # runs in closeEvent
    def Shutdown(self):
        self.timer.stop()
        self.lcd.stop_lcd()
        self.lcd.clear_lcd()
        self.lcd.set_lcd_backlight(False)
        self.timer.stop()

    def check_buttons(self):
        
        buffer_keys = list(alerts_buffer.keys())

        # turns Display on and off with switch
        if self.alert_displaying == False:
            if self.switch.is_pressed:
                self.lcd.set_lcd_backlight(True)
                
                if self.button_pressed == False:
                    self.lcd.write_lcd_string(time.strftime('%I:%M       %m/%d/%y'))
                    self.lcd.write_lcd_string(f'      {len(buffer_keys)} Alerts', 1)
                    self.lcd.write_lcd_string('                    ',2)
                    self.lcd.write_lcd_string('   Down Select UP  ',3)
                
            else:
                if self.button_pressed == False:
                    self.lcd.clear_lcd()
                    self.lcd.set_lcd_backlight(False)
                    self.alert_led.off()
                    self.audio_led.off()

            if self.btn3.is_pressed and self.btn1.is_pressed:
                
                self.button_pressed = False
                self.buffer_number = -1
                self.lcd.clear_lcd()
                time.sleep(1)
            else:

                if self.btn1.is_pressed:
                    if self.buffer_number < len(buffer_keys)-1:
                        #Right
                        try:
                            self.buffer_number +=1        
                            
                            self.button_pressed = True
                            alert_details = buffer_keys[self.buffer_number].split(',')
                            
                            self.lcd.clear_lcd()
                            self.lcd.write_lcd_string(alert_details[0],0)
                            self.lcd.write_lcd_string(alert_details[1],1)
                            self.lcd.write_lcd_string(alert_details[2],2)
                            self.lcd.write_lcd_string(alert_details[3],3)

                            time.sleep(1)

                        except Exception as e:
                            print(self.buffer_number)
                            print(e) 
                
                if self.btn2.is_pressed:
                    if self.buffer_number <= len(buffer_keys) and self.buffer_number != -1:
                        # Middle 
                        try:
                            alert_details = buffer_keys[self.buffer_number].split(',')
                            self.lcd.clear_lcd()
                            self.lcd.lcd_scroll_text(alerts_buffer[buffer_keys[self.buffer_number]], delay=lcd_speed, wr_1=alert_details[1],wr_2=alert_details[0])

                            self.buffer_number = -1
                            self.button_pressed = False
                            
                        except Exception as e:
                                print(self.buffer_number)
                                print(e) 
                
                if self.btn3.is_pressed:
                    if self.buffer_number >0:
                        # Left
                        try:
                            self.buffer_number -=1
                            
                            self.button_pressed = True
                            alert_details = buffer_keys[self.buffer_number].split(',')
                            
                            self.lcd.clear_lcd()
                            self.lcd.write_lcd_string(alert_details[0],0)
                            self.lcd.write_lcd_string(alert_details[1],1)
                            self.lcd.write_lcd_string(alert_details[2],2)
                            self.lcd.write_lcd_string(alert_details[3],3)

                            time.sleep(1)
                        
                        except Exception as e:
                            print(self.buffer_number)
                            print(e)
                    
                    # scroll backwards to newest alert
                    elif self.buffer_number == -1 and buffer_keys:
                        try:
                            self.buffer_number = len(buffer_keys)

                            self.button_pressed = True
                            alert_details = buffer_keys[self.buffer_number].split(',')
                            
                            self.lcd.clear_lcd()
                            self.lcd.write_lcd_string(alert_details[0],0)
                            self.lcd.write_lcd_string(alert_details[1],1)
                            self.lcd.write_lcd_string(alert_details[2],2)
                            self.lcd.write_lcd_string(alert_details[3],3)

                            time.sleep(1)
                        
                        except Exception as e:
                            print(self.buffer_number)
                            print(e)
                
    def alert_led_control(self,i):
                
        if self.switch.is_pressed:
                    
            if i == 1:
                self.alert_led.on()

            elif i == 0:
                self.alert_led.off()
            
    def audio_led_control(self,i):
                
        if self.switch.is_pressed:
                    
            if i == 1:
                self.audio_led.on()

            elif i == 0:
                self.audio_led.off()
                                            
class web(QThread):
    def __init__(self):
        super(web, self).__init__()
       
        hostname = gethostname()

        # if ip address is not exexplicitly defined it gets the ip automaticly
        if IP == None:
            try:
                self.hostip = socket.gethostbyname(hostname + ".local")
            except:
                
                try:
                    self.hostip = gethostbyname(hostname)
                except Exception as e:
                    print('\nError: Unable to Get IP Address:\n',e)
        else:
            self.hostip = IP

    # starts the web server            
    def run(self):
        try:
            system(f'python3 -m http.server 8080 --bind {self.hostip}')
        except Exception as e:
            print('\nFailed to Start Webserver\n',e)

class EASAlertThread(QObject):
    new_alert_signal = Signal(str)

    def __init__(self):
        super(EASAlertThread,self).__init__()

        self.command = ["multimon-ng","-q", "-a","eas"]
        self.running = True

    @Slot()
    def run(self):
      
      # starts Multimon-mg and pipes in its output
        try:
            global Eom_count
            decoder = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            while self.running:
                output = decoder.stdout.readline()
                
                self.new_alert_signal.emit(output)

                if output == 'EAS: NNNN\n':
                    Eom_count +=1

        except Exception as e:
            traceback.print_exc()

class Main_Window(QMainWindow):
    lcd_text_string = Signal(str, str, str)  
    def __init__(self):
        super(Main_Window,self).__init__()
        
        global IP, lcd_speed
        
        self.args = args
        if self.args.Headless == True:
            self.args.lcd = False

        self.audio_level_change = None
        # Hardware Class
        self.hardware = None

        self.samplerate = 44100
        self.channels = 2
        self.recording = False
        self.audio_data = []

        if self.args.Headless == False:
            uic.loadUi("main.ui", self)

            # Widgets
            self.message_DSP = self.findChild(QTextEdit, 'Message_DSP')
            self.clear_button = self.findChild(QPushButton, 'pushButton')
            
            self.clear_button.clicked.connect(self.clear_screen) 

            # VU meter
            self.equalizer = EqualizerBar(1,100)
            self.findChild(QVBoxLayout,'verticalLayout').addWidget(self.equalizer)

        elif self.args.Headless:
            self.send_picow_data(clear_lcd=True,Screen_Data=['Waiting for Alerts..'])
            cprint(screen,color="red")
            
        # Defines Lcd scroll speed and ip address from argsparse
        IP = self.args.ip
        lcd_speed = self.args.speed

        # Starts the Alert Thread for decodeing EAS Alerts with Mulimon-ng
        self.alert_thread = QThread(self)
        self.alert = EASAlertThread()
        self.alert.new_alert_signal.connect(self.display_alert)
        self.alert.moveToThread(self.alert_thread)
        self.alert_thread.start()
        
        # keeps program from waiting for lcd to scroll
        QMetaObject.invokeMethod(self.alert, "run", Qt.QueuedConnection)

        self.webserver_thread = web()
        self.webserver_thread.start()

        if self.args.Audio:
            self.play_audio()

        # audio stream monitored by the VU Meter
        self.stream = sd.InputStream(callback=self.print_sound,channels=1,samplerate=44100,blocksize=1024)
        self.stream.start()

        # defines hardware_thread
        self.hardware_thread = QThread(self)

        # checks if lcd lcd arg is enabled
        if self.args.lcd:
            self.hardware = hardware()
            self.lcd_text_string.connect(self.hardware.lcd_text)

            # moves hardware function to thread 
            self.hardware.moveToThread(self.hardware_thread)
            self.hardware_thread.start()
        
        # timer for updateing VU Meter
        self.timer = QTimer()
        self.timer.setInterval(20)

        self.timer.timeout.connect(self.update_values)
        self.timer.start()

        self.audio_level = 0

        if not self.args.Headless:
            self.setFixedSize(1010, 600)
            self.show()
    
    def play_audio(self):
        url = self.args.Audio
        command = ['mpv',f'{url}']
        
        self.play_audio_proc = subprocess.Popen(command)


    def send_picow_data(self,Audio_Playing_Led='None', Recording_Led='None', Screen_Data='None', clear_lcd='None'):
        data = {

            "Audio_Playing": Audio_Playing_Led,
            "Recording": Recording_Led,
            "Screen": Screen_Data,
            "Clear_Lcd": clear_lcd
        }

        json_data = json.dumps(data)

        socket.sendto(json_data.encode(), (PICO_IP, PICO_PORT))

    # gets sound levels
    def print_sound(self,indata, outdata, frames, time, ):
        self.volum_norm = np.linalg.norm(indata) * 10
        self.audio_level = min(self.volum_norm,100)

    # updates VU Meter
    def update_values(self):
        if self.args.Headless == False:
            self.equalizer.setValues([self.audio_level])
        
        playing = self.audio_level > 0
        
        # turns on led on if audio is playing
        if self.hardware_thread.isRunning() and self.hardware != None:
            if playing != self.audio_level_change:
                if playing:
                    self.hardware.audio_led_control(1)
                
                else:
                    self.hardware.audio_led_control(0)
                self.audio_level_change = playing

        if self.args.Headless:
            if playing != self.audio_level_change:
                
                if playing:
                    self.send_picow_data(Audio_Playing_Led=1)
                else:
                    self.send_picow_data(Audio_Playing_Led=0)
                self.audio_level_change = playing
            
    # clears the message desplay 
    def clear_screen(self):
        if not self.args.Headless:
            self.message_DSP.clear()

    # Starts Audio Recording     
    def start(self):
        self.audio_data = []
        self.recording = True
        self.stream = sd.InputStream(samplerate=self.samplerate,channels=self.channels,dtype='int16',callback=self.callback)
        self.stream.start()
        
        # turns on led if there is an alert
        if self.hardware_thread.isRunning() and self.hardware != None and self.args.Headless == False:
            self.hardware.alert_led_control(1)
        
        if self.args.Headless:
            
            self.send_picow_data(Recording_Led=1)

    # makes a repesentation of the audio in a list
    def callback(self, indata, frames, time, status):
        if self.recording:
            self.audio_data.append(indata.copy())
    
    # stops audio Recording
    def stop(self, filename="output.wav"):
        try:
            self.recording = False
            self.stream.stop()
            self.stream.close()

            # saves Audio as a Wave File
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)
                wf.setframerate(self.samplerate)
                wf.writeframes(b''.join(np.concatenate(self.audio_data)))
            
            if self.hardware_thread.isRunning() and self.args.Headless == False:
                self.hardware.alert_led_control(0)
            
            if self.args.Headless:
                
                self.send_picow_data(Recording_Led=0)

        except Exception as e:
            traceback.print_exc()

    def display_alert(self, alert_text):
        global File_made, msg_to_save, alerts_buffer,save_buffer,buffer_keys,header_to_buffer, New_alert,Eom_count
        
        now = time.strftime('%m-%d-%y-%H-%M-%S')
        
        # Removes the 'EAS:' from the begining of the alert text produced by Multimon-ng and decodes it with the EAS2Text module
        header_decoded = EAS2Text(alert_text.replace('EAS:',''))

        # Reset File_made when a new alert starts (i.e., not NNNN)
        if alert_text != 'EAS: NNNN\n' and File_made:
            File_made = False

        
        # adds the Raw EAS header and the decoded Header together to be save in output.txt
        header_joined = f'{alert_text}\n{header_decoded.EASText}\n'
        
        # Displays the Message inside the Window
        if self.args.Headless == False:
            self.message_DSP.append(header_joined.replace('EAS:',''))
        
        # Displays the message inside the terminal
        elif self.args.Headless == True:
            if New_alert == True:
                cprint('\nNEW ALERT!',color="red",attrs=['bold','blink'])
                New_alert = False
            
                cprint(f'{alert_text.replace('EAS:','').strip()}',color="red")

               
            if header_decoded.EASText != 'End Of Message':
                cprint(f'Alert: {header_decoded.EASText}',color="red")
                self.send_picow_data(Screen_Data=[f'New Alert!: {header_decoded.evnt}',f'ORG: {header_decoded.org}',f'Starting: {header_decoded.startTimeText}',f'Ending: {header_decoded.endTimeText}'], clear_lcd=True,)

        # displays the message on the lcd if its not EOM
        if header_decoded.EASText != 'End Of Message' and self.hardware_thread.isRunning():
                self.lcd_text_string.emit(header_decoded.EASText,f'Event:{header_decoded.evnt}',f'Originator:{header_decoded.org}')
        
        if alert_text == 'EAS: NNNN\n':
                if not File_made:
                    try:
                        # makes new directory for new alert tp be stored 
                        system(f'mkdir -p output/{header_to_buffer.org}-{now}-{header_to_buffer.evnt}')
                        
                        # Stops audio recording and provides the directory to save it in
                        self.stop(f'output/{header_to_buffer.org}-{now}-{header_to_buffer.evnt}/output.wav')
                        File_made = True
                        
                        # flormats message to be saved in text file
                        msg = f'{msg_to_save}\nNNNN'        
                        
                        # adds Decoded Message to Alerts_Buffer dict for Lcd Display
                        alerts_buffer[f'Event:{header_to_buffer.evnt},originator:{header_to_buffer.org},From:{header_to_buffer.startTimeText[:8]},To:{header_to_buffer.endTimeText[:8]}'] = save_buffer
                        
                        # Writes Decoded Message in Output Text File
                        with open(f'output/{header_to_buffer.org}-{now}-{header_to_buffer.evnt}/output.txt', 'a') as f:
                            f.write(msg)
                        
                        # Adds the new directory name to a directories.txt
                        with open('directories.txt', 'a') as f:
                            f.write(f'{header_to_buffer.org}-{now}-{header_to_buffer.evnt}\n')

                        
                    # if it catches an EOM without getting a header 
                    except AttributeError as e:
                        pass
        
        if Eom_count == 3:

            New_alert = True
            Eom_count = 0

            if args.Headless:
                self.send_picow_data(clear_lcd=True,Screen_Data=['Waiting For Alerts..'])

        else:
            
            # stores Raw Alert Alert Header and Decoded header to save in a text file
            msg_to_save = f'{alert_text}{header_decoded.EASText}'

            # saves decoded text to be added to the alerts buffer dict
            save_buffer = f'{header_decoded.EASText}'
            
            # saves decoded header to be flormated with .evnt and .org for naming new alert in alerts buffer dict
            header_to_buffer = header_decoded

            # starts audio recording
            if not File_made:
                self.start()
            
    def closeEvent(self,event):
        
        # kills Multimon-ng and the simple HTTP Server
        system('fuser -k 8080/tcp -s')
        system('fuser -k /usr/bin/multimon-ng -s')
        
        # Shuts down the hardware thread if its running 
        if self.hardware_thread.isRunning():
            self.hardware.Shutdown()
            self.hardware_thread.quit()
            self.hardware_thread.wait()
        
        if self.args.Audio:
            self.play_audio_proc.terminate()

        # stops the timer and closese the audio stream for the VU meter      
        self.timer.stop()
        self.stream.close()

        # stops the webserver thread
        self.webserver_thread.quit()
        self.webserver_thread.wait()
    
        # stops the alert thread
        self.alert.running = False
        self.alert_thread.quit()
        self.alert_thread.wait()
  
        sys.exit()
            
if __name__ == '__main__':
    app = QApplication([])
    window = Main_Window()
    app.exec_()