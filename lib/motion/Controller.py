import serial
import serial.tools.list_ports as list
from serial.serialutil import SerialException
import io
from time import sleep

# globals
devices = {}
ports = {}

# response
messages = {}
estCall = "? listen _"
estResponse = "$ listen yes"


def main():
    devices = findPorts()

    print(devices)

def findPorts():

    # List Available serial ports
    for port in list.comports():
        print("Found " + port.device)

        if (establishComms(port.device)):
            ID = getID(port.device)
            ports[ID] = port.device;

    # if len(ret) < 1:
    #     findPorts()

    return ports

def getID(port):
    ID = sendMessage("? id _", port).split(" ")

    if len(ID) < 3:
        confirmation = sendMessage("! id test_motor_00", port)

    return ID[2]

def establishComms(port):
    response = sendMessage("? listen _", port)

    if (response == "$ listen yes"):
        return True
        print("Communication established")

    return False

def sendMessage(msg, port):
    delay = 0.6
    try:
        ser = serial.Serial(port, timeout=1)
        sleep(delay)

        sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

        sio.write(msg)
        sleep(delay)

        sio.flush()
        response = sio.readline().strip()

        response = response.split(" ")

        if len(response) != 3:
            raise Exception("Arduino response was not proper length, but was {}".format(response))

        return response
    except SerialException:
        print("Failed to open {}".format(port))

def move(steps, port):
    command = "! move " + str(steps)
    confirmation = sendMessage(command, ports[port])
    if !(confirmation == "# move " + str(steps))
        raise SerialException("The motor has not confirmed its movement, and it may have not moved")
    return confirmation
def kill(port):
    command = "! kill _"
    confirmation = sendMessage(command, ports[port])
    if confirmation != "# kill _":
        raise SerialException("The motor has not confirmed the action, and may have not been killed")
    return confirmation



main()
