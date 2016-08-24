import serial
import serial.tools.list_ports as list
from serial.serialutil import SerialException
import threading

# protocol.py is the post office of the library,
# controller.py is the central government, and motor.py describes the functions and duties
# of the average citizen. I should add that to the README.md


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
        return "Message({}, {}, {}, {})".format(self.symbol, self.motor_index, self.command, self.data)

    def __str__(self):
        return " ".join([self.symbol, str(self.motor_index), self.command, str(self.data)])

    def __len__(self):
        return 4

def sendMessage(msg, ser, callback=None):
    pigeon = MessengerPigeon(msg, ser)
    pigeon.start()
    msg_string = "{} {} {} {}".format(msg.symbol, msg.motor_index, msg.command, msg.data)
    print("--> " + msg_string)
    ser.write(bytes(msg_string, "ascii"))
    return


class MessengerPigeon(threading.Thread):
    def __init__(self, message, ser, callback=None):
        threading.Thread.__init__(self)

        self.message = message
        self.ser = ser
        self.callback = callback

    def run(self):
        msg_string = "{} {} {} {}".format(self.message.symbol, self.message.motor_index, self.message.command, self.message.data)
        self.ser.write(bytes(msg_string, "ascii"))
        return

class SerialHandler(threading.Thread):
    def __init__(self, ser, motor_list, stopper, verbose=False):
        threading.Thread.__init__(self)
        self.stopper = stopper

        # Note: verbose has no function yet, and is a placeholder for future developments
        self.verbose = verbose

        self.ser = ser
        self.motor_list = motor_list

        self.wait_message = Message("$", "_", "wait", "_")

        for motor in self.motor_list:
            motor.responseIs(self.wait_message)

    def run(self):
        while not self.stopper.is_set():
            response = self.ser.readline().strip().decode("ascii").split(" ")
            if response != [""]:
                if len(response) != 4:
                    print("Received erroneous message '{}'; Not of length 4".format(response))
                else:
                    print("<-- " + " ".join(response))
                    response = Message(response[0], response[1], response[2], response[3])
                    self.filter_response(response)
        return

    def get_exit_flag(self):
        return self.exit_flag

    def filter_response(self, message):
        if message.symbol == Symbol.STREAM and message.command == Command.STEP:
            self.motor_list[int(message.motor_index)].responseIs(self.wait_message)
            self.motor_list[int(message.motor_index)].updateStep(message.data)
        elif message.symbol == Symbol.ERROR:
            self.motor_list[int(message.motor_index)].responseIs(self.wait_message)
            print("Arduino on port {} threw an error of type '{}' with data value '{}'".format(self.ser.name, message.command, message.data))
        else:
            try:
                motor_intdex = int(message.motor_index)
            except ValueError:
                self.motor_list[0].responseIs(message)
                self.motor_list[1].responseIs(message)
                return
            self.motor_list[motor_intdex].responseIs(message)
