import serial
import serial.tools.list_ports as list
from serial.serialutil import SerialException

import os
from time import sleep
import threading

from labsight.motor import Motor
from labsight.protocol import Symbol, MotorIndex, Command, Data, Message, sendMessage

lib_version = "0.8"

# These are outside of a function so that they are accessible to every function here, as they needs to be
motor_objects = {}
motor_serials = {}

# initialize the container for the serialHandlers
threads = {}

""" Talks to available ports and creates motor object if it finds anything """
def start():
    # initialize return array

    # search through available ports
    for i in range(len(list.comports())):
        port = list.comports()[i]

            # sleep for some time to give the arduino time to reset
            # sleep(2)

            # if we can establish communications with the port, get the id and then append motor object to motors
        if somethingConnected(port.device):
            motor_objects[port.device] = []
            for motor_index in range(2):
                motor_objects[port.device].append(Motor(port.device, motor_index)) #

            threads[port.device] = serialHandler(port.device, motor_objects[port.device])
            arduino_version = motor_objects[port.device][motor_index].getVersion()
            if arduino_version != lib_version:
                del motor_objects[port.device]
            motor_objects[port.device][motor_index].getID()

    # return motor dictionary
    return motor_objects

class serialHandler(threading.Thread):
    def __init__(self, port_name, motor_list, verbose=False):
        threading.Thread.__init__(self)


        self.exit_flag = threading.Event()
        self.port_name = port_name
        try:
            self.ser = serial.Serial(port_name, timeout=2)
        except SerialException:
            print("Unable to open '{}'. This port is probably already open.").format(port_name)
            self.exit()

        self.verbose = verbose
        self.motor_list = motor_list

    def run(self):
        while True:
            response = self.serial.readline().strip().decode("ascii").split(" ")
            if len(response) != 4:
                print("Received erroneous message '{}'; Not of length 4")
            else:
                response = Message(response[0], response[1], response[2], response[3])
                self.filter_response(response)
            if exit.is_set():
                self.ser.close()
                return

        def getExitFlag(self):
            return self.exit_flag

    def filter_response(self, message):
        if message.Symbol == Symbol.STREAM and message.Command == Command.STEP:
            self.motor_list[int(message.MotorIndex)].updateStep(message.Data)
        elif message.Symbol == Symbol.ERROR:
            print("Arduino on port {} threw an error of type '{}' with data value '{}'").format(port_name, message.Command, message.Data)
        else:
            self.motor_list[message.MotorIndex].lastResponseIs(response)

def somethingConnected(port_device):
    if sendMessage (Message(Symbol.GET, MotorIndex.NIL, Command.VERSION, Data.NIL), port_device) != "":
        return True
    else:
        return False




def exit():
    for thread in threads.items():
        thread.getExitFlag.set()
    threads = {}
    motor_serials = {}

def motors(reset=False):
    if len(motor_objects) == 0 or reset:
        start()
    return motor_objects

def serials():
    if len(motor_serials) == 0:
        start()
    return motor_serials






# def establishComms(ser):
#     # send initial message
#     try:
#         response = sendMessage (Message(Symbol.GET, Motor.NIL, Command.VERSION, Data.NIL), ser)
#         print(response)
#     except:
#         print("no response")
#         return False
#
#     if response == None:
#         print("no response")
#         return False
#
#     # check to make sure that returned lib_version matches ours
#     if (response.data != lib_version):
#         print("Arduino is version {} instead of version {}".format(response.data, lib_version))
#         return False
#     # communications have been established
#     return True
