import serial
import serial.tools.list_ports as list
from serial.serialutil import SerialException

import os
import threading
import sys
import signal
import atexit

from labsight.motor import Motor
from labsight.protocol import Symbol, MotorIndex, Command, Data, Message, sendMessage, SerialHandler

# This is the main

lib_version = "0.8"

# These are outside of a function so that they are accessible to every function here, as they needs to be
motor_objects = {}
motor_serials = {}

# initialize the container for the serialHandlers
threads = {}
stopper = threading.Event()
""" Talks to available ports and creates motor object if it finds anything """
def start():
    # search through available ports
    for i in range(len(list.comports())):
        port = list.comports()[i]

        # From this serial initialization, every other use of the serial comes forth
        ser = serial.Serial(port.device, timeout=2)
        motor_serials[port.device] = ser

        if somethingConnected(ser):
            motor_serials[port.device] = ser

            motor_objects[port.device] = []
            for motor_index in range(2):
                motor_object = Motor(port.device, motor_index, ser)
                motor_objects[port.device].append(motor_object)
            threads[port.device] = SerialHandler(ser, motor_objects[port.device], stopper)

        else:
            del motor_serials[port.device]


    handler = SignalHandler(stopper, threads)
    signal.signal(signal.SIGINT, handler)

    for port_device, thread in threads.items():
        thread.start()

        for motor_object in motor_objects[port_device]:
            arduino_version = motor_object.getVersion()
            if arduino_version != lib_version:
                del motor_object
                continue
            else:
                motor_object.getID()
                print("id gotten?")

    # return motor dictionary
    return motor_objects


def somethingConnected(ser):
    sendMessage (Message(Symbol.GET, MotorIndex.NIL, Command.VERSION, Data.NIL), ser)
    response = ser.readline().strip().decode("ascii")
    if response != "":
        return True
    else:
        return False

def test():
    print("testing")

def end():
    print("ending this!")
    stopper.set()
    return None

atexit.register(end)

class SignalHandler:
    stopper = None
    workers = None

    def __init__(self, stopper, workers):
        self.stopper = stopper
        self.workers = workers

    def __call__(self, signum, frame):
        self.stopper.set()

        for port, worker in self.workers.items():
            worker.join()

        sys.exit(0)

def motors(reset=False):
    if len(motor_objects) == 0 or reset:
        start()
    return motor_objects

def serials():
    if len(motor_serials) == 0:
        start()
    return motor_serials
