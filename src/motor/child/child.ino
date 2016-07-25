#include <EEPROM.h>
#include <Wire.h>
#include <Adafruit_MotorShield.h>
#include "utility/Adafruit_MS_PWMServoDriver.h"

// identity
String id = "";

// variables
int LED = 13;

// version number
String version_number = "0.5";

// encoder pins
int encoderA = 4;
int encoderAm = 6;
int encoderB = 5;
int encoderBm = 7;

// encoder position and previous encoder pin sum
volatile unsigned int encoderPos = 0;
int prevEncoderSum = 0;

// Hardware objects
Adafruit_MotorShield AFMS = Adafruit_MotorShield(); 
// Connect a stepper motor with 200 steps per revolution (1.8 degree)
// to motor port #1 (M1 and M2)
Adafruit_StepperMotor *motor = AFMS.getStepper(200, 1);

uint8_t current_style = SINGLE;
uint16_t default_speed = 60;

struct sym {
  String GET = "?";
  String SET = "!";
  String ANSWER = "$";
  String STREAM = ">";
  String ERROR = "@";
};

sym Symbol; // This and the other one below it is a bit hacky, but who cares

struct com {
  String ID = "id";
  String STEP = "step";
  String KILL = "kill";
  String SPEED = "speed";
  String VERSION = "version";
  String STYLE = "style";
  String HALT = "halt";
};

com Command;

struct dat {
  String NIL = "_";
};

dat Data;

bool erred = false;

// bool moving = false;
int steps_to_move = 0;

String readID() {
  char value;
  int address = 0;
  String id = "";
  while (true) { // loop
    value = EEPROM.read(address);
    
    if (value != 0 && byte(value) != 255) { // value is not null
      id += value;
    } else {
      break;
    }
    
    address++;
  }
  
  return id;
}

// the setup function runs once when you press reset or power the board
void setup() {
  Serial.begin(9600);
  pinMode(LED, OUTPUT);

  // setup encoder pins and turn on internal pull-up resistor
  pinMode(encoderA, INPUT);
  // digitalWrite(encoderA, LOW);

  pinMode(encoderB, INPUT);
  // digitalWrite(encoderB, HIGH);

  pinMode(encoderAm, INPUT);
  // digitalWrite(encoderAm, HIGH);

  pinMode(encoderBm, INPUT);
  // digitalWrite(encoderBm, HIGH);

  // initalize prevEncoderSum
//  prevEncoderSum = binaryToDecimal(digitalRead(encoderA), digitalRead(encoderB));

  id = readID();

  // Set up motor hardware
  AFMS.begin();
  motor->setSpeed(default_speed);
}

void updateMotorPos() {
  if (steps_to_move != 0) {

    // set direction 
    uint8_t dir = FORWARD;
    if (steps_to_move < 0) {
      dir = BACKWARD;
    }

    // move motor one step in the right direction
    motor->step(1, dir, current_style);

    // update steps_to_move
    if (dir == FORWARD) {
      steps_to_move --;
    } else if (dir == BACKWARD) {
      steps_to_move ++;
    }
  }
}

int binaryToDecimal(int a, int b) {
  return (a*2 + b*1);
}

void updateEncoderPos() {
  if (steps_to_move != 0) {
    if (steps_to_move < 0) {
      encoderPos --;
    } else {
      encoderPos ++;
    }
    Serial.println(join(Symbol.STREAM, Command.STEP, String(encoderPos)));
  } else if (encoderPos != 0) {
    encoderPos = 0;
  }
}

void updateEncoderPosCorrect() {
  int encoderSum = binaryToDecimal(digitalRead(encoderA), digitalRead(encoderB));

  if (encoderSum != prevEncoderSum) {
    switch(encoderSum) {
      case 1:
        if (prevEncoderSum == 0) {
          encoderPos ++;
        } else if (prevEncoderSum == 3) {
          encoderPos --;
        }
        break;
        
      case 0:
        if (prevEncoderSum == 2) {
          encoderPos ++;
        } else if (prevEncoderSum == 1) {
          encoderPos --;
        }
        break;
  
      case 2:
        if (prevEncoderSum == 3) {
          encoderPos ++;
        } else if (prevEncoderSum == 0) {
          encoderPos --;
        }
        break;
  
      case 3:
        if (prevEncoderSum == 1) {
          encoderPos ++;
        } else if (prevEncoderSum == 2) {
          encoderPos --;
        }
        break;
    }
    prevEncoderSum = encoderSum;
    Serial.println(join(Symbol.STREAM, Command.STEP, String(encoderPos)));  
  }
}

String join(String symbol, String command, String data) {
  return symbol + " " + command + " " + data;
}

// ----------------Getter Functions----------------

String getID() {
  return id;
}

String getVersion() {
  return version_number;
}

// ----------------Setter Functions----------------

String setID(String new_id) {
  for (int i = 0; i < new_id.length(); i++) {
    EEPROM.write(i, new_id[i]);
  }
  EEPROM.write(new_id.length(), 0);
  
  id = readID();
  return id;
}

// The below function supports only relative motion
String setStep(String distance, uint8_t style = current_style) {
  if (distance.toInt() % 1 != 0) {
    erred = true;
    return distance;
  }

  // set steps to move
  steps_to_move = distance.toInt();
  
  return distance;
}

String setKill() {
  motor->release();
  return Data.NIL;
}

String setStyle(String style) {
  if (style == "single") {
    current_style = SINGLE;
  }
  else if (style == "double") {
    current_style = DOUBLE;
  }
  else if (style == "interleave") {
    current_style = INTERLEAVE;
  }
  else if (style == "microstep") {
    current_style = MICROSTEP;
  }
  else {
    erred = true;
  }
}

String setHalt() {
  steps_to_move = 0;
  return Data.NIL;
}

void serialEvent() {
  if (Serial.available()) {
    String symbol = Serial.readStringUntil(' ');
    String command = Serial.readStringUntil(' ');
    String data = Serial.readStringUntil('\n');
    receivedMessage(symbol, command, data);
  }
}

void receivedMessage(String symbol, String command, String data) {
  // initializing strings for constructing a response
  String respond_symbol = Symbol.ERROR;
  String respond_command = command;
  String respond_data = Data.NIL;

  // if symbol is get
  if (symbol == Symbol.GET) {
    // contruct answer 
    respond_symbol = Symbol.ANSWER;
    
    if (command == Command.ID) {
      respond_data = getID();
    }
    else if (command == Command.VERSION) {
      respond_data = getVersion();
    } else {
      respond_symbol = Symbol.ERROR;
    }
  }
 
  // if symbol is set
  else if (symbol == Symbol.SET) {
    // construct response
    respond_symbol = Symbol.ANSWER;
    
    if (command == Command.ID) {
      respond_data = setID(data);
    }
    else if (command == Command.STEP) {
      respond_data = setStep(data);
    }
    else if (command == Command.SPEED) {
      motor->setSpeed(data.toInt()); //This function is already in the motor shield library
      respond_data = data;
    }
    else if (command == Command.KILL) {
      respond_data = setKill();
    } 
    else if (command == Command.STYLE) {
      respond_data = setStyle(data);
    }
    else if (command == Command.HALT) {
      // moving = false; // Method 2
      respond_data = setHalt(); // Method 1
    }
    else {
      respond_symbol = Symbol.ERROR;
    }
  }
  
  if (erred == true) {
    respond_symbol = Symbol.ERROR;
  }

  Serial.println(join(respond_symbol, respond_command, respond_data));
}

void loop() {
  updateMotorPos();
  updateEncoderPos();
}


