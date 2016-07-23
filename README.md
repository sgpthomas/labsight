# LabSight

This will detail every subroutine that we write.

## Files

The current goal for these files is that they allow you to control motors, in a manner similar to NI MAX. Functionality for dataruns will be added later.

(Note from Sam: This Controller Library is being built from the ground up to allow for multiple motors. It is much harder to add this at a later stage)

Any planned functions can be added to these files as is seen fit.

### File List:

* child.ino
  - Supports every Arduino command of the protocol as outlined in the Google doc

* controller.py
  - Based off of the current Controller.py
  - Conducts the serial communications, and contains the base functionality for all of the various protocol commands related to the controller
  - Communicates with the arduino for the GUI

* application.py
  - The first program that is run when the GUI is started.
  - Coordinates all actions of the GUI

* window.py
  - Some utility functions that allow the GUI to exist, and set up everything for the rest of the GUI files

* main.css
  - CSS styling for the GUI
  
* MotorControl.py, MotorList.py, WelcomeView.py
  - Welcome view is what is diaplayed upon opening the application for the first time, when no Arduinos are connected
  - Motor list is the menu shown for listing each motor
  - Motor control is the view that can be accessed for each motor from the motor list, allowing you to move the and configue the motors in various ways

* CalibrateDialog.py and NewMotorDialog.py
  - Calibrate dialog is used for inputting conversions between degrees/centimetres and steps
  - New motor dialog is used for giving the motor a name, and setting its axis and movement type
    - Functionality is minimal at this point for these configuration settings

* config.py
  - Various global infos for the GUI

* labsight-control
  - A bash file for starting the GUI

* ModeButton.py
  - A widget for changing between steps and the appropriate unit, while in the motor control view

* encoder.ino
  - Testing encoder code before moving it to child.ino

* datarun.py
    - A placeholder file for our later datarun functionality

* __init__.py
  - Various files necessary for the creation of a Python library
  - Adds certain features that ease accessing functions from within the library

## Protocol

  - *Every message has three parts (symbol, command, data)*
    - *Symbol indicates the how the action is performed*
      - *Symbols are always 1 character*
    - *Command indicates the specific action*
    - *Data consists of the arguments or output for the action (this depends on the symbol used)*
  - *Controller initiates all contact and child always responds with something*
  - *Send underscore `_` when there is no data to send*

* **Symbols Used by Controller**
  - Questions, like a get function (**?**)
  - Commands, like a set function (**!**)
* **Symbols Used by Arduino**
  - Responses from Arduino (**$**)
  - Stream (**>**)
  - Errors (**@**)
* **Commands**
  - step
  - id
  - kill
  - halt?
  - speed
  
## Original Objectives for the GUI:
  - A GUI class that communicates with controller.py, and provides NI-MAX functionality
  - It will ultimately manifest itself as a sidebar, but for now it will probably be the only GUI we have.
  - Features:
    - Motor Dashboard that indicates for each motor (in no particular order):
      - Has it been killed?
      - Is it moving?
      - Is it ready?
      - Has an error occurred?
    - Movement (which can be converted between centimeters or steps)
      - Relative motion
      - Absolute motion
    - Setting the origin
    - Changing the motor's speed
    - Ability to change between motors
