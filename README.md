# LabSight Development Plans

This will detail every subroutine that we need to write and the files in which we put them. There will be nothing functional in this repository.

For example, a planned function would look like this:

```python
def foo():
    # some description
    # of the function this routine will provide
```
## Proposed Files

The current assumption for these files is that they are allow you to control motors, in a manner similar to NI MAX. This means no support for dataruns or interface with oscilloscope. Functionality for multiple motors and dataruns will be added later.

(Note from Sam: The Controller Library should be built from the ground up to allow for multiple motors. It would be much harder to add this in at a later stage)

Any planned functions can be added to these files as is seen fit

### File List (in order of priority):

* child.ino
  - Supports every Arduino command of the protocol as outlined in the Google doc

* Controller.py
  - Based off of the current Controller.py
  - Conducts the serial communications, and contains the base functionality for all of the various protocol commands related to the controller
  - Communicates with the arduino, as well as ManualControl.py

* Main.py
  - Run this file to start the application
  - This holds all the constants and global variables
  - It saves and loads itself those variables on shutdown or when requested
  - Most importantly it knows the current position
  - Runs Setup.py if it hasn't been run already
  - This class can do all the unit conversions, according to the rates determined by the user during setup
  - Directs the user to the appropriate menu (probably ManualControl.py) when the program's initialization is done

* Setup.py
  - Asks for the user to define the calibration values:
    - Steps per centimeter and/or steps per radian
  - This will likely be a GUI class
  - *Later on, this file can be used to set up the different drives for dataruns, grouping them and specifying their ranges of motion*

* ManualControl.py
  - A GUI class that communicates with Controller.py, and provides NI-MAX functionality
  - It will ultimately manifest itself as a sidebar, but for now it will probably be the only GUI we have.
  - Features (which could possibly be translated into functions):
    - Motor Dashboard that indicates for each motor (in no particular order):
      - Has it been killed?
      - Is it moving?
      - Is it ready?
      - Has an error occurred?
    - Movement (which can be converted between centimeters or steps, using the functions of Main.py)
      - Relative motion
      - Absolute motion
      - Requests for movement are then sent to Controller.py
    - Setting the origin
      - This information is then stored in the global variables from Main.py
    - Changing the motor's speed
    - *Eventually, you'll be able to change between motors*
