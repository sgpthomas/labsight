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
        print("****Motor initialization started****")
        self.response = ""
        self.motor_index = motor_index
        self._id = ""
        self._step = 0
        self._version = None
        if config_folder == None:
            config_folder = self.createConfig()
        self.path = config_folder
        print("Config created...")
        self.ser = ser
        print("Ser set...")
        print("Motor object initialized...")
        # self.defaults = {"motor_index":self.motor_index,"port":self.ser.name,"step":self._step,"style":Data.SINGLE}

    def __repr__(self):
        return "Motor(port={}, motor_index={})".format(self.ser.name,self.motor_index) # id={}, | self.id,

# Functions used by the SerialHandler thread:
    def responseIs(self, last_response):
        self.response = last_response

    def updateStep(self, step):
        self._step = step
        # self.properties["step"] = self._step

# File and config management functions:

    def createConfig(self):
        path = os.path.expanduser(os.path.join("~", ".labsight", "motors"))
        # if configuration folder is not given, then use default
        if (not os.path.isdir(path)):
            os.makedirs(path)
        self.path = os.path.join(path, self._id)
        return self.path

    def loadProperties(self, config_path=None):
        # Load the appropriate YAML config file from the config folder
        if config_path == None:
            config_path = self.path
        archivo = io.open(config_path)
        properties = yaml.load(archivo)
        self.id = properties["id"]
        self.step = properties["step"]
        self.style = properties["style"]
        archivo.close()
        return properties

    def saveProperties(self):
        # Makes a new YAML file in the config
        if (not os.path.isdir(self.path)):
            self.createConfig()
            properties = {"id":self._id,"step":self._step,"style":self._style}
            f = io.open(self.path, "w+")
        else:
            f = io.open(self.path, "r+")
            properties = yaml.load(f)
            properties["id"] = self._id
            properties["step"] = self._step
            properties["style"] = self._style
        # try:
        #     os.remove(self.path)
        # except OSError:
        #     pass
        yaml.dump(properties, new_file, default_flow_style = False)
        f.close()

    def removeConfig(self):
        os.remove(self.path)

# Protocol function:
    def sendMessage(self, msg, func = None):
        print("Motor sending message...")
        # Allows this class to call the protocol.py function with reference to a motor
        sendMessage(msg, self.ser, func)
        # There should probably be a sleep function here...
        # This is to give the serialHandler time to receive the message
        # time.sleep(10)
        print(self.response)
        if self.response.command == "wait":
            while True:
                if self.response.command != "wait":
                    break
        # time.sleep(1)
        # if msg.command != self.response.command:
        #     raise Exception("Sent command from message '{}' does not match received command from response '{}'".format(msg, self.response))
        return self.response

    """The functions that allow you to run certain commands on the motor object:"""

    """ Getters """

    def getVersion(self):
        print("Version is being gotten...")
        msg = Message(Symbol.GET, MotorIndex.NIL, Command.VERSION, Data.NIL)
        self._version = self.sendMessage(msg)
        # self.properties["version"] = self._version
        # return self.properties["version"]

    def getID(self):
        # Get's the id from the Arduino, and updates this class' values as is appropriate
        msg = Message(Symbol.GET, self.motor_index, Command.ID, Data.NIL)
        self.id = self.sendMessage(msg).data
        # self.properties["id"] = self.id
        # return self.self.properties["id"]

    def getStep(self):
        msg = Message(Symbol.GET, self.motor_index, Command.STEP, Data.NIL)
        self._step = self.sendMessage(msg).data
        # self.properties["step"] = self._step
        # return self.properties["step"]

    def getStyle(self):
        msg = Message(Symbol.GET, self.motor_index, Command.STYLE, Data.NIL)
        self.style = self.sendMessage(msg).data
        # self.properties["style"] = self.style
        # return self.properties["style"]


    """ Setters (with no return values, because that's what getters are for. If there are no getters for a property, it means it can not be gotten) """

    def setID(self, new_id):
        msg = Message(Symbol.SET, self.motor_index, Command.ID, str(new_id))
        self.id = self.sendMessage(msg).data
        if self.id != new_id:
            raise Exception("You requested that the id be set to '{}', but the Arduino has set the id to '{}'").format(new_id, self.id)
        # self.properties["id"] = self.id
        # return self.properties["id"]

    # This is essentially a move function, as you are setting the motor's position (step) in the world
    def setStep(self, steps):
        # define function to update relative step count in dictionary
        if steps != 0:
            msg = Message(Symbol.SET, self.motor_index, Command.STEP, str(steps))
            confirm = self.sendMessage(msg)

    def kill(self):
        # This kills the motor, calling its release() function
        msg = controller.Message(Symbol.SET, self.motor_index, Command.KILL, Data.NIL)
        self.sendMessage(msg)

    def setStyle(self,new_style):
        if new_style not in [Data.SINGLE, Data.DOUBLE, Data.INTERLEAVE, Data.MICROSTEP]:
             raise Exception("Must be a valid style: single, double, interleave, or microstep")
        msg = Message(Symbol.SET, self.motor_index, Command.ID, str(new_style))
        confirmed_style = self.sendMessage(msg).data
        if new_style != confirmed_style:
            raise Exception("You requested that the style be set to '{}', but the Arduino has set the style to '{}'").format(new_style, confirmed_style)
        # self.properties["style"] = confirmed_style

        # return self.response

    def halt(self):
        msg = Message(Symbol.SET, self.motor_index, Command.HALT, Data.NIL)
        confirm = self.sendMessage(msg)
        if confirm.command != Command.HALT:
            raise Exception("You requested that the motor be halted, but the Arduino has replied with this: {}").format(confirm)
        # return self.response

# Functions for for handling the properties:

    version = property(fget=getVersion)
    id = property(getID, setID)

    step = property(getStep, setStep)

    # The below code should be made to work some day...
    # def step():
    #     doc = "The step property."
    #     def fget(self):
    #         return self.getStep()
    #     def fset(self, value):
    #         print("It works")
    #         self.setStep(value - self._step)
    #     return locals()
    #     step = property(**step())

    style = property(getStyle,setStyle)

    def port():
        doc = "The name of the port."
        def fget(self):
            return self.ser.name
        def fset(self, value):
            raise SerialException("Motor's port can not be reassigned; try making a new Motor object with your desired port")
        return locals()
    port = property(**port())


# I don't exactly understand what this is for, but I know it's used in the GUI...
    # def hasProperty(self, property_name):
        # return property_name in self.properties
