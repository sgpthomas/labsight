import os
import io
import yaml
from labsight.protocol import Symbol, Command, Message, sendMessage

class Motor:
    def __init__(self, config_folder, serial, eyedee):
        # searches the config_folder directory for a YAML file with the name of eyedee.
        # Stores all other necessary global variables as well
        self.config_folder = config_folder
        self.serial = serial
        self.id = eyedee
        self.properties = {}
        self.filename = str(self.id) + ".yml"
        self.path = os.path.join(config_folder,self.filename)
        file_list = os.listdir(config_folder)
        if self.filename in file_list:
            self.load_properties()
        else:
            self.new_properties()

    def __repr__(self):
        return "Motor('{}', {}, {})".format(self.config_folder, self.serial, self.id)

    def load_properties(self):
        archivo = io.open(self.path)
        self.properties = yaml.load(archivo)
        archivo.close()

    def load_external(self,path):
        archivo = io.open(path)
        self.properties = yaml.load(archivo)
        archivo.close()

    def new_properties(self):
        # Makes a new YAML file in the config
        new_file = io.open(self.path, "w")
        yaml.dump({"id":self.id, "step":0}, new_file, default_flow_style = False)
        new_file.close()
        self.load_properties()

    def save_properties(self):
        # This function assumes that there is already a YAML file in the directory
        archivo = io.open(self.path, "w")
        yaml.dump(self.properties, archivo, default_flow_style = False)
        archivo.close()

    def send_message(self, msg, func = None):
        sendMessage(msg, self.serial, func)

    """The functions that allow you to run certain commands on the motor object:"""

    def getID(self):
        msg = Message(Symbol.GET, Command.ID, "_")
        return send_message(msg)

    def setID(self, new_id):
        msg = Message(Symbol.SET, Command.ID, str(new_id))
        return send_message(msg)

    def setStep(self, steps):
        move_msg = Message(Symbol.SET, Command.STEP, str(steps))
        return send_message(move_msg, self.updateDistance)

    def updateDistance(self, response):
        self.properties["step"] += distance

    def getStep(self):
        return self.properties["step"]

    def setKill():
        msg = controller.Message(Symbol.SET, Command.KILL, "_")

    def setProperty(new_property, value):
        self.properties[new_property] = value

"""
    def the rest
"""
