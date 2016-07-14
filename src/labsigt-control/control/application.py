
# ensure that we have the right version of gtk
import gi
gi.require_version ("Gtk", "3.0")

# imports
from gi.repository import Gtk, Gio, GLib, Gdk
from control.window import MainWindow
import control.config as config
import os

# application class
class Application(Gtk.Application):
    # init function
    def __init__(self):
        Gtk.Application.__init__(self, application_id=config.RESOURCE_NAME,
                                    flags=Gio.ApplicationFlags.FLAGS_NONE)

        # Set application name
        GLib.set_application_name(config.APP_NAME)
        GLib.set_prgname(config.EXEC_NAME)

        # add stylesheet
        add_stylesheet("main.css")

        # window
        self._window = None

    def do_activate(self):
        # window does not yet exist, create one
        if not self._window:
            self._window = MainWindow(self)

        # present the window to the user
        self._window.present()

        # start gtk main loop
        Gtk.main()

# add a stylesheet
def add_stylesheet(name):
    provider = Gtk.CssProvider()
    css_file = os.path.join(config.STYLE_DIR, name)
    try:
        provider.load_from_path(css_file) # load css file
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        print("Loaded %s" % css_file)
    except GLib.Error as e:
        print("Error loading %s" % css_file)
        print("%s" % e.message)