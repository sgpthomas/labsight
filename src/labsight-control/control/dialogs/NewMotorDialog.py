
# imports
from gi.repository import Gtk, GObject

# new motor view class
class NewMotorDialog(Gtk.Dialog):

    # create apply signal
    __gsignals__ = {
        "applied": (GObject.SIGNAL_RUN_FIRST, None, ())
    }

    # constructor
    def __init__(self, dname=None, axis=None, mtype=None):
        # call super constructor
        Gtk.Box.__init__(self)
        # self.props.border_width = 24
        self.set_resizable(False)
        self.set_deletable(False)
        self.set_modal(True)

        # build_ui
        self.build_ui(dname, axis, mtype)

        self.connect("response", self.on_response)

        # show all
        self.show_all()

    def build_ui(self, dname, axis, mtype):
        # grid
        grid = Gtk.Grid()
        grid.props.margin = 6
        grid.props.column_spacing = 12

        # Display Name
        title = self.get_title_widget("Display Name:")
        description = self.get_description_widget("A name you can use to identify\nthis motor")
        self.name = Gtk.Entry()
        self.name.props.text = dname
        self.name.props.hexpand = True

        grid.attach(title, 0, 0, 1, 1)
        grid.attach(description, 0, 1, 1, 1)
        grid.attach(self.name, 1, 0, 1, 2)

        # Axis
        title = self.get_title_widget("Axis:")
        description = self.get_description_widget("Choose the axis this motor controls")
        axis_list = ["X", "Y", "Z"]
        self.axis_combo = Gtk.ComboBoxText()
        self.axis_combo.props.hexpand = True
        self.axis_combo.props.valign = Gtk.Align.CENTER
        for ax in axis_list:
            self.axis_combo.append_text(ax)
        if axis in axis_list:
            self.axis_combo.props.active = axis_list.index(axis)

        grid.attach(title, 0, 2, 1, 1)
        grid.attach(description, 0, 3, 1, 1)
        grid.attach(self.axis_combo, 1, 2, 1, 2)

        # Type
        title = self.get_title_widget("Type:")
        description = self.get_description_widget("Decides whether to use\nrotational or linear coordinates")
        type_list = ["Linear", "Rotational"]
        self.type_combo = Gtk.ComboBoxText()
        self.type_combo.props.hexpand = True
        self.type_combo.props.valign = Gtk.Align.CENTER
        for t in type_list:
            self.type_combo.append_text(t)
        if mtype in type_list:
            self.type_combo.props.active = type_list.index(mtype)

        grid.attach(title, 0, 4, 1, 1)
        grid.attach(description, 0, 5, 1, 1)
        grid.attach(self.type_combo, 1, 4, 1, 2)

        # watch for changes in all the things
        def buffer_changed(origin=None, prop=None):
            if prop.name == "text":
                self.update_actions()
        self.name.props.buffer.connect("notify", buffer_changed)

        self.axis_combo.connect("changed", self.update_actions)
        self.type_combo.connect("changed", self.update_actions)

        self.get_content_area().add(grid)

        # add actions
        self.add_button("Cancel", Gtk.ResponseType.CLOSE)
        self.add_button("Save", Gtk.ResponseType.APPLY)

        self.update_actions()

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

    def update_actions(self, event=None, param=None):
        sensitive = True
        if self.name.props.text == "" or self.name.props.text == None:
            sensitive = False

        if self.axis_combo.get_active_text() == None:
            sensitive = False

        if self.type_combo.get_active_text() == None:
            sensitive = False

        self.get_widget_for_response(Gtk.ResponseType.APPLY).props.sensitive = sensitive

    def on_response(self, event, param=None):
        if param == Gtk.ResponseType.CLOSE:
            self.destroy()

        if param == Gtk.ResponseType.APPLY:
            self.display_name = self.name.props.text
            self.axis_name = self.axis_combo.get_active_text()
            self.type_name = self.type_combo.get_active_text()
            self.emit("applied")
