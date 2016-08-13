import os
import io
import yaml
import time

import serial

from labsight.protocol import Symbol, MotorIndex, Command, Data, Message, sendMessage

class Motor(object):
    def __init__(self, port_name, motor_index, ser, config_folder=None):
        # Searches the config_folder directory for a YAML file called the motor's id.
        # Stores all other necessary global variables as well
        # If there is no config file, a new one is created
        # self.response = ""
        self.motor_index = motor_index
        if config_folder == None:
            config_folder = self.createConfig()
        self.config_folder = config_folder
        self.ser = ser
        self.step = 0

        self.properties = {}
        self.defaults = {"motor_index":self.motor_index,"port":self.ser.name,"step":self.step,"style":Data.SINGLE}

    def __repr__(self):
        return "Motor(port={}, motor_index={})".format(self.ser.name,self.motor_index) # id={}, | self.id,

# Functions used by the SerialHandler thread:
    def responseIs(self, last_response):
        print("Response is:")
        self.response = last_response
        print(self.response)
        print(type(self.response))

    def updateStep(self, step):
        self.step = step
        self.properties["step"] = self.step

# File and config management functions:

    def createConfig(self):
        path = os.path.expanduser(os.path.join("~", ".labsight", "motors"))

        # if configuration folder is not given, then use default
        if (not os.path.isdir(path)):
            # print("Config Directory doesn't exist. Generating a new one.")
            os.makedirs(path)

        return path

    def loadProperties(self):
        # Load the appropriate YAML config file from the config folder
        archivo = io.open(self.path)
        self.properties = yaml.load(archivo)
        archivo.close()

    def loadExternal(self, path):
        # Load a config file from any given folder
        archivo = io.open(path)
        self.properties = yaml.load(archivo)
        archivo.close()

    def newProperties(self):
        # Makes a new YAML file in the config
        try:
            os.remove(self.path)
        except OSError:
            pass
        new_file = io.open(self.path, "w")
        yaml.dump(self.defaults, new_file, default_flow_style = False)
        new_file.close()
        self.loadProperties()

    def saveProperties(self):
        # This function assumes that there is already a YAML file in the directory
        archivo = io.open(self.path, "w")
        yaml.dump(self.properties, archivo, default_flow_style = False)
        archivo.close()

    def removeConfig(self):
        os.remove(self.path)

# Protocol function:
    def sendMessage(self, msg, func = None):
        # Allows this class to call the protocol.py function with reference to a motor
        sendMessage(msg, self.ser, func)
        # There should probably be a sleep function here...
        # This is to give the serialHandler time to receive the message
        return self.receiveResponse(msg)

    def receiveResponse(self,msg):
        time.sleep(10)
        print("The world according to sendMessage:")
        print("index: " + str(self.motor_index))
        print(msg)
        print(self.response)
        if msg.command != self.response.command:
            raise Exception("Sent command from message '{}' does not match received command from response '{}'".format(msg.command, self.response.command))
        return self.response

    """The functions that allow you to run certain commands on the motor object:"""

    """ Getters """

    def getVersion(self):
        msg = Message(Symbol.GET, MotorIndex.NIL, Command.VERSION, Data.NIL)
        self.version = self.sendMessage(msg)
        self.properties["version"] = self.version
        print("Version Gotten!")
        return self.properties["version"]

    def getID(self):
        # Get's the id from the Arduino, and updates this class' values as is appropriate
        msg = Message(Symbol.GET, self.motor_index, Command.ID, Data.NIL)
        self.id = self.sendMessage(msg).data
        self.properties["id"] = self.id
        return self.self.properties["id"]

    def getStep(self):
        msg = Message(Symbol.GET, self.motor_index, Command.STEP, Data.NIL)
        self.step = self.sendMessage(msg).data
        self.properties["step"] = self.step
        return self.properties["step"]

    def getStyle(self):
        msg = Message(Symbol.GET, self.motor_index, Command.STYLE, Data.NIL)
        self.style = self.sendMessage(msg).data
        self.properties["style"] = self.style
        return self.properties["style"]


    """ Setters (with no return values, because that's what getters are for. If there are no getters for a property, it means it can not be gotten) """

    def setID(self, new_id):
        msg = Message(Symbol.SET, self.motor_index, Command.ID, str(new_id))
        self.id = self.sendMessage(msg).data
        if self.id != new_id:
            raise Exception("You requested that the id be set to '{}', but the Arduino has set the id to '{}'").format(new_id, self.id)
        self.properties["id"] = self.id
        # return self.properties["id"]

    # This is essentially a move function, as you are setting the motor's position (step) in the world
    def setStep(self, steps):
        # define function to update relative step count in dictionary

        msg = Message(Symbol.SET, self.motor_index, Command.STEP, str(steps))
        confirm = self.sendMessage(msg)

        # update step count after moving
        # self.saveProperties()

        # return self.properties["step"]

    def setKill(self):
        # This kills the motor, calling its release() function
        msg = controller.Message(Symbol.SET, self.motor_index, Command.KILL, Data.NIL)
        self.sendMessage(msg)
        # return self.response

    def setStyle(self,new_style):
        if new_style not in [Data.SINGLE, Data.DOUBLE, Data.INTERLEAVE, Data.MICROSTEP]:
             raise Exception("Must be a valid style: single, double, interleave, or microstep")
        msg = Message(Symbol.SET, self.motor_index, Command.ID, str(new_style))
        confirmed_style = self.sendMessage(msg).data
        if new_style != confirmed_style:
            raise Exception("You requested that the style be set to '{}', but the Arduino has set the style to '{}'").format(new_style, confirmed_style)
        self.properties["style"] = confirmed_style

        # return self.response

    def setHalt(self):
        msg = Message(Symbol.SET, self.motor_index, Command.HALT, Data.NIL)
        confirm = self.sendMessage(msg)
        if confirm.command != Command.HALT:
            raise Exception("You requested that the motor be halted, but the Arduino has replied with this: {}").format(confirm)
        # return self.response

# Property utility functions:

    def getProperty(self, property_name):
        # make sure that our local dictionary is up-to-date with the config file
        self.loadProperties()
        value = None

        try:
            value = self.properties[property_name]
        except KeyError:
            print("Property '%s' does not exist!" % property_name)
        return value

    def setProperty(self, property_name, value):
        # allows something like the GUI to store it's own data in the YAML file
        self.properties[property_name] = value
        self.saveProperties()

# I don't exactly understand what this is for, but I know it' used in the GUI...
    def hasProperty(self, property_name):
        return property_name in self.properties
