
# imports
from gi.repository import Gtk, Gdk, GObject

class ModeButton(Gtk.Box):

    # setup signals
    __gsignals__ = {
        "mode-changed": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,))
    }

    active = None

    def __init__(self, option_list):
        Gtk.Box.__init__(self)

        self.props.homogeneous = True
        self.props.spacing = 0
        self.props.can_focus = False

        self.get_style_context().add_class(Gtk.STYLE_CLASS_LINKED)

        self.buttons = {}

        for option in option_list:
            button = Gtk.ToggleButton().new_with_label(option)

            self.buttons[option] = button

            def click(btn, param=None):
                for key in self.buttons:
                    if self.buttons[key] == btn:
                        self.buttons[key].props.active = True
                        self.emit("mode-changed", key)
                    else:
                        self.buttons[key].props.active = False

                return True

            button.connect("button-press-event", click)

            self.add(button)

            button.show_all()

    def set_active(self, option):
        for key in self.buttons:
            if key == option:
                self.buttons[key].props.active = True
                self.emit("mode-changed", key)
            else:
                self.buttons[key].props.active = False

