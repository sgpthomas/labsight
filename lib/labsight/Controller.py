import serial
import serial.tools.list_ports as list
from serial.serialutil import SerialException
import io
from time import sleep

def getMotors (config_folder = ""):
    # some stuff
    
