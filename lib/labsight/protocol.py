import serial
import serial.tools.list_ports as list
from serial.serialutil import SerialException
import threading

# The only thing left to do now is change how serials are handled. There can not be so many objects open at once
# They must all (all 2 of them max on my computer) come from controller.py or protocol.py (probably the former)
# , and be handed to whatever needs them. Also, serialHandler should probably go in protocol.py,
# and be renamed to serialReceiver. Protocol.py at this point is largely just becoming a reference file
# for the protocol, as well as containig serialReceiver. protocol.py is the post office of the library,
# let's put it that way. controller.py is the central government, and motor.py describes the functions and duties
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
        return "Message({}, {}, {}, {})".format(self.symbol, self.motor_index, self.command, self.data)

    def __str__(self):
        return " ".join([self.symbol, str(self.motor_index), self.command, str(self.data)])

    def __len__(self):
        return 4

def sendMessage(msg, ser, callback=None):

    # if callback != None:
    #     MessengerPigeon(msg, ser, callback).start()
    #     return

    # def default_callback(response):
    #     global msg_response
    #     msg_response = response


    # pigeon = MessengerPigeon(msg, ser, default_callback)
    # pigeon.start()
    # pigeon.join()

    # global msg_response

    msg_string = "{} {} {} {}".format(msg.symbol, msg.motor_index, msg.command, msg.data)
    ser.write(bytes(msg_string, "ascii"))

    # return msg_response

class MessengerPigeon(threading.Thread):
    def __init__(self, message, ser, callback=None):
        threading.Thread.__init__(self)

        self.message = message
        self.ser = ser
        self.callback = callback

    def run(self):
        msg_string = "{} {} {} {}".format(self.message.symbol, self.message.motor_index, self.message.command, self.message.data)

        self.ser.write(bytes(msg_string, "ascii"))

        """"""

        # read response and strip extrenous space and split it
        # response = self.ser.readline().strip().decode("ascii").split(" ")

        # if response == [""]:
        #     raise Exception("Received no response on this port")

        # make sure that there are 4 parts
        # if len(response) != 4:
        #     raise Exception("Received message '{}' from port {}, which is not of length 4".format(response, self.ser.name))

        # format response array into a Message object
        # response = Message(response[0], response[1], response[2], response[3])

class SerialHandler(threading.Thread):
    def __init__(self, ser, motor_list, stopper, verbose=False):
        threading.Thread.__init__(self)
        self.stopper = stopper

        # Note: verbose has no function yet, and is a placeholder for future developments
        self.verbose = verbose

        self.ser = ser
        self.motor_list = motor_list

        self.wait_message = Message("$", "_", "wait", "_")

        print("SerialHandler's Motor list:")
        print(self.motor_list)
        for motor in self.motor_list:
            motor.responseIs(self.wait_message)

    def run(self):
        print("Thread running")
        while not self.stopper.is_set():
            response = self.ser.readline().strip().decode("ascii").split(" ")
            if response != [""]:
                if len(response) != 4:
                    raise Exception("Received erroneous message '{}'; Not of length 4".format(response))
                else:
                    print(response)
                    response = Message(response[0], response[1], response[2], response[3])
                    print("response now")
                    print(response)
                    self.filter_response(response)
            # if self.exit_flag.is_set():
            #     print("exit flag set!")
            #     self.ser.close()
            #     break
        print("exitting?")
        return

    def get_exit_flag(self):
        return self.exit_flag

    def filter_response(self, message):
        print("Filtering:")
        print(message)
        if message.symbol == Symbol.STREAM and message.command == Command.STEP:
            self.motor_list[int(message.motor_index)].responseIs(self.wait_message)
            self.motor_list[int(message.motor_index)].updateStep(message.data)
        elif message.symbol == Symbol.ERROR:
            self.motor_list[int(message.motor_index)].responseIs(self.wait_message)
            print("Arduino on port {} threw an error of type '{}' with data value '{}'".format(self.ser.name, message.command, message.data))
        else:
            try:
                motor_intdex = int(message.motor_index)
                print(motor_intdex)
            except ValueError:
                self.motor_list[0].responseIs(message)
                self.motor_list[1].responseIs(message)
                return
            self.motor_list[motor_intdex].responseIs(message)
