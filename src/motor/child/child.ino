#include <EEPROM.h>
#include <Wire.h>
#include <Adafruit_MotorShield.h>
#include "utility/Adafruit_MS_PWMServoDriver.h"

// Standardize to camelCase and/or snake_case please!!
// A few more setter and getter functions
//  Remember to add all this to motor.py
//    - encoderStepsPerMotorStep [DONE]
//    - followingErrorTolerance [DONE]
//    - encoderSamplingFrequency [DONE]
//    - Possibly deimplement speed [X]
//    - getStep [DONE]


// version number
String version_number = "0.8";

// identity
String id = "";

float encoderStepsPerMotorStep = 2.0;
int followingErrorTolerance = 10.0;
int encoderSamplingFrequency = 5000;

// encoder pins for motor 1
int encoderPinA[2] = {4, 6};
int encoderPinB[2] = {5, 7};

// the motors' believed internal position
int motorPos[2] = {0, 0};

// encoder position and previous encoder pin sum
int encoderPos[2] = {0, 0};
int prevEncoderSum[2] = {0, 0};

// Hardware objects
Adafruit_MotorShield AFMS = Adafruit_MotorShield();
// Adafruit_StepperMotor *motor0 = ;
// Adafruit_StepperMotor *motor1 = ;
Adafruit_StepperMotor *motor[2] = {AFMS.getStepper(200, 1), AFMS.getStepper(200, 2)};

// default motor settings
uint8_t style[2] = {SINGLE, SINGLE};
uint16_t default_speed = 60;

// motor movement variables
int steps_to_move[2] = {0, 0};
String queue_response[2] = {"", ""};

// for sending errors
bool erred = false;
// to stop the kill error from spamming
bool killed = false;
/* Hacky Enums */
struct sym {
  String GET = "?";
  String SET = "!";
  String ANSWER = "$";
  String STREAM = ">";
  String ERROR = "@";
};
sym Symbol;

struct mot {
  String NIL = "_";
  String ZERO = "0";
  String ONE = "1";
};
mot MotorIndex;

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

struct err {
  String TRANSITION = "transition";
  String FOLLOWING = "following";
};
err Error;

String join(String symbol, String motor, String command, String data) {
  return symbol + " " + motor + " " + command + " " + data;
}

int len = (sizeof(motor) / sizeof(motor[0]));

int binaryToDecimal(int a, int b) {
  return (a * 2 + b * 1);
}

/* ----------------Update Functions---------------- */

void updateMotorPos(String motor_stringdex) {
  uint8_t dir;
  int motor_index = motor_stringdex.toInt();
  // set direction
  if (steps_to_move[motor_index] != 0) {
    dir = FORWARD;
    if (steps_to_move[motor_index] < 0) {
      dir = BACKWARD;
    }
    // move motor one step in the right direction
    motor[motor_index]->step(1, dir, style[motor_index]);
    // update steps_to_move
    if (dir == FORWARD) {
      steps_to_move[motor_index] --;
      motorPos[motor_index] ++;
    } else if (dir == BACKWARD) {
      steps_to_move[motor_index] ++;
      motorPos[motor_index] --;
    }
  }
}

bool moved[2] = {false,false};
bool transitionError[2] = {false,false};

// This is the interrupt service routine
void updateEncoderPos(String motor_stringdex) {
  // This ISR takes 20 microseconds to execute
  //  digitalWrite(9, HIGH);
  //  digitalWrite(9, LOW);
  //  digitalWrite(9, HIGH);
  //  digitalWrite(9, LOW);
  for (int motor_index = 0; motor_index < len ; motor_index++) {
    //    int motor_index = motor_stringdex.toInt();
    // if (steps_to_move[motor_index] != 0) {
    int deltaEncoderPos = 0;
    int encoderSum = binaryToDecimal(digitalRead(encoderPinA[motor_index]), digitalRead(encoderPinB[motor_index]));
    if (encoderSum != prevEncoderSum[motor_index]) {
      moved[motor_index] = true;
      switch (encoderSum) {
        case 1:
          if (prevEncoderSum[motor_index] == 3) {
            deltaEncoderPos ++;
          } else if (prevEncoderSum[motor_index] == 0) {
            deltaEncoderPos --;
          }
          break;

        case 0:
          if (prevEncoderSum[motor_index] == 1) {
            deltaEncoderPos ++;
          } else if (prevEncoderSum[motor_index] == 2) {
            deltaEncoderPos --;
          }
          break;

        case 2:
          if (prevEncoderSum[motor_index] == 0) {
            deltaEncoderPos ++;
          } else if (prevEncoderSum[motor_index] == 3) {
            deltaEncoderPos --;
          }
          break;

        case 3:
          if (prevEncoderSum[motor_index] == 2) {
            deltaEncoderPos ++;
          } else if (prevEncoderSum[motor_index] == 1) {
            deltaEncoderPos --;
          }
          break;
      }
      if (deltaEncoderPos == 0) {
        transitionError[motor_index] = true;
      }
      encoderPos[motor_index] += deltaEncoderPos;
      prevEncoderSum[motor_index] = encoderSum;
    } //else if (encoderPos[motor_index] != 0) {
    //  encoderPos[motor_index] = 0;
    //}
  }// digitalWrite(9, LOW);
}

