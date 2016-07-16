import os
import io
import yaml
from labsight.protocol import Symbol, Command, Message, sendMessage

class Motor(object):

    def __init__(self, config_folder, serial, id):
        # Searches the config_folder directory for a YAML file called the motor's id.
        # Stores all other necessary global variables as well
        # If there is no config file, a new one is created
        self.config_folder = config_folder
        self.serial = serial
        self.id = id
        self.properties = {}
        self.filename = str(self.id) + ".yml"
        self.path = os.path.join(config_folder, self.filename)
        self.defaults = {"id":self.id, "step":0}
        file_list = os.listdir(config_folder)
        if self.filename in file_list:
            self.loadProperties()
        else:
            self.newProperties()

    def __repr__(self):
        return "Motor(id={}, port={})".format(self.id, self.serial.port)

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
            return sendMessage(msg, self.serial, func)
        else:
            raise SerialException("Serial for Motor '{}' is not open. Open it before sending a message.".format(self.id))
            return None

    """The functions that allow you to run certain commands on the motor object:"""

    def getID(self):
        # Get's the id from the Arduino, and updates this class' values as is appropriate
        msg = Message(Symbol.GET, Command.ID, "_")
        self.id = self.sendMessage(msg).data
        self.properties["id"] = self.id
        return self.sendMessage(msg)

    def setID(self, new_id):
        msg = Message(Symbol.SET, Command.ID, str(new_id))
        self.id = new_id
        self.properties["id"] = new_id
        return self.sendMessage(msg)

    def setStep(self, steps):
        # This is essentially a move function, as you are setting the motor's position (step) in the world
        # Line on updating kill may be wrong, it depends on how the Arduino handles its release() function
        move_msg = Message(Symbol.SET, Command.STEP, str(steps))
        confirm = self.sendMessage(move_msg, self.updateDistance)
        # self.getKill()
        return confirm
    def updateDistance(self, response):
        # This function allows for realtime receiving and updating of the traveled
        self.properties["step"] += int(response.data)
        print(self.properties["step"])

    def getStep(self):
        # Tells you the current position
        return self.properties["step"]

    def setKill(self):
        # This kills the motor, calling its release() function
        msg = controller.Message(Symbol.SET, Command.KILL, "_")
        ret = self.sendMessage(msg)
        self.getKill

    # def getKill(self):
    #     # Updates this object's kill property according to what the Arduino tells it
    #     get_kill_msg = Message(Symbol.GET, Command.KILL, "_")
    #     kill_status = self.sendMessage(get_kill_msg).data
    #     self.properties["kill"] = kill_status
    #     return self.properties["kill"]

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
