import os
import io
import yaml

import serial

from labsight.protocol import Symbol, MotorIndex, Command, Data, Message, sendMessage

class Motor(object):
    def __init__(self, port_name, motor_index, config_folder=None):
        # Searches the config_folder directory for a YAML file called the motor's id.
        # Stores all other necessary global variables as well
        # If there is no config file, a new one is created
        self.response = ""
        self.motor_index = motor_index
        if config_folder == None:
            config_folder = self.createConfig()
        self.config_folder = config_folder
        self.port_name = port_name
        self.serial = serial.Serial(self.port_name)
        self.id = id
        self.properties = {}
        filename = str(self.id) + ".yml"
        self.path = os.path.join(config_folder, filename)
        self.defaults = {"id":self.id,"port":self.port_name,"motor_index":self.motor_index,"step":0,"style":Data.SINGLE}
        file_list = os.listdir(config_folder)
        if filename in file_list:
            self.loadProperties()
        else:
            self.newProperties()

    def __repr__(self):
        return "Motor(id={}, port={}, motor_port={})".format(self.id, self.port_name,self.motor_port)


    def createConfig(self):
        path = os.path.expanduser(os.path.join("~", ".labsight", "motors"))

        # if configuration folder is not given, then use default
        if (not os.path.isdir(path)):
            # print("Config Directory doesn't exist. Generating a new one.")
            os.makedirs(path)

        return path



    def responseIs(self, last_response):
        self.response = last_response

    def updateStep(self, step):
        self.step = step

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
        # print("No config file found. Generating a new one.")
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

    def sendMessage(self, msg, func = None):
        # Allows this class to call the protocol.py function with reference to a motor
        # Also, automatically adds the motor's appropriate serial object
        if self.serial != None:
            sendMessage(msg, self.port_name, func)
            return self.response
        else:
            raise SerialException("Serial for Motor '{}' is not open. Open it before sending a message.".format(self.id))
            return None

    """The functions that allow you to run certain commands on the motor object:"""

    def getVersion(self):
        msg = Message(Symbol.GET, MotorIndex.NIL, Command.VERSION, Data.NIL)
        self.sendMessage(msg)
        self.version = self.response
        self.properties["version"] = self.version
        return self.properties["version"]

    def getID(self):
        # Get's the id from the Arduino, and updates this class' values as is appropriate
        msg = Message(Symbol.GET, self.motor_port, Command.ID, Data.NIL)
        self.sendMessage(msg)
        self.id = self.response.data
        self.properties["id"] = self.id
        return self.response

    def setID(self, new_id):
        msg = Message(Symbol.SET, self.motor_port, Command.ID, str(new_id))
        self.sendMessage(msg)
        self.id = self.response.data
        self.properties["id"] = self.id
        return self.properties["id"]

    # This is essentially a move function, as you are setting the motor's position (step) in the world
    # Line on updating kill may be wrong, it depends on how the Arduino handles its release() function
    def setStep(self, steps, function = None):
        # define function to update relative step count in dictionary

        move_msg = Message(Symbol.SET, self.motor_port, Command.STEP, str(steps))
        confirm = self.sendMessage(move_msg, function)
        confirm = self.response

        # update step count after moving
        self.properties["step"] += int(confirm.data)
        self.saveProperties()

        return self.properties["step"]

    def getStep(self):
        # Tells you the current position
        return self.properties["step"]

    def setKill(self):
        # This kills the motor, calling its release() function
        msg = controller.Message(Symbol.SET, self.motor_port, Command.KILL, Data.NIL)
        self.sendMessage(msg)
        # self.getKill
        return self.response

    # def getKill(self):
    #     # Updates this object's kill property according to what the Arduino tells it
    #     get_kill_msg = Message(Symbol.GET, Command.KILL, "_")
    #     kill_status = self.sendMessage(get_kill_msg).data
    #     self.properties["kill"] = Kill_status
    #     return self.properties["kill"]

    def setStyle(self,style):
        new_style
        if style not in [Data.SINGLE, Data.DOUBLE, Data.INTERLEAVE, Data.MICROSTEP]:
             raise Excpetion("Must be a valid style: single, double, interleave, or microstep")
        msg = Message(Symbol.SET, self.motor_port, Command.ID, str(new_style))
        self.properties["style"] = style
        self.sendMessage(msg)
        return self.response

    def getStyle(self,style):
        return self.properties["style"]

    def setHalt(self):
        msg = Message(Symbol.SET, self.motor_port, Command.HALT, Data.NIL)
        self.sendMessage(msg)
        return self.response

    def setProperty(self, property_name, value):
        # allows something like the GUI to store it's own data in the YAML file
        self.properties[property_name] = value
        self.saveProperties()

    def getProperty(self, property_name):
        # make sure that our local dictionary is up-to-date with the config file
        self.loadProperties()
        value = None

        try:
            value = self.properties[property_name]
        except KeyError:
            print("Property '%s' does not exist!" % property_name)

        return value

    def hasProperty(self, property_name):
        return property_name in self.properties

    def remove(self):
        os.remove(self.path)
