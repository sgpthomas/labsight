import serial
import serial.tools.list_ports as list
from serial.serialutil import SerialException
import os
from time import sleep
from labsight.motor import Motor
from labsight.protocol import Symbol, Command, Message, sendMessage

version = "0.3"

""" Talks to available ports and creates motor object if it finds anything """
def getAttachedMotorSerials():
    # initialize return array
    motor_serials = {}

    # # print config directory
    # print("Using config directory: {}".format(config_folder))

    # search through available ports
    for port in list.comports():
        print("Found " + port.device)

        # try to connect to serial
        try:
            ser = serial.Serial(port.device, timeout=2)

            # sleep for some time to give the arduino time to reset
            sleep(2)

            # if we can establish communications with the port, get the id and then append motor object to motors
            if (establishComms(ser)):

                # get id from arduino
                response = sendMessage(Message(Symbol.GET, Command.ID, Data.NIL), ser)
                mid = response.data

                # create motor object and append it to the array
                # motors.append(Motor(config_folder, ser, ID))
                motors[mid] = ser

        except SerialException:
            print("Unable to open '{}'. This port is probably already open.")

    # return motor dictionary
    return motor_serials

def createDefaultConfigDirectory():
    path = os.path.expanduser(os.path.join("~", ".labsight", "motors"))

    # if configuration folder is not given, then use default
    if (not os.path.isdir(path)):
        print("Config Directory doesn't exist. Generating a new one.")
        os.makedirs(path)

    return path

def establishComms(ser):
    # send initial message
    response = sendMessage (Message(Symbol.GET, Command.VERSION, Data.NIL), ser)

    if response == None:
        return False

    # check to make sure that returned version matches ours
    if (response.data == version):
        return True

    # communications have not been established
    return False