/* -----------------Misc Functions----------------- */

String readID() {
  char value;
  int address = 0;
  String reading_id = "";
  while (true) { // loop
    value = EEPROM.read(address);

    if (value != 0 && byte(value) != 255) { // value is not null
      reading_id += value;
    } else {
      break;
    }

    address++;
  }

  return reading_id;
}

/* ----------------Getter Functions---------------- */

String getID(String motor_stringdex) {
  return id + "_" + motor_stringdex;
}

String getVersion() {
  return version_number;
}

String getStep(String motor_stringdex) {
  return String(int(encoderPos[motor_stringdex.toInt()]/encoderStepsPerMotorStep));
}

/* ----------------Setter Functions---------------- */

String setID(String new_id) {
  int start_index = 0;

  for (int i = 0; i < new_id.length(); i++) {
    EEPROM.write(i + start_index, new_id[i]);
  }
  EEPROM.write(start_index + new_id.length(), 0);
  return readID();
}

// The below function supports only relative motion
String setStep(String distance, String motor_stringdex) {
  if (distance.toInt() % 1 != 0) {
    erred = true;
    return distance;
  }

  // sets steps to move and adds one so that it actually moves the right number of steps
  steps_to_move[motor_stringdex.toInt()] = distance.toInt() + (distance.toInt() / abs(distance.toInt()));

  return distance;
}

String setKill(String motor_stringdex) {
  motor[motor_stringdex.toInt()]->release();
  return Data.NIL;
}

String setStyle(String new_style, String motor_stringdex) {
  int motor_index = motor_stringdex.toInt();
  if (new_style == "single") {
    style[motor_index] = SINGLE;
  }
  else if (new_style == "double") {
    style[motor_index] = DOUBLE;
  }
  else if (new_style == "interleave") {
    style[motor_index] = INTERLEAVE;
  }
  else if (new_style == "microstep") {
    style[motor_index] = MICROSTEP;
  }
  else {
    erred = true;
  }
  return new_style;
}

String setHalt(String motor_stringdex) {
  steps_to_move[motor_stringdex.toInt()] = 0;
  return Data.NIL;
}

// setSpeed may not work right now
String setRate(String data, String motor_stringdex) {
  motor[motor_stringdex.toInt()]->setSpeed(data.toInt());
  return data;
}

// Handles receiving messages from the arduino
void receivedMessage(String symbol, String motor, String command, String data) {
  // initializing strings for constructing a response
  String respond_symbol = Symbol.ERROR;
  String respond_motor = motor;
  String respond_command = command;
  String respond_data = data;

  // if symbol is get
  if (symbol == Symbol.GET) {
    // contruct answer
    respond_symbol = Symbol.ANSWER;

    if (command == Command.ID) {
      respond_data = getID(motor);
    }
    else if (command == Command.VERSION) {
      respond_data = getVersion();
    }
    else if (command == Command.STEP) {
      respond_data = getStep(motor);
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
      respond_data = setStep(data, motor);
    }
    else if (command == Command.SPEED) {
      respond_data = setRate(data, motor);
    }
    else if (command == Command.KILL) {
      respond_data = setKill(motor);
    }
    else if (command == Command.STYLE) {
      respond_data = setStyle(data, motor);
    }
    else if (command == Command.HALT) {
      respond_data = setHalt(motor);
    }
    else {
      respond_symbol = Symbol.ERROR;
    }
  }

  if (erred == true) {
    respond_symbol = Symbol.ERROR;
  }

  String response = join(respond_symbol, respond_motor, respond_command, respond_data);

  if (steps_to_move[respond_motor.toInt()] != 0) {
    queue_response[respond_motor.toInt()] = response;
  } else {
    Serial.println(response);
  }
}

