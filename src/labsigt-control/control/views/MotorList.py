
# imports
from gi.repository import Gtk, GObject
from labsight.motor import Motor
from labsight import controller
from control.views.NewMotorView import NewMotorView
from multiprocessing import Pool

# Motor List Class
class MotorList(Gtk.Box):

    # stack
    stack = None

    # widgets
    list_box = None

    scrolled_window = None

    # setup signals
    __gsignals__ = {
        "done-loading": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ())
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
        self.stack.add_named(grid, "loading")

        # create list box
        self.create_list_box()

        # add to scrolled window
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.add(self.list_box)

        self.stack.add_named(self.scrolled_window, "list")

        # add to this
        self.add(self.stack)

        # create pool
        self.pool = Pool(processes=1)

        self.show_all()

    def create_list_box(self):
        self.list_box = Gtk.ListBox()
        self.list_box.props.expand = True
        self.list_box.props.selection_mode = Gtk.SelectionMode.NONE

        # add css class to this for styling
        self.list_box.get_style_context().add_class("motor-list")

    def start_load(self):
        self.stack.set_visible_child_name("loading")
        self.spinner.start()

        self.pool.apply_async(controller.getMotors, (), callback=self.end_load)

    def end_load(self, result):
        self.spinner.stop()
        self.stack.set_visible_child_name("list")

        for motor in result:
            self.list_box.insert(MotorListChild(motor), -1)

        self.emit("done-loading")

class MotorListChild(Gtk.ListBoxRow):

    # grid for this
    grid = None

    # motor id
    motor = None

    # widgets
    motor_detected_label = None
    configure_button = None

    # constructor
    def __init__(self, motor):
        Gtk.ListBoxRow.__init__(self)

        # build ui
        self.build_ui()

        # show all
        self.show_all()

    def build_ui(self):
        # add class to self
        self.get_style_context().add_class("motor-list-child")
        self.props.margin = 6

        # create grid
        self.grid = Gtk.Grid()
        self.grid.props.expand = True
        self.grid.props.halign = Gtk.Align.CENTER
        self.grid.props.column_spacing = 6

        # create motor detected
        self.motor_detected_label = Gtk.Label("New Motor Detected")
        self.motor_detected_label.props.wrap = True
        self.motor_detected_label.props.expand = True
        self.motor_detected_label.props.valign = Gtk.Align.CENTER
        self.motor_detected_label.props.halign = Gtk.Align.START
        self.motor_detected_label.props.justify = Gtk.Justification.CENTER
        self.motor_detected_label.get_style_context().add_class("motor-detected")

        # configure button
        self.configure_button = Gtk.Button().new_with_label("Configure")
        self.props.valign = Gtk.Align.CENTER
        self.configure_button.connect("clicked", self.configure)

        # attach things to the grid
        self.grid.attach (self.motor_detected_label, 0, 0, 1, 3)
        self.grid.attach (self.configure_button, 1, 1, 1, 1)

        self.add(self.grid)

    def configure(self, event, param=None):
        dialog = NewMotorView()
        dialog.run()