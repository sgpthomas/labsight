
# imports
from gi.repository import Gtk, GObject
from labsight.motor import Motor
from labsight import controller
from control.views.NewMotorDialog import NewMotorDialog
import control.config as config
import os
from threading import Thread
import queue

# Motor List Class
class MotorList(Gtk.Box):

    # stack
    stack = None

    # widgets
    list_box = None

    scrolled_window = None

    motors = {}

    serial_worker = None
    serial_queue = None

    # setup signals
    __gsignals__ = {
        "done-loading": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),
        "control-motor": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,))
    }

    # constructor
    def __init__(self):
        # initiate grid
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        # create stack
        self.stack = Gtk.Stack()

        # create spinner
        grid = Gtk.Grid()
        grid.props.expand = True
        grid.props.halign = Gtk.Align.CENTER
        grid.props.valign = Gtk.Align.CENTER
        self.spinner = Gtk.Spinner()
        self.spinner.set_size_request(32, 32)
        grid.attach(self.spinner, 0, 0, 1, 1)
        label = Gtk.Label("Scanning Ports for Connected Motors")
        label.get_style_context().add_class("new-motor-title")
        grid.attach(label, 0, 1, 1, 1)
        # self.stack.add_named(grid, "loading")

        # create list box
        self.create_list_box()

        # add to scrolled window
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.add(self.list_box)

        self.stack.add_named(self.scrolled_window, "list")

        # add to this
        self.add(self.stack)

        self.show_all()

    def create_list_box(self):
        self.list_box = Gtk.ListBox()
        self.list_box.props.expand = True
        self.list_box.props.selection_mode = Gtk.SelectionMode.NONE

        # add css class to this for styling
        self.list_box.get_style_context().add_class("motor-list")

    def load_from_files(self):
        file_list = os.listdir(config.MOTOR_CONFIG_DIR)
        for f in file_list:
            (mid, ext) = f.split(".")
            if ext == "yml" or ext == "yaml":
                m = Motor(config.MOTOR_CONFIG_DIR, None, mid)

                motor_list_child = MotorListChild(m)
                def f(motor):
                    self.emit("control-motor", motor)
                motor_list_child.control_callback = f

                self.motors[mid] = motor_list_child
                self.list_box.insert(motor_list_child, -1)

    def start_load(self):

        self.load_from_files()

        if self.serial_worker != None:
            print("waiting for serial worker to end")
            self.serial_worker.join()

        self.serial_queue = queue.Queue()
        self.serial_worker = SerialWorker(self.serial_queue, self.end_load)
        self.serial_worker.start()

        while self.serial_queue != None:

            if not self.serial_queue:
                print("hi")
                task = self.serial_queue.get()
                task()

            if Gtk.events_pending():
                Gtk.main_iteration()

    def end_load(self, result):

        for mid in result:
            if mid in self.motors:
                self.motors[mid].connect_serial(result[mid])
            else:
                self.load_from_files()
                self.end_load(result)

        self.serial_queue = None
        self.emit("done-loading")

class SerialWorker(Thread):
    # construct self
    def __init__(self, ser_queue, callback):
        Thread.__init__(self)

        self.callback = callback
        self.queue = ser_queue

    def run(self):
        serials = controller.getAttachedSerials(config.MOTOR_CONFIG_DIR)

        self.queue.put(lambda: self.callback(serials))

