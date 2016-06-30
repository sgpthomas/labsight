/* Includes */
#include <EEPROM.h>

/* Global Variables */
String id = ""; // stores id of this
int LED = 13;  // which LED should be flashed as an indicator

/* Built-in Arduino Routines that we need */
void setup() {
    /* 
    Sets up everything

    - Start Serial
    - Setup Pins
        - Led
        - Interrupt pin for stop switch
        - Motor Pins (if we need to do this with the library)
        - Encoder Pins
    - Remember ID if there is one set
    - Attach interrupt for Stop Switch `attachInterrupt(interrupt, function, mode);`

    */
}

void serialEvent() {
    /*
    This method fires every time something is put into the Serial Message Boad. We will
    use as the starting point for most things. One thing to note here is that reading
    from the message board destroys the message.

    - Make sure Serial is available
    - Decide if this should read message (might not want to if sending a stream)
    - If should read message, parse message and send it to `void processMessage(String symbol, String command, String info)`
     
    */
}

void loop() {
    /*
    Nothing here yet

    */
}

/* Custom Routines that we need */
String rememberID() {
    /*
    Read EEPROM to see if there is already an ID set. If there is one, return the ID String,
    else, return an empty String

    */
}

void clearMemory() {
    /*
    Goes through every byte in EEPROM and sets it to 0

    */
}

void processMessage(String symbol, String command, String info) {
    /*
    Proccess message and take necessary steps

    TODO: Figure out an efficient way to process messages and do necessary things
    */
}

/* Setters and Getters for all Global Variables */
// id
void set_id(String id) {
    /*
    Clears memory, writes given string into EEPROM, and then sets global id to given string

    */
}

String get_id() {
    /*
    Returns global id

    */
}

// led
void set_led(int pin) {
    /*
    Sets Global led pin

    */
}

int get_led(int pin) {
    /*
    Returns Global led pin

    */
}
