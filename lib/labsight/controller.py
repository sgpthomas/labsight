import serial
import serial.tools.list_ports as list
from serial.serialutil import SerialException
import io
import os
from time import sleep
from labsight.motor import Motor
import termios

version = "0.1"

""" Symbols """
class Symbol:    
    ASK = "?"
    COMMAND = "!"
    Answer = "$"
    OPEN_STREAM = ">"
    CLOSE_STREAM = "/"

""" Message Structure """
class Message:
    def __init__(self, symbol, command, data):
        self.symbol = symbol
        self.command = command
        self.data = data

    def __repr__(self):
        return "Message({}, {}, {})".format(self.symbol, self.command, self.data)

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

        # Disable reset after hangup
        with open(port.device) as f:
            attrs = termios.tcgetattr(f)
            attrs[2] = attrs[2] & ~termios.HUPCL
            termios.tcsetattr(f, termios.TCSAFLUSH, attrs)

        # if we can establish communications with the port, get the id and then append motor object to motors
        if (establishComms(port.device)):

            # get id from arduino
            response = sendMessage(Message(Symbol.ASK, "id", "_"), port.device)
            ID = response.data

            # create motor object and append it to the array
            motors.append(Motor(config_folder, port.device, ID))

    # return motor array
    return motors

def establishComms(port):
    # send initial message
    response = sendMessage (Message(Symbol.ASK, "version", "_"), port)

    # check to make sure that returned version matches ours
    if (response.data == version):
        return True

    # communications have not been established
    return False

def sendMessage(msg, port, func=None):
    # define delay because of serial gods looking down on us
    delay = 0.6
    try:
        # create serial port and relevant text wrapper
        ser = serial.Serial(None, timeout=2)
        ser.port = port
        ser.dsrdtr = True
        ser.open()

        # create message
        msg_string = "{} {} {}".format(msg.symbol, msg.command, msg.data)

        # ask the gods of serial about the delays
        # sleep(delay)
        ser.write(bytes(msg_string, "ascii"))
        # sleep(delay)

        # read response and strip extrenous space and split it
        response = ser.readline().strip().decode("ascii").split(" ")

        # make sure that there are 3 parts
        if len(response) != 3:
            raise Exception("Arduino response was not proper length, but was {}".format(response))

        # format response array into a Message object
        response = Message(response[0], response[1], response[2])

        # make sure that response has the same command as initial message
        if response.command != msg.command:
            raise Exception("Arduino responded with incorrect command. {} instead of {}".format(response.command, msg.command))

        # if response opens a stream, pass the serial instance to a given function
        if response.symbol == Symbol.OPEN_STREAM and func != None:
            while True:
                response = ser.readline().strip().decode("ascii").split(" ")

                # check if received full message or just data
                if len(response) == 3:
                    # format response array into a Message object
                    response = Message(response[0], response[1], response[2])

                    if (response.symbol == Symbol.CLOSE_STREAM):
                        break

                # if we reach here, pass the data to the given delegate
                func(response)

        return response
    except SerialException:
        print("Failed to open {}".format(port))

motors = getMotors()
print(motors[0])

def func(response):
    print(response)
    
sendMessage(Message(Symbol.COMMAND, "move", '100'), motors[0].port, func)
print("done")