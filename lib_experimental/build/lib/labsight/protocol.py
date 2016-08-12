import serial
import serial.tools.list_ports as list
from serial.serialutil import SerialException
from threading import Thread

# How to rework this:
#     have a class that loops, repeatedly readlining, and it organizes each command into categories, and updates the motor's positions however is necessary
#     This loop must run as a background thread, fyi
#     These processes could be a part of the motor class, so that the class handles itself and it's own data
#     the send one works the way you'd expect it
#     controller.py of course initializes and oversees everything as you'd expect it to
#
#     so, i'll also be getting rid of protocol.py, it seems
#     No. I'll just being pairing it down to its bare essentials, similar to SerMon

msg_response = None

""" Symbols """
class Symbol:
    GET = "?"
    SET = "!"
    ANSWER = "$"
    STREAM = ">"
    ERROR = "@"

    """ Motor Indexing """

class MotorIndex:
    NIL = "_"
    ZERO = "0"
    ONE = "1"

""" Commands """
class Command:
    INIT = "init"
    ID = "id"
    STEP = "step"
    KILL = "kill"
    SPEED = "speed"
    VERSION = "version"
    STYLE = "style"
    HALT = "halt"

""" Data """
class Data:
    NIL = "_"
    SINGLE = "single"
    DOUBLE = "double"
    INTERLEAVE = "interleave"
    MICROSTEP = "microstep"

""" Message Structure """
class Message:
    def __init__(self, symbol, motor_index, command, data):
        self.symbol = symbol
        self.motor_index = motor_index
        self.command = command
        self.data = data

    def __repr__(self):
        return "Message({}, {}, {}, {})".format(self.symbol, self.motor, self.command, self.data)

    def __str__(self):
        return " ".join([self.symbol, self.motor, self.command, self.data])

    def __len__(self):
        return 4

def sendMessage(msg, port_path, move_func=None, callback=None):

    ser = serial.Serial(port_path)

    if callback != None:
        MessengerPigeon(msg, ser, move_func, callback).start()
        return

    def default_callback(response):
        global msg_response
        msg_response = response


    pigeon = MessengerPigeon(msg, ser, move_func, default_callback)
    pigeon.start()
    pigeon.join()

    global msg_response
    return msg_response

class MessengerPigeon(Thread):
    def __init__(self, message, ser, move_func=None, callback=None):
        Thread.__init__(self)

        self.message = message
        self.ser = ser
        self.move_func = move_func
        self.callback = callback

    def run(self):
        msg_string = "{} {} {} {}".format(self.message.symbol, self.message.motor_index, self.message.command, self.message.data)

        self.ser.write(bytes(msg_string, "ascii"))

        # read response and strip extrenous space and split it
        response = self.ser.readline().strip().decode("ascii").split(" ")

        if response == "":
            raise Exception("Received no response on this port")

        # make sure that there are 4 parts
        if len(response) != 4:
            raise Exception("Received message '{}' which is not of length 4".format(response))

        # format response array into a Message object
        response = Message(response[0], response[1], response[2], response[3])