/* ------------Default Arduino Functions------------ */
void setup() {
  Serial.begin(9600);

  // setup encoder pins
  pinMode(encoderPinA[1], INPUT);
  pinMode(encoderPinB[1], INPUT);

  pinMode(encoderPinA[2], INPUT);
  pinMode(encoderPinB[2], INPUT);

//Debugging stuff for the oscilloscope
//  pinMode(8, OUTPUT);
//  pinMode(9, OUTPUT);

// Kill switches
  pinMode(9, INPUT_PULLUP);  // Motor 0 - kill witch
  pinMode(10, INPUT_PULLUP); // Motor 0 + kill switch
  pinMode(11, INPUT_PULLUP); // Motor 1 - Kill switch
  pinMode(12, INPUT_PULLUP); // Motor 1 + kill switch

  //Interrupts
  attachInterrupt(digitalPinToInterrupt(2), updateEncoderPos, RISING);
//  attachInterrupt(digitalPinToInterrupt(3), updateEncoderPos, RISING);
  // Attach the interrupt pin to a 5 kHz signal
  tone(8, encoderSamplingFrequency);
// This frequency should be adequate for 10 revolutions per second on the motor (oversampling x2)

  // read the ids from eeprom
  id = readID();

  // Set up motor hardware
  AFMS.begin();
  motor[0]->setSpeed(default_speed);
  motor[1]->setSpeed(default_speed);
}

int encoderPosInUnitsOfMotorStep;

void loop() {
  // loop through motor arrays
  for (int i = 0; i < len; i++) {
    updateMotorPos(String(i));
    encoderPosInUnitsOfMotorStep = int(encoderPos[i] / encoderStepsPerMotorStep);

    if (moved[i]) {
      Serial.println(join(Symbol.STREAM, String(i), Command.STEP, String(encoderPosInUnitsOfMotorStep)));
      moved[i] = false;
    }
    if (transitionError[i]) {
      Serial.println(join(Symbol.ERROR, String(i), Error.TRANSITION, String(encoderPosInUnitsOfMotorStep)));
      transitionError[i] = false;
    }
    if (steps_to_move[i] != 0) {
      if (abs(motorPos[i]-encoderPosInUnitsOfMotorStep) > followingErrorTolerance) {
        Serial.println(join(Symbol.ERROR, String(i), Error.FOLLOWING, String(encoderPosInUnitsOfMotorStep)));
        motorPos[i] = encoderPos[i];
      }
    }
    if (steps_to_move[i] == 0 && queue_response[i] != "") {
      Serial.println(queue_response[i]);
      queue_response[i] = "";
    }
  }
//  Check kill switch pins:
//   The Arduino will not work without a grounded kill switch attached!!
//  if (digitalRead(9) == HIGH || digitalRead(10) == HIGH) {
//    setHalt("0");
//    if (!killed) {
//      Serial.println(join(Symbol.ERROR, "0", Command.HALT, String(int(encoderPos[0] / encoderStepsPerMotorStep))));
//      killed = true;
//    }
//  }
//  else if (digitalRead(11) == HIGH || digitalRead(12) == HIGH) {
//    setHalt("1");
//    if (!killed) {
//      Serial.println(join(Symbol.ERROR, "1", Command.HALT, String(encoderPos[1] / encoderStepsPerMotorStep)));
//      killed = true;
//    }
//  } else if (killed) {
//    killed = false;
//  }
}

//void serialLoop () {
//}

// fires every time we get a serial event. Parses incoming message and passes it on to receivedMessage()
void serialEvent() {
  if (Serial.available()) {
    String symbol = Serial.readStringUntil(' ');
    String motor = Serial.readStringUntil(' ');
    String command = Serial.readStringUntil(' ');
    String data = Serial.readStringUntil('\n');
    receivedMessage(symbol, motor, command, data);
  }
}