class MotorListChild(Gtk.ListBoxRow):

    # grid for this
    grid = None

    # motor id
    motor = None

    # widgets
    motor_detected_label = None

    # status 0 = disconnected, 1 = connecting, 2 = connected
    status = 0

    # constructor
    def __init__(self, motor):
        Gtk.ListBoxRow.__init__(self)

        # make motor available throughout the class
        self.motor = motor

        # set motor properties
        if not self.motor.hasProperty("configured"):
            self.motor.setProperty("configured", False)

        # if motor is not already configured, make sure all of our properties exist
        if self.motor.getProperty("configured") == False:
            self.motor.setProperty("display-name", "Motor")
            self.motor.setProperty("axis", None)
            self.motor.setProperty("type", None)

        self.control_callback = None

        # build ui
        self.update_ui()

    def clean_ui(self):
        for child in self.get_children():
            child.destroy()

    def update_ui(self):
        # add class to self
        self.get_style_context().add_class("card")
        self.props.margin = 6

        # box
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        # create info grid
        info_grid = Gtk.Grid()
        info_grid.props.expand = True
        info_grid.props.halign = Gtk.Align.START
        info_grid.props.valign = Gtk.Align.CENTER
        info_grid.props.column_spacing = 6
        info_grid.props.row_spacing = 3

        # create button grid
        button_grid = Gtk.Grid()
        button_grid.props.expand = True
        button_grid.props.halign = Gtk.Align.END
        button_grid.props.valign = Gtk.Align.CENTER
        button_grid.props.column_spacing = 6
        button_grid.props.row_spacing = 6

        # clean ui
        self.clean_ui()

        # universal widgets
        self.control_button = Gtk.Button().new_with_label("Control")
        self.control_button.connect("clicked", self.control)

        self.connect_button = Gtk.Button().new_with_label("Connect")
        self.connect_button.connect("clicked", self.connect)

        self.status_label = Gtk.Label("")
        self.status_label.props.use_markup = True
        self.status_label.props.halign = Gtk.Align.START

        if self.motor.getProperty("configured") == True:
            # info labels
            display_label = Gtk.Label(self.motor.getProperty("display-name"))
            display_label.props.wrap = True
            display_label.props.halign = Gtk.Align.START
            display_label.get_style_context().add_class("motor-detected")

            axis_label = Gtk.Label("<b>Axis:</b> {}".format(self.motor.getProperty("axis")))
            axis_label.props.use_markup = True
            axis_label.props.halign = Gtk.Align.START

            type_label = Gtk.Label("<b>Type:</b> {}".format(self.motor.getProperty("type")))
            type_label.props.use_markup = True
            type_label.props.halign = Gtk.Align.START

            id_label = Gtk.Label("<b>ID:</b> {}".format(self.motor.getProperty("id")))
            id_label.props.use_markup = True
            id_label.props.halign = Gtk.Align.START

            configure_button = Gtk.Button().new_with_label("Configure")
            configure_button.connect("clicked", self.configure)

            # attach things to the grid
            info_grid.attach(display_label, 0, 0, 1, 1)
            info_grid.attach(axis_label, 0, 1, 1, 1)
            info_grid.attach(type_label, 0, 2, 1, 1)
            info_grid.attach(self.status_label, 1, 1, 1, 1)
            info_grid.attach(id_label, 1, 2, 1, 1)

            button_grid.attach(self.control_button, 0, 0, 1, 1)
            button_grid.attach(self.connect_button, 0, 1, 1, 1)
            button_grid.attach(configure_button, 0, 2, 1, 1)

            # if there is no serial, add disconnected class
            if self.motor.serial == None:
                self.get_style_context().add_class("insensitive")
            else:
                self.get_style_context().remove_class("insensitive")

        else:
            # create motor detected
            motor_detected_label = Gtk.Label("New Motor Detected")
            motor_detected_label.props.wrap = True
            motor_detected_label.props.expand = True
            motor_detected_label.get_style_context().add_class("motor-detected")

            motor_id = Gtk.Label("<b>ID:</b> {}".format(self.motor.getProperty("id")))
            motor_id.props.use_markup = True
            motor_id.props.halign = Gtk.Align.START
            motor_id.props.wrap = True

            # configure button
            configure_button = Gtk.Button().new_with_label("Configure")
            configure_button.connect("clicked", self.configure)

            # attach things to the grid
            info_grid.attach(motor_detected_label, 0, 0, 1, 1)
            info_grid.attach(motor_id, 0, 1, 1, 1)

            button_grid.attach(configure_button, 0, 0, 1, 1)

        # add grids to box
        box.add(info_grid)
        box.add(button_grid)

        # add resulting grid to self
        self.add(box)

        # show all
        self.show_all()

        if self.motor.serial == None:
            self.control_button.props.visible = False
            self.connect_button.props.visible = True
            self.status = 0
        else:
            self.control_button.props.visible = True
            self.connect_button.props.visible = False
            self.status = 2

        self.update_status()

    def control(self, event, param=None):
        self.control_callback(self.motor)

    def connect(self, event, param=None):
        print("configure all the things")

    def configure(self, event, param=None):
        if self.motor.getProperty("configured") == True:
            dialog = NewMotorDialog(dname=self.motor.getProperty("display-name"),
                                    axis=self.motor.getProperty("axis"),
                                    mtype=self.motor.getProperty("type"))
        else:
            dialog = NewMotorDialog()

        # define method for applying changes from dialog
        def apply_configurations(event, param=None):
            # save configurations
            self.motor.setProperty("configured", True)
            self.motor.setProperty("display-name", dialog.display_name)
            self.motor.setProperty("axis", dialog.axis_name)
            self.motor.setProperty("type", dialog.type_name)

            # destroy dialog
            dialog.destroy()

            # update self
            self.update_ui()

        # connect to applied signal
        dialog.connect("applied", apply_configurations)

        # start the dialog
        dialog.run()

    def update_status(self):
        if self.status == 0:
            self.status_label.props.label = "<b>Status:</b> {}".format("Disconnected")

        elif self.status == 1:
            self.status_label.props.label = "<b>Status:</b> {}".format("Connecting…")

        elif self.status == 2:
            self.status_label.props.label = "<b>Status:</b> {}".format("Connected")

    def connect_serial(self, serial):
        self.motor.serial = serial
        self.update_ui()