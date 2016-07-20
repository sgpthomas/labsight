
# imports
from gi.repository import Gtk, GObject, Gio
import control.config as config

class WelcomeView(Gtk.Grid):

    # setup signals
    __gsignals__ = {
        "refresh-motor-list": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ())
    }

    # constructor
    def __init__(self):
        Gtk.Grid.__init__(self)

        # set some grid properties
        self.props.valign = Gtk.Align.CENTER
        self.props.row_spacing = 6
        self.props.border_width = 24

        # create widgets
        header = Gtk.Label("No Motors Detected.")
        header.props.hexpand = True
        header.props.halign = Gtk.Align.CENTER
        header.get_style_context().add_class("welcome-header")
        header.props.wrap = True
        header.props.justify = Gtk.Justification.CENTER

        description = Gtk.Label("Plug a compatible motor in and press 'Refresh'")
        description.props.hexpand = True
        description.props.halign = Gtk.Align.CENTER
        description.get_style_context().add_class("welcome-description")
        header.props.wrap = True
        header.props.justify = Gtk.Justification.CENTER

        welcome_button = Gtk.Button()
        welcome_button.props.label = "Refresh"
        welcome_button.props.expand = False
        welcome_button.props.halign = Gtk.Align.CENTER
        welcome_button.get_style_context().add_class("welcome-button")

        # build user interface
        self.attach(header, 0, 0, 1, 1)
        self.attach(description, 0, 1, 1, 1)
        self.attach(welcome_button, 0, 2, 1, 1)

        # show all
        self.show_all()

        # connect to button clicked
        welcome_button.connect("clicked", self.clicked_new_motor)

    def clicked_new_motor(self, event, param=None):
        self.emit("refresh-motor-list")
