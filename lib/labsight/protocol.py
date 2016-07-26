import serial
import serial.tools.list_ports as list
from serial.serialutil import SerialException
from threading import Thread

msg_response = None

""" Symbols """
class Symbol:
    GET = "?"
    SET = "!"
    ANSWER = "$"
    STREAM = ">"
    ERROR = "@"

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
    def __init__(self, symbol, command, data):
        self.symbol = symbol
        self.command = command
        self.data = data

    def __repr__(self):
        return "Message({}, {}, {})".format(self.symbol, self.command, self.data)

    def __str__(self):
        return " ".join([self.symbol,self.command,self.data])

def sendMessage(msg, ser, move_func=None, callback=None):
    if callback != None:
        MessengerPigeon(msg, ser, move_func, callback).start()
        return

    # else callback == None
    def default_callback(response):
        global msg_response
        msg_response = response

    pigeon = MessengerPigeon(msg, ser, move_func, default_callback)
    pigeon.start()
    pigeon.join()
    
    global msg_response
    return msg_response

class MessengerPigeon(Thread):
    def __init__(self, message, serial, move_func=None, callback=None):
        Thread.__init__(self)

        self.message = message
        self.serial = serial
        self.move_func = move_func
        self.callback = callback

    def run(self):
        msg_string = "{} {} {}".format(self.message.symbol, self.message.command, self.message.data)

        self.serial.write(bytes(msg_string, "ascii"))

        # read response and strip extrenous space and split it
        response = self.serial.readline().strip().decode("ascii").split(" ")

        # make sure that there are 3 parts
        if len(response) != 3:
            raise Exception("Received message '{}' which is not of length 3".format(response))

        # format response array into a Message object
        response = Message(response[0], response[1], response[2])

        # make sure that response has the same command as initial message
        if response.command != self.message.command:
            raise Exception("Arduino responded with incorrect command. {} instead of {}".format(response.command, self.message.command))

        if response.symbol == Symbol.ERROR:
            raise Exception("The Arduino sent the error {}".format(response))

        # if response opens a stream, pass the serial instance to a given function
        if response.symbol == Symbol.STREAM:
            response = [response]
            while True:
                # last_response is here because the stream response should be distinct from the final response, which is a list of the stream responses
                last_response = self.serial.readline().strip().decode("ascii").split(" ")

                # check if received full message or just data
                if len(last_response) == 3:
                    # format response array into a Message object
                    last_response = Message(last_response[0], last_response[1], last_response[2])

                    if (last_response.symbol == Symbol.ANSWER):
                        break
                if self.move_func != None:
                    self.move_func(last_response)
                # response.append(last_response)
            response = last_response
        
        # give response to the callback function
        if self.callback != None:
            self.callback(response)