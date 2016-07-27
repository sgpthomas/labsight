#include <EEPROM.h>
#include <Wire.h>
#include <Adafruit_MotorShield.h>
#include "utility/Adafruit_MS_PWMServoDriver.h"

// version number
String version_number = "0.6";

// identity
String id[2] = {"", ""};

// encoder pins for motor 1
int encoderPinA[2] = {2, 4};
int encoderPinB[2] = {3, 5};

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
mot Motor;

struct com {
  String NIL = "_";
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

/* ----------------Update Functions---------------- */

void updateMotorPos(String motor_stringdex) {
  uint8_t dir;
  int motor_index = motor_stringdex.toInt();

  if (steps_to_move[motor_index] != 0) {
    // set direction 
    dir = FORWARD;
    if (steps_to_move[motor_index] < 0) {
      dir = BACKWARD;
    }

    // move motor one step in the right direction
    motor[motor_index]->step(1, dir, style[motor_index]);

    // update steps_to_move
    if (dir == FORWARD) {
      steps_to_move[motor_index] --;
    } else if (dir == BACKWARD) {
      steps_to_move[motor_index] ++;
    }
    Serial.println(join(Symbol.STREAM, motor_stringdex, Command.STEP, String(steps_to_move[motor_index])));
  }
}

// This function's kinda broken now that there are multiple motors
//void updateEncoderPosFake() {
//  if (steps_to_move1 != 0) {
//    if (steps_to_move1 < 0) {
//      encoderPos1 --;
//    } else {
//      encoderPos1 ++;
//    }
//    Serial.println(join(Symbol.STREAM, Command.STEP, String(encoderPos1)));
//  } else if (encoderPos1 != 0) {
//    encoderPos1 = 0;
//  }
//}

void updateEncoderPos(String motor_stringdex) {
  int motor_index = motor_stringdex.toInt();
//  if (steps_to_move1 != 0) {
  int deltaEncoderPos = 0;
  int encoderSum = binaryToDecimal(digitalRead(encoderPinA[motor_index]), digitalRead(encoderPinB[motor_index]));
  if (encoderSum != prevEncoderSum[motor_index]) {
    switch(encoderSum) {
      case 1:
        if (prevEncoderSum[motor_index] == 0) {
          deltaEncoderPos ++;
        } else if (prevEncoderSum[motor_index] == 3) {
          deltaEncoderPos --;
        }
        break;
        
      case 0:
        if (prevEncoderSum[motor_index] == 2) {
          deltaEncoderPos ++;
        } else if (prevEncoderSum[motor_index] == 1) {
          deltaEncoderPos --;
        }
        break;
  
      case 2:
        if (prevEncoderSum[motor_index] == 3) {
          deltaEncoderPos ++;
        } else if (prevEncoderSum[motor_index] == 0) {
          deltaEncoderPos --;
        }
        break;
  
      case 3:
        if (prevEncoderSum[motor_index]== 1) {
          deltaEncoderPos ++;
        } else if (prevEncoderSum[motor_index] == 2) {
          deltaEncoderPos --;
        }
        break;
    }
    encoderPos[motor_index] += deltaEncoderPos;

//      Serial.println(join(Symbol.STREAM, Command.STEP, String(encoderPos1) + " " + String(steps_to_move1) + " " + String(digitalRead(encoderA1)) + String(digitalRead(encoderB1))));
    Serial.println(join(Symbol.STREAM, String(motor_index), Command.STEP, String(deltaEncoderPos)));
  }
//  } else if (encoderPos1 != 0) {
//    encoderPos1 = 0;
//  }
}

/* -----------------Misc Functions----------------- */

String join(String symbol, String motor, String command, String data) {
  return symbol + " " + motor + " " + command + " " + data;
}

int binaryToDecimal(int a, int b) {
  return (a*2 + b*1);
}

String readID(String motor_index) {
  char value;
  int address = 0;
  if (motor_index == Motor.ONE) {
    address += 511;
  }
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
  return id[motor_stringdex.toInt()];
}

String getVersion() {
  return version_number;
}

/* ----------------Setter Functions---------------- */

String setID(String new_id, String motor_stringdex) {
  int start_index = 0;
  if (motor_stringdex == Motor.ONE) {
    start_index += 511;
    id[1] = new_id;
  } else if (motor_stringdex == Motor.ZERO) {
    id[0] = new_id;
  }
  for (int i = 0; i < new_id.length(); i++) {
    EEPROM.write(i + start_index, new_id[i]);
  }
  EEPROM.write(start_index + new_id.length(), 0);
  Serial.println(readID(motor_stringdex));
  return readID(motor_stringdex);
}

// The below function supports only relative motion
String setStep(String distance, String motor_stringdex = Motor.ZERO) {
  if (distance.toInt() % 1 != 0) {
    erred = true;
    return distance;
  }

  // set steps to move and add one so that it actually moves the right number of steps
  steps_to_move[motor_stringdex.toInt()] = distance.toInt() + (distance.toInt() / abs(distance.toInt()));
  
  return distance;
}

String setKill(String motor_stringdex = Motor.ZERO) {
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

String setHalt(String motor_stringdex = Motor.ZERO) {
  steps_to_move[motor_stringdex.toInt()] = 0;
  return Data.NIL;
}

String setRate(String data, String motor_stringdex = Motor.ZERO) {
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
    } else {
      respond_symbol = Symbol.ERROR;
    }
  }
 
  // if symbol is set
  else if (symbol == Symbol.SET) {
    // construct response
    respond_symbol = Symbol.ANSWER;
    
    if (command == Command.ID) {
      respond_data = setID(data, motor);
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

  // read the ids from eeprom
  id[0] = readID(Motor.ZERO);
  id[1] = readID(Motor.ONE);

  // Set up motor hardware
  AFMS.begin();
  motor[0]->setSpeed(default_speed);
  motor[1]->setSpeed(default_speed);
}

void loop() {
  // loop through motor arrays
  for (int i = 0; i < (sizeof(motor) / sizeof(motor[0])); i++) {
    updateMotorPos(String(i));
    updateEncoderPos(String(i));
    
    if (steps_to_move[i] == 0 && queue_response[i] != "") {
      Serial.println(queue_response[i]);
      queue_response[i] = "";
    }
  }
}

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

