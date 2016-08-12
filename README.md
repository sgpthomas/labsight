# LabSight

A collection of code for controlling motors, intended for probe drives. Includes an Arduino sketch, a Python control library and a GUI for using all of it.

## Files

The current goal for these files is that they allow you to control motors, in a manner similar to NI MAX. Functionality for dataruns will be added later.

Any planned functions will be added to these files as is seen fit.

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

* **Symbols**
  * Used by Controller:
    - Questions, like a get function (**?**)
    - Commands, like a set function (**!**)
  * Used by Arduino:
    - Responses from Arduino (**$**)
    - Stream (**>**)
    - Errors (**@**)
* **Motor Index**
  - Specifies which of the up to two motors per Arduino you would like to apply the given command to
  - It is zero-indexed
* **Commands**
  - init - A function that starts the streaming of encoder data. It was implemented so that when the Python library checks for the version and id, it is not immediately overwhelemed by frivolous encoder readings
  - version - Returns the protocol version upploaded to the arduino, for compatibility reasons
  - id - Allows the getting and setting a string to identify the arduino by
  - step - Enables one to get the current position in steps, as well as to set the current step, AKA moving the motor
  - style - Used for the changing of stepping style between "single", "double", "interleave", and "microstep"
  - kill - Kill the motor, allowing the axle to be turned freely
  - halt - Stops the motor's movement immediately, but does not release it

## Arduino Pins:
  This pin scheme is meant for the Arduino Uno, though it may work on other boards. 
  The only pins used are digital, so everybody listed below is assumed to be digital.
  - Pin 0 and 1:
    - Not used because let's not mess with serial communication pins
  - Pins 2 and 3:
    - Pin 2 is attached as an interrupt to update the encoder position 
      - The Arduino's loop function was not fast enough to read the encoder positions at the appropriate rate, so we have an ISR for updating the encoder position attached to this pin
    - A 5 kHz square wave from pin 8 triggers this interrupt
    - Pin 3 is not used currently, because interrupt pins are precious on the Uno
  - Pins 4 and 5: 
    - Read the waveforms for the two channels of encoder 0 (which is attached to motor 0)
  - Pins 6 and 7:
    - Do the same thing as pins 4 and 5 for encoder 1
  - Pin 8: 
    - Emits a 5 kHz square wave to trigger the ISR at pin 2
  - Pins 9, 10, 11, and 12:
    - Kill switches (2 per motor for each end of the motor's axis) are attached here
    - See the note below for more details
  - Pin 13:
    - Not used because we'd rather not mess with the LED if we don't have to

**A note about kill switches:**
  The pins for the kill switches use a pullup resistor that sets them at HIGH. Therefore, if a kill switch is not connected, the Arduino will fail-safe, and believe it is being killed. Not only is this terrifying and misleading message of imminent demise endangering the Arduino's mental health, it also prevents the motor from being moved. **Make sure to have all 4 kill switches attached, or else none of the motors will be able to move!**
  
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
