
# imports
from gi.repository import Gtk, GObject
from threading import Thread
import queue
from control.widgets import ModeButton

# motor control class
class MotorControl(Gtk.Grid):

    moving = False
    relative_target = -1
    motor_mover = None

    queue = None

    movement_mode = ""

    __gsignals__ = {
        "go-back": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ())
    }

    def __init__(self, motor = None):
        Gtk.Grid.__init__(self)

        self.props.margin = 6
        self.props.row_spacing = 6

        # globalize motor
        self.motor = motor

        # build_ui
        self.init_ui()
        self.update_ui()

        # connect signals
        self.connect_signals()

    def init_ui(self):
        # box
        info_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        info_box.props.vexpand = False
        info_box.props.margin = 6

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

        # info labels
        self.display_label = Gtk.Label("")
        self.display_label.props.wrap = True
        self.display_label.props.halign = Gtk.Align.START
        self.display_label.get_style_context().add_class("motor-detected")

        self.axis_label = Gtk.Label("")
        self.axis_label.props.use_markup = True
        self.axis_label.props.halign = Gtk.Align.START

        self.type_label = Gtk.Label("")
        self.type_label.props.use_markup = True
        self.type_label.props.halign = Gtk.Align.START

        configure_button = Gtk.Button().new_with_label("Configure")
        control_button = Gtk.Button().new_with_label("Calibrate")

        # attach things to the grid
        info_grid.attach(self.display_label, 0, 0, 1, 1)
        info_grid.attach(self.axis_label, 0, 1, 1, 1)
        info_grid.attach(self.type_label, 1, 1, 1, 1)

        button_grid.attach(control_button, 0, 0, 1, 1)
        button_grid.attach(configure_button, 0, 1, 1, 1)

         # add grids to box
        info_box.add(info_grid)
        info_box.add(button_grid)
        padding_box = Gtk.Box()
        padding_box.get_style_context().add_class("card")
        padding_box.add(info_box)

        # status grid
        status_grid = Gtk.Grid()
        status_grid.props.halign = Gtk.Align.CENTER
        status_grid.props.margin = 6
        status_grid.props.row_spacing = 6
        status_grid.props.column_spacing = 12

        pos_stat = Gtk.Label("Position:")
        pos_stat.props.halign = Gtk.Align.END
        pos_stat.get_style_context().add_class("status")

        vel_stat = Gtk.Label("Velocity:")
        vel_stat.props.halign = Gtk.Align.END
        vel_stat.get_style_context().add_class("status")

        self.pos_val = Gtk.Label("")
        self.pos_val.props.halign = Gtk.Align.START
        self.pos_val.get_style_context().add_class("value")

        self.vel_val = Gtk.Label("")
        self.vel_val.props.halign = Gtk.Align.START
        self.vel_val.get_style_context().add_class("value")

        self.reset_pos_button = Gtk.Button().new_with_label("Reset Position")
        self.reset_pos_button.props.halign = Gtk.Align.CENTER

        status_grid.attach(pos_stat, 0, 0, 1, 1)
        status_grid.attach(self.pos_val, 1, 0, 1, 1)
        status_grid.attach(vel_stat, 0, 1, 1, 1)
        status_grid.attach(self.vel_val, 1, 1, 1, 1)
        status_grid.attach(self.reset_pos_button, 0, 2, 2, 1)

        # control box
        control_grid = Gtk.Grid()
        control_grid.props.halign = Gtk.Align.START
        control_grid.props.margin = 6
        control_grid.props.row_spacing = 6
        control_grid.props.column_spacing = 12

        # self.type_modebutton = ModeButton("Absolute", "Relative")
        self.type_modebutton = ModeButton(["Absolute", "Relative"])
        def update_mode(origin, selected):
            self.movement_mode = selected
            self.update_move_button()
        self.type_modebutton.connect("mode-changed", update_mode)

        self.move_entry = Gtk.SpinButton().new_with_range(-2000000, 2000000, 1)
        self.move_entry.props.width_request = 160
        self.move_button = Gtk.Button().new_with_label("Move")

        control_grid.attach(self.type_modebutton, 0, -1, 1, 1)
        control_grid.attach(self.move_entry, 0, 0, 1, 1)
        control_grid.attach(self.move_button, 0, 1, 1, 1)

        self.attach(padding_box, 0, 0, 2, 1)
        self.attach(status_grid, 1, 1, 1, 1)
        self.attach(control_grid, 0, 1, 1, 1)

    def update_ui(self):

        # reset some aspects of the ui
        self.move_entry.props.value = 0

        # set default movement mode
        self.type_modebutton.set_active("Relative")

        # update status
        self.update_status()

        # show all
        self.show_all()

    def move(self, event, param=None):
        if self.motor != None:

            if self.motor_mover != None:
                self.motor_mover.join()
            
            # define callback
            def callback(result):
                self.update_status()
                self.queue = None

            self.relative_target = self.get_relative_target()

            # set button to be insenstive
            self.move_button.props.sensitive = False

            self.queue = queue.Queue()

            # setup thread and queue
            self.motor_mover = MotorMover(self.motor, self.relative_target, self.queue, move_func=self.update_pos, callback=callback)
            self.motor_mover.start()

            while self.queue != None:
                task = self.queue.get()
                task()

                while Gtk.events_pending():
                    Gtk.main_iteration()

    def connect_signals(self):
        self.move_button.connect("clicked", self.move)
        self.reset_pos_button.connect("clicked", self.reset_pos)

        # update move position on all text changess
        def notify_text(origin=None, prop=None):
            if prop.name == "text":
                self.update_move_button()

        self.move_entry.props.buffer.connect("notify", notify_text)

    def get_relative_target(self):
        target = 0
        try:
            move_entry_value = int(self.move_entry.props.buffer.props.text)
            if self.movement_mode == "Relative":
                target = move_entry_value
            elif self.movement_mode == "Absolute":
                target = move_entry_value - self.motor.getProperty("step")
        except:
            pass

        return target

    def reset_pos(self, event=None, param=None):
        if self.motor != None:
            self.motor.setProperty("step", 0)
            self.update_status()

    def update_pos(self, pos):
        self.pos_val.props.label = "%s %s" % (str(int(self.motor.getProperty("step")) + int(pos.data)), self.get_position_units())
        self.move_entry.props.progress_fraction = int(pos.data) / self.relative_target

    def update_move_button(self, a=None, b=None, c=None, d=None):
        # update move button
        self.move_button.props.label = "Move {} {}".format(self.get_relative_target(), self.get_position_units())

    def update_status(self):
        if self.motor != None:
            # display label
            self.display_label.props.label = str(self.motor.getProperty("display-name"))

            # axis label
            self.axis_label.props.label = "<b>Axis:</b> {}".format(self.motor.getProperty("axis"))

            # type label
            self.type_label.props.label = "<b>Type:</b> {}".format(self.motor.getProperty("type"))

            # position value
            self.pos_val.props.label = "%s %s" % (str(int(self.motor.getProperty("step"))), self.get_position_units())

            # kill value
            self.vel_val.props.label = "{} {}".format(0, self.get_velocity_units())

            # update entry
            self.move_entry.props.progress_fraction = 0
            self.move_button.props.sensitive = True

            self.update_move_button()

    def get_position_units(self):
        return "steps"

    def get_velocity_units(self):
        return "steps/s"

class MotorMover(Thread):
    def __init__(self, motor, step, motor_queue, move_func = None, callback = None):
        Thread.__init__(self)

        self.motor = motor
        self.step = step
        self.move_func = move_func
        self.callback = callback
        self.queue = motor_queue

    def run(self):
        def queue_move(pos):
            self.queue.put(lambda: self.move_func(pos))

        # res = self.motor.setStep(self.step, self.move_func)
        res = self.motor.setStep(self.step, queue_move)

        if self.callback != None:
            self.queue.put(lambda: self.callback(res))