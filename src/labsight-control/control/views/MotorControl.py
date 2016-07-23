
# imports
from gi.repository import Gtk, GObject
from threading import Thread
import queue
from control.widgets import ModeButton
from control.dialogs import NewMotorDialog
from control.dialogs import CalibrateDialog

# motor control class
class MotorControl(Gtk.Grid):

    moving = False
    relative_target = -1
    motor_mover = None

    queue = None

    movement_mode = ""
    use_steps = True

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

        self.calibrate_button = Gtk.Button().new_with_label("Calibrate")
        self.configure_button = Gtk.Button().new_with_label("Configure")

        # attach things to the grid
        info_grid.attach(self.display_label, 0, 0, 1, 1)
        info_grid.attach(self.axis_label, 0, 1, 1, 1)
        info_grid.attach(self.type_label, 1, 1, 1, 1)

        button_grid.attach(self.calibrate_button, 0, 0, 1, 1)
        button_grid.attach(self.configure_button, 0, 1, 1, 1)

         # add grids to box
        info_box.add(info_grid)
        info_box.add(button_grid)
        padding_box = Gtk.Box()
        padding_box.get_style_context().add_class("card")
        padding_box.add(info_box)

        # unit toggle
        self.unit_toggle = ModeButton(["Steps", "Units"])
        self.unit_toggle.props.halign = Gtk.Align.CENTER

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

        self.move_entry = Gtk.SpinButton().new_with_range(-20000.0, 20000.0, 0.1)
        self.move_entry.props.width_request = 160
        self.move_entry.props.orientation = Gtk.Orientation.HORIZONTAL
        self.move_button = Gtk.Button().new_with_label("Move")

        control_grid.attach(self.type_modebutton, 0, -1, 1, 1)
        control_grid.attach(self.move_entry, 0, 0, 1, 1)
        control_grid.attach(self.move_button, 0, 1, 1, 1)

        self.attach(padding_box, 0, 0, 2, 1)
        self.attach(self.unit_toggle, 0, 1, 2, 1)
        self.attach(status_grid, 1, 2, 1, 1)
        self.attach(control_grid, 0, 2, 1, 1)

    def update_ui(self):

        # reset some aspects of the ui
        self.move_entry.props.value = 0

        # set default movement mode
        self.type_modebutton.set_active("Relative")
        self.unit_toggle.set_active("Steps")

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

    def calibrate(self, origin=None, params=None):
        if self.motor != None:
            if self.motor.getProperty("calibrated") == True:
                dialog = CalibrateDialog(steps=self.motor.getProperty("calibrated-steps"),
                                        units=self.motor.getProperty("calibrated-units"))
            else:
                dialog = CalibrateDialog()

            # define method for applying changes from dialog
            def apply_configurations(event, param=None):
                # save configurations
                self.motor.setProperty("calibrated", True)
                self.motor.setProperty("calibrated-steps", dialog.steps)
                self.motor.setProperty("calibrated-units", dialog.units)

                # destroy dialog
                dialog.destroy()

                # update self
                self.update_ui()

            # connect to applied signal
            dialog.connect("applied", apply_configurations)

            # start the dialog
            dialog.run()

    def configure(self, origin=None, params=None):
        if self.motor != None:
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

                # set units active
                self.unit_toggle.set_active("Units")

            # connect to applied signal
            dialog.connect("applied", apply_configurations)

            # start the dialog
            dialog.run()

    def connect_signals(self):

        # connect buttons
        self.calibrate_button.connect("clicked", self.calibrate)
        self.configure_button.connect("clicked", self.configure)
        self.move_button.connect("clicked", self.move)
        self.reset_pos_button.connect("clicked", self.reset_pos)

        # update move position on all text changess
        def notify_text(origin=None, prop=None):
            if prop.name == "text":
                self.update_move_button()

        self.move_entry.props.buffer.connect("notify", notify_text)

        # connect unit mode button
        def update_unit(origin, selected):
            if self.motor != None:
                if selected == "Steps":
                    self.use_steps = True
                else:
                    self.use_steps = False
                    if not self.motor.getProperty("calibrated"):
                        self.unit_toggle.set_active("Steps")
                        self.calibrate()
                    self.move_entry.props.climb_rate = self.motor.getProperty("calibrated-units") / self.motor.getProperty("calibrated-steps")

            self.update_status()
            self.update_move_entry()

        self.unit_toggle.connect("mode-changed", update_unit)

        # connect move mode modebutton
        def update_mode(origin, selected):
            self.movement_mode = selected
            self.update_move_button()
        self.type_modebutton.connect("mode-changed", update_mode)

    def get_relative_target(self):
        target = 0
        # try:
        if self.move_entry.props.buffer.props.text != "":
            move_entry_value = 0
            if self.use_steps:
                move_entry_value = int(float(self.move_entry.props.buffer.props.text))
            else:
                move_entry_value = self.units_to_steps(float(self.move_entry.props.buffer.props.text))

            if self.movement_mode == "Relative":
                target = move_entry_value
            elif self.movement_mode == "Absolute":
                target = move_entry_value - self.motor.getProperty("step")
            # except:
                # pass

        return target

    def reset_pos(self, event=None, param=None):
        if self.motor != None:
            self.motor.setProperty("step", 0)
            self.update_status()

    def update_pos(self, pos):
        position = self.motor.getProperty("step") + int(pos.data)
        if not self.use_steps:
            position = self.steps_to_units(position)

        self.pos_val.props.label = "{} {}".format(position, self.get_position_units())
        self.move_entry.props.progress_fraction = int(pos.data) / self.relative_target

    def update_move_button(self, a=None, b=None, c=None, d=None):
        # update move button
        target = self.get_relative_target()
        if not self.use_steps:
            target = self.steps_to_units(target)

        self.move_button.props.label = "Move {} {}".format(target, self.get_position_units())

    def update_move_entry(self):
        if self.use_steps:
            self.move_entry.props.value = self.units_to_steps(float(self.move_entry.props.buffer.props.text))
            self.move_entry.set_increments(1.0, 1.0)
        else:
            self.move_entry.props.value = self.steps_to_units(float(self.move_entry.props.buffer.props.text))
            self.move_entry.set_increments(self.motor.getProperty("calibrated-units"), self.motor.getProperty("calibrated-units"))


    def update_status(self):
        if self.motor != None:
            # display label
            self.display_label.props.label = str(self.motor.getProperty("display-name"))

            # axis label
            self.axis_label.props.label = "<b>Axis:</b> {}".format(self.motor.getProperty("axis"))

            # type label
            self.type_label.props.label = "<b>Type:</b> {}".format(self.motor.getProperty("type"))

            # position value
            if self.use_steps:
                self.pos_val.props.label = "{} {}".format(self.motor.getProperty("step"), self.get_position_units())
            else:
                self.pos_val.props.label = "{} {}".format(self.steps_to_units(self.motor.getProperty("step")), self.get_position_units())

            # kill value
            self.vel_val.props.label = "{} {}".format(0, self.get_velocity_units())

            # update entry
            self.move_entry.props.progress_fraction = 0
            self.move_button.props.sensitive = True

            self.update_move_button()

    def steps_to_units(self, steps):
        return round(steps * (self.motor.getProperty("calibrated-units") / self.motor.getProperty("calibrated-steps")), 3)

    def units_to_steps(self, units):
        return int(units * (self.motor.getProperty("calibrated-steps") / self.motor.getProperty("calibrated-units")))

    def get_position_units(self):
        if self.use_steps:
            return "steps"
        elif self.motor != None:
            if self.motor.getProperty("type") == "Rotational":
                return "degs"
            elif self.motor.getProperty("type") == "Linear":
                return "cms"

    def get_velocity_units(self):
        return "{}/s".format(self.get_position_units())

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
