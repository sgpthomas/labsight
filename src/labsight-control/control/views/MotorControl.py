
# imports
from gi.repository import Gtk, GObject
from threading import Thread
import queue

# motor control class
class MotorControl(Gtk.Grid):

    moving = False
    relative_target = -1
    motor_mover = None

    queue = None

    # constructor

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
        # back button
        back_button = Gtk.Button().new_with_label("Back")
        back_button.props.halign = Gtk.Align.START
        back_button.get_style_context().add_class("back-button")
        def back_click(event, param = None):
            self.emit("go-back")

        back_button.connect("clicked", back_click)

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
        status_grid.props.halign = Gtk.Align.END
        status_grid.props.margin = 6
        status_grid.props.row_spacing = 6
        status_grid.props.column_spacing = 12

        pos_stat = Gtk.Label("Position:")
        pos_stat.props.halign = Gtk.Align.END
        pos_stat.get_style_context().add_class("status")

        move_stat = Gtk.Label("Moving:")
        move_stat.props.halign = Gtk.Align.END
        move_stat.get_style_context().add_class("status")

        kill_stat = Gtk.Label("Killed:")
        kill_stat.props.halign = Gtk.Align.END
        kill_stat.get_style_context().add_class("status")

        self.pos_val = Gtk.Label("")
        self.pos_val.props.halign = Gtk.Align.START
        self.pos_val.get_style_context().add_class("value")

        self.move_val = Gtk.Label("")
        self.move_val.props.halign = Gtk.Align.START
        self.move_val.get_style_context().add_class("value")

        self.kill_val = Gtk.Label("")
        self.kill_val.props.halign = Gtk.Align.START
        self.kill_val.get_style_context().add_class("value")

        status_grid.attach(pos_stat, 0, 0, 1, 1)
        status_grid.attach(self.pos_val, 1, 0, 1, 1)
        status_grid.attach(move_stat, 0, 1, 1, 1)
        status_grid.attach(self.move_val, 1, 1, 1, 1)
        status_grid.attach(kill_stat, 0, 2, 1, 1)
        status_grid.attach(self.kill_val, 1, 2, 1, 1)

        # control box
        control_grid = Gtk.Grid()
        control_grid.props.halign = Gtk.Align.START
        control_grid.props.margin = 6
        control_grid.props.row_spacing = 6
        control_grid.props.column_spacing = 12

        self.entry = Gtk.Entry()
        self.move_button = Gtk.Button().new_with_label("Move")

        control_grid.attach(self.entry, 0, 0, 1, 1)
        control_grid.attach(self.move_button, 0, 1, 1, 1)

        self.attach(back_button, 0, -1, 1, 1)
        self.attach(padding_box, 0, 0, 2, 1)
        self.attach(status_grid, 1, 1, 1, 1)
        self.attach(control_grid, 0, 1, 1, 1)

    def update_ui(self):

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
                self.move_button.props.sensitive = True
                self.queue = None

            # set button to be insenstive
            self.move_button.props.sensitive = False

            self.move_val.get_style_context().add_class("green")
            self.move_val.get_style_context().remove_class("red")
            self.move_val.props.label = "True"

            self.relative_target = int(self.entry.props.text)

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

    def update_pos(self, pos):
        self.move_val.props.label = "%i / %i" % (int(pos.data), self.relative_target)

    def update_status(self):
        if self.motor != None:
            # display label
            self.display_label.props.label = str(self.motor.getProperty("display-name"))

            # axis label
            self.axis_label.props.label = "<b>Axis:</b> {}".format(self.motor.getProperty("axis"))

            # type label
            self.type_label.props.label = "<b>Type:</b> {}".format(self.motor.getProperty("type"))

            # position value
            self.pos_val.props.label = str(self.motor.getProperty("step"))

            # moving value
            self.move_val.props.label = "False"
            self.move_val.get_style_context().add_class("red")
            self.move_val.get_style_context().remove_class("green")

            # kill value
            # self.kill_val.props.label = str(self.motor.getProperty("kill"))
            self.kill_val.props.label = "False"
            self.kill_val.get_style_context().add_class("red")
            self.kill_val.get_style_context().remove_class("green")

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