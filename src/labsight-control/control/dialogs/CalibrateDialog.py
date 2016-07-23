
# imports
from gi.repository import Gtk, GObject

# new motor view class
class CalibrateDialog(Gtk.Dialog):

    # create apply signal
    __gsignals__ = {
        "applied": (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    # constructor
    def __init__(self, steps=None, units=None):
        # call super constructor
        Gtk.Box.__init__(self)
        # self.props.border_width = 24
        self.set_resizable(False)
        self.set_deletable(False)
        self.set_modal(True)

        # build_ui
        self.build_ui(steps, units)

        self.connect("response", self.on_response)

        # show all
        self.show_all()

    def build_ui(self, steps, units):
        # grid
        grid = Gtk.Grid()
        grid.props.margin = 6
        grid.props.column_spacing = 12

        # Units
        title = self.get_title_widget("Units:")
        description = self.get_description_widget("The number of units per number\nof steps you define below.")
        self.units_entry = Gtk.Entry()
        if units != None:
            self.units_entry.props.text = str(units)
        self.units_entry.props.hexpand = True

        grid.attach(title, 0, 0, 1, 1)
        grid.attach(description, 0, 1, 1, 1)
        grid.attach(self.units_entry, 1, 0, 1, 2)

        # Steps
        title = self.get_title_widget("Steps:")
        description = self.get_description_widget("The number of steps per number\nof units you define above.")
        self.steps_entry= Gtk.Entry()
        if steps != None:
            self.steps_entry.props.text = str(steps)
        self.steps_entry.props.hexpand = True

        grid.attach(title, 0, 2, 1, 1)
        grid.attach(description, 0, 3, 1, 1)
        grid.attach(self.steps_entry, 1, 2, 1, 2)

        self.get_content_area().add(grid)

        # add actions
        self.add_button("Cancel", Gtk.ResponseType.CLOSE)
        self.add_button("Calibrate", Gtk.ResponseType.APPLY)

    def get_title_widget(self, string):
        title = Gtk.Label(string)
        title.props.halign = Gtk.Align.END
        title.get_style_context().add_class("new-motor-title")

        return title

    def get_description_widget(self, string):
        description = Gtk.Label(string)
        description.props.halign = Gtk.Align.END
        description.props.justify = Gtk.Justification.RIGHT
        description.props.wrap = True
        description.get_style_context().add_class("new-motor-description")

        return description

    def on_response(self, event, param=None):
        if param == Gtk.ResponseType.CLOSE:
            self.destroy()

        if param == Gtk.ResponseType.APPLY:
            self.steps = float(self.steps_entry.props.text)
            self.units = float(self.units_entry.props.text)
            self.emit("applied")
