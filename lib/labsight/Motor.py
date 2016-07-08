import os
import io
import yaml

class Motor:
    def __init__(self,config_folder, port, eyedee):
        # searches the config_folder directory for a YAML file with the name of eyedee.
        # Stores all other necessary global variables as well
        self.port = port
        self.id = eyedee
        self.properties = {}
        self.filename = str(self.id) + ".yml"
        self.path = os.path.join(config_folder,self.filename)
        file_list = os.listdir(config_folder)
        if self.filename in file_list:
            self.load_properties()
        else:
            self.new_properties()

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
        yaml.dump({"id":self.id}, new_file, default_flow_style = False)
        new_file.close()
        self.load_properties()

    def save_properties(self):
        # This function assumes that there is already a YAML file in the directory
        archivo = io.open(self.path, "w")
        yaml.dump(self.properties, archivo, default_flow_style = False)
        archivo.close()
"""
    def move

    def the rest
"""

foo = Motor(os.path.expanduser("~/Desktop/config"), "/dev/whatever", "different_id")
print(foo.path)

print(foo.properties)
