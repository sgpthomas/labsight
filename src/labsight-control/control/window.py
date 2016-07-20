
# imports
from gi.repository import Gtk, GObject, Gio
import control.config as config
from control.views.WelcomeView import WelcomeView
from control.views.MotorList import MotorList
from control.views.MotorControl import MotorControl

from threading import Timer

# window class
class MainWindow(Gtk.Window):

    """ properties and widgets """
    stack = None

    # views
    welcome = None

    # loading
    loading = False

    # constructor
    def __init__(self, app):
        Gtk.Window.__init__(self, title=config.APP_TITLE)

        # window settings
        self.set_size_request(650, 700)

        # build ui
        self.build_ui()

        # connect signals
        self.connect_signals()

        # show all the things
        self.show_all()

        self.refresh()

    def build_ui(self):
        # initiate stack
        self.stack = Gtk.Stack()
        self.stack.props.transition_type = Gtk.StackTransitionType.SLIDE_LEFT_RIGHT

        # create welcome view and add it to the stack
        self.welcome = WelcomeView()
        self.stack.add_named(self.welcome, "welcome")

        self.motor_list = MotorList()
        self.stack.add_named(self.motor_list, "motor-list")

        self.motor_control = MotorControl()
        self.stack.add_named(self.motor_control, "motor-control")

        self.add(self.stack)

        # build headerbar
        self.back_button = Gtk.Button().new_with_label("Back")
        self.back_button.get_style_context().add_class("back-button")
        self.back_button.props.visible = False
        self.back_button.props.no_show_all = True

        self.headerbar = Gtk.HeaderBar()
        self.headerbar.pack_start(self.back_button)
        self.headerbar.set_show_close_button(True)
        self.headerbar.set_title(config.APP_TITLE)

        self.set_titlebar(self.headerbar)

    def connect_signals(self):
        self.connect("destroy", self.destroy) # connect the close button to destroying the window
        self.welcome.connect("refresh-motor-list", self.refresh)
        self.motor_list.connect("done-loading", self.done_loading)
        self.motor_list.connect("control-motor", self.control_motor)
        self.back_button.connect("clicked", self.to_list)

    # signal functions
    def destroy(self, event=None, param=None):
        # print(self.loading)
        if not self.loading:
            Gtk.main_quit()
        else:
            Timer(1, self.destroy).start()

    def refresh(self, event=None, param=None):
        self.loading = True
        self.stack.set_visible_child_name("motor-list")
        self.motor_list.start_load()

    def done_loading(self, event, param=None):
        self.loading = False

        if len(self.motor_list.list_box.get_children()) < 1:
            self.stack.set_visible_child_name("welcome")

    def control_motor(self, event, motor):
        self.back_button.props.visible = True
        self.motor_control.motor = motor
        self.motor_control.update_ui()
        self.stack.set_visible_child_name("motor-control")

    def to_list(self, event, param=None):
        self.back_button.props.visible = False
        self.motor_control.motor = None
        self.stack.set_visible_child_name("motor-list")