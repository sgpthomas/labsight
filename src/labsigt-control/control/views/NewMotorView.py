
# imports
from gi.repository import Gtk, GLib

# new motor view class
class NewMotorView(Gtk.Dialog):
    # constructor
    def __init__(self):
        # call super constructor
        Gtk.Box.__init__(self)
        # self.props.border_width = 24
        self.set_resizable(False)
        self.set_deletable(False)
        self.set_modal(True)

        # build_ui
        self.build_ui()

        self.connect("response", self.on_response)

        # show all
        self.show_all()

    def build_ui(self):
        # grid
        grid = Gtk.Grid()
        grid.props.margin = 6
        grid.props.column_spacing = 12
        grid.props.width_request = 300

        # Display Name
        title = self.get_title_widget("Display Name:")
        description = self.get_description_widget("A name you can use to identify\nthis motor")
        entry = Gtk.Entry()
        entry.props.hexpand = True

        grid.attach(title, 0, 0, 1, 1)
        grid.attach(description, 0, 1, 1, 1)
        grid.attach(entry, 1, 0, 1, 2)

        # Axis
        title = self.get_title_widget("Axis:")
        description = self.get_description_widget("Choose the axis this motor controls")
        axis_list = ["X", "Y", "Z"]
        entry = Gtk.ComboBoxText()
        entry.props.hexpand = True
        entry.props.valign = Gtk.Align.CENTER
        for axis in axis_list:
            entry.append_text(axis)

        grid.attach(title, 0, 2, 1, 1)
        grid.attach(description, 0, 3, 1, 1)
        grid.attach(entry, 1, 2, 1, 2)

        # Type
        title = self.get_title_widget("Type:")
        description = self.get_description_widget("Decides whether to use\nrotational or linear coordinates")
        type_list = ["Linear", "Rotational"]
        entry = Gtk.ComboBoxText()
        entry.props.hexpand = True
        entry.props.valign = Gtk.Align.CENTER
        for t in type_list:
            entry.append_text(t)

        grid.attach(title, 0, 4, 1, 1)
        grid.attach(description, 0, 5, 1, 1)
        grid.attach(entry, 1, 4, 1, 2)

        # save configuration
        # self.save_button = Gtk.Button().new_with_label("Save Configuration")
        # grid.attach(self.save_button, 0, 6, 2, 1)

        # create scrolled box, add grid to it, add scroll to self
        # scroll = Gtk.ScrolledWindow()
        # scroll.props.expand = True
        # scroll.add(grid)

        self.get_content_area().add(grid)

        # add actions
        self.add_button("Cancel", Gtk.ResponseType.CLOSE)
        self.add_button("Save", Gtk.ResponseType.APPLY)

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

        elif param == Gtk.ResponseType.APPLY:
            print("apply")
        