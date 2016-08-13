import serial
import serial.tools.list_ports as list
from serial.serialutil import SerialException

import os
from time import sleep
import threading

from labsight.motor import Motor
from labsight.protocol import Symbol, MotorIndex, Command, Data, Message, sendMessage, SerialHandler

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

        # From this serial initialization, every other use of the serial comes forth
        ser = serial.Serial(port.device, timeout=2)
        motor_serials[port.device] = ser

        if somethingConnected(ser):
            motor_serials[port.device] = ser

            motor_objects[port.device] = []
            for motor_index in range(2):
                motor_object = Motor(port.device, motor_index, ser)
                motor_objects[port.device].append(motor_object)

            threads[port.device] = SerialHandler(ser, motor_objects[port.device])
            threads[port.device].start()
            for motor_object in motor_objects[port.device]:
                arduino_version = motor_object.getVersion()
                if arduino_version != lib_version:
                    del motor_object
                    continue
                else:
                    motor_object.getID()
                    print("id gotten?")

        else:
            del motor_serials[port.device]
    # return motor dictionary
    return motor_objects


def somethingConnected(ser):
    sendMessage (Message(Symbol.GET, MotorIndex.NIL, Command.VERSION, Data.NIL), ser)
    response = ser.readline().strip().decode("ascii")
    if response != "":
        return True
    else:
        return False




def exit():
    for thread in threads.items():
        thread.get_exit_flag.set()
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
