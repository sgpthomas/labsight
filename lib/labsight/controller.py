import serial
import serial.tools.list_ports as list
from serial.serialutil import SerialException
import os
from time import sleep
from labsight.motor import Motor
from labsight.protocol import Symbol, Motor, Command, Data, Message, sendMessage

lib_version = "0.6"

# This is outside of a function so that it is accessible to every function here, as it needs to be
motor_objects = {}

""" Talks to available ports and creates motor object if it finds anything """
def getAttachedSerials(config_folder):
    # initialize return array
    motor_serials = {}

    # createDefaultConfigDirectory()
    # print config directory
    # print("Using config directory: {}".format(config_folder))

    # search through available ports
    for port in list.comports():
        # print("Found " + port.device)

        # try to connect to serial
        try:
            ser = serial.Serial(port.device, timeout=2)

            # sleep for some time to give the arduino time to reset
            sleep(2)

            # if we can establish communications with the port, get the id and then append motor object to motors
            if (establishComms(ser)):
                for i in range(2):
                    # get id from arduino
                    response = sendMessage(Message(Symbol.GET, str(i), Command.ID, Data.NIL), ser)
                    mid = response.data

                    # create motor object and append it to the array
                    motor_objects[mid] = (Motor(config_folder, str(i), ser, mid))

                    # create new motor object so that a new config folder is generated if needs
                    motor_serials[mid] = ser

        except SerialException:
            print("Unable to open '{}'. This port is probably already open.")

    # return motor dictionary
    return motor_serials

def motors(config = "", reset=False):
    if config == "":
        config = createDefaultConfigDirectory()
    if len(motor_objects) > 0 and not reset:
        return motor_objects
    getAttachedSerials(config)
    return motor_objects

def createDefaultConfigDirectory():
    path = os.path.expanduser(os.path.join("~", ".labsight", "motors"))

    # if configuration folder is not given, then use default
    if (not os.path.isdir(path)):
        # print("Config Directory doesn't exist. Generating a new one.")
        os.makedirs(path)

    return path

def establishComms(ser):
    # send initial message
    try:
        response = sendMessage (Message(Symbol.GET, Motor.NIL, Command.VERSION, Data.NIL), ser)
    except:
        print("no response")
        return False

    if response == None:
        print("no response")
        return False

    # check to make sure that returned lib_version matches ours
    if (response.data != lib_version):
        print("Arduino is version {} instead of version {}".format(response.data, lib_version))
        return False

    # communications have been established
    return True
