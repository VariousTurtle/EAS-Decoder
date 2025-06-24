# EAS-Decoder

### A Program To Record Emergency Alerts

The Program Uses multimon-ng to decode the inital Raw same header.
The output of the program will be stored in a directory name output
Each new alert will create a directory.

Each recorded alert Directory will be named like this

    EAS_Origonater-Date-Time-event_type
Example

    EAS-06-12-25-18-17-36-RWT
inside of each alert directory there will be a audio recording in the wav flormat and a text document both named

    output.txt
    output.wav
the text document will contain the raw header and the header translated into readable text, Like

    EAS: ZCZC-WXR-SVR-013135-013157-013013-013297+0045-1640042-WJON/TV -
    The National Weather Service has issued a Severe Thunderstorm Warning for Barrow, GA; Gwinnett, GA; Jackson, GA; and Walton, GA; beginning at 07:42 pm and ending at 08:27 pm. Message from WJON/TV.
    NNNN

## Installation
first clone the repo

    git clone https://github.com/VariousTurtle/EAS-Decoder/
    cd EAS-Decoder

install the python requrments

    pip -r install reqirments.txt

then, install multimon-ng, Multimon-ng does the raw decodeing of the SAME Header.

    # for arch
    pacman -S multimon-ng
    # for debian
    apt install multimon-ng


If you are running this on a normal stytem without the raspbery pi hardware run the program with the --Lcd flag
    
    python main.py -l

if you are running it with the raspberry pi hardware run it without the flag

## Args
run the program with the help flag to see the a available flags

    python main.py --help

### output

    usage: EAS-Decoder [-h] [-i IP] [-l] [-s SPEED]
    
    EAS-Decoder: A program to Record Emergency Alerts (Decodes With Multimon-ng)
    
    options:
      -h, --help         show this help message and exit
      -i, --ip IP        Explcitly define the ip address for the webserver
      -l, --lcd          Run Without LCD screen
      -s, --speed SPEED  Sets the text scroll speed of the LCD screen, Defalut is 0.1


# Rasperry Pi hardware Documentation
TODO: Add Documentation For Raspberry pi hardware support





    

