import serial
import serial.tools.list_ports as list
from serial.serialutil import SerialException
import os
from time import sleep
from labsight.motor import Motor
from labsight.protocol import Symbol, Command, Message, sendMessage

version = "0.1"

""" Talks to available ports and creates motor object if it finds anything """
def getMotors (config_folder = ""):
    # initialize return array
    motors = []

    # if configuration folder is not given, then use default
    if (config_folder == ""):
        config_folder = os.path.expanduser(os.path.join("~", ".labsight", "motors"))
        if (not os.path.isdir(config_folder)):
            print("Default config folder doesn't exist. Generating a new one.")
            os.makedirs(config_folder)

    # print config directory
    print("Using config directory: {}".format(config_folder))

    # search through available ports
    for port in list.comports():
        print("Found " + port.device)

        ser = serial.Serial(port.device, timeout=2)
        sleep(0.6)

        # if we can establish communications with the port, get the id and then append motor object to motors
        if (establishComms(ser)):

            # get id from arduino
            response = sendMessage(Message(Symbol.GET, "id", "_"), ser)
            ID = response.data

            # create motor object and append it to the array
            motors.append(Motor(config_folder, ser, ID))

    # return motor array
    return motors

def establishComms(port):
    # send initial message
    response = sendMessage (Message(Symbol.GET, "version", "_"), port)

    if response == None:
        return False

    # check to make sure that returned version matches ours
    if (response.data == version):
        return True

    # communications have not been established
    return False

"""Testing"""

motors = getMotors()
print(motors)

def func(response):
    print(response)

motors[0].send_message(Message(Symbol.SET, Command.STEP, "100"), func)

print("done")
