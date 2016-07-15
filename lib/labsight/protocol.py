import serial
import serial.tools.list_ports as list
from serial.serialutil import SerialException
from time import sleep


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

""" Data """
class Data:
    NIL = "_"

""" Message Structure """
class Message:
    def __init__(self, symbol, command, data):
        self.symbol = symbol
        self.command = command
        self.data = data

    def __repr__(self):
        return "Message({}, {}, {})".format(self.symbol, self.command, self.data)

def sendMessage(msg, ser, func=None):
    try:
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
            print("Arduino response was not proper length, but was {}".format(response))
            return None

        # format response array into a Message object
        response = Message(response[0], response[1], response[2])

        # make sure that response has the same command as initial message
        if response.command != msg.command:
            print("Arduino responded with incorrect command. {} instead of {}".format(response.command, msg.command))
            return None

        # if response opens a stream, pass the serial instance to a given function
        if response.symbol == Symbol.STREAM:
            response = [response]
            while True:
                # last_response is here because the stream response should be distinct from the final response, which is a list of the stream responses
                last_response = ser.readline().strip().decode("ascii").split(" ")

                # check if received full message or just data
                if len(last_response) == 3:
                    # format response array into a Message object
                    last_response = Message(last_response[0], last_response[1], last_response[2])

                    if (last_response.symbol == Symbol.ANSWER):
                        break
                if func != None:
                    func(last_response)
                response.append(last_response)

        return response
    except SerialException:
        print("Failed to open {}".format(port))
