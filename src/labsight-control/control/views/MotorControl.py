
# imports
from gi.repository import Gtk

# motor control class
class MotorControl(Gtk.Grid):
    # constructor
    def __init__(self, motor = None):
        Gtk.Grid.__init__(self)

        # globalize motor
        self.motor = motor

        # build_ui
        self.update_ui()

        # connect signals
        self.connect_signals()

        # show all
        self.show_all()

    def update_ui(self):
        if self.motor != None:
            label = Gtk.Label(self.motor.getProperty("display-name"))

            self.attach(label, 0, 0, 1, 1)

    def connect_signals(self):
        print("connect signals")