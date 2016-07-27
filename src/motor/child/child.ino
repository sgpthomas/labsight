#include <EEPROM.h>
#include <Wire.h>
#include <Adafruit_MotorShield.h>
#include "utility/Adafruit_MS_PWMServoDriver.h"

// version number
String version_number = "0.6";

// identity
String id0 = "";
String id1 = "";

// encoder pins for motor 1
int encoderA0 = 2;
int encoderB0 = 3;

// encoder pins for motor 2
int encoderA1 = 4;
int encoderB1 = 5;

// encoder position and previous encoder pin sum
int encoderPos0 = 0;
int prevEncoderSum0 = 0;

int encoderPos1 = 0;
int prevEncoderSum1 = 0;

// Hardware objects
Adafruit_MotorShield AFMS = Adafruit_MotorShield(); 
// Connect a stepper motor with 200 steps per revolution (1.8 degree)
// to motor port #1 (M1 and M2)
Adafruit_StepperMotor *motor0 = AFMS.getStepper(200, 1);
Adafruit_StepperMotor *motor1 = AFMS.getStepper(200, 2);

uint8_t style0 = SINGLE;
uint16_t default_speed = 60;

uint8_t style1 = SINGLE;

struct sym {
  String GET = "?";
  String SET = "!";
  String ANSWER = "$";
  String STREAM = ">";
  String ERROR = "@";
};

sym Symbol; // This and the other one below it is a bit hacky, but who cares

struct mot {
  String ZERO = "0";
  String ONE = "1";
};

mot MOTOR;

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

int steps_to_move0 = 0;
int steps_to_move1 = 0;

String queue_response = "";

String readID(String motor_index = Motor.ZERO) {
  char value;
  int address = 0;
  if (motor_index == Motor.ONE) {
    address += 511;
  }
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

void setup() {
  Serial.begin(9600);

  // setup encoder pins
  pinMode(encoderA1, INPUT);
  pinMode(encoderB1, INPUT);

  pinMode(encoderA2, INPUT);
  pinMode(encoderB2, INPUT);

  id = readID();

  // Set up motor hardware
  AFMS.begin();
  motor1->setSpeed(default_speed);
  motor2->setSpeed(default_speed);
}

void updateMotorPos(String motor_index = "0") {
  uint8_t dir;
  uint8_t style;
  int steps_to_move;
  Adafruit_StepperMotor *motor;

  // This sets the variable for the given motor
  if (motor_index == MOTOR.ZERO) {
    steps_to_move = steps_to_move0;
    motor = motor0;
    style = style0;
  } else if (motor_index == MOTOR.ONE) {
    steps_to_move = steps_to_move1;
    motor = motor1;
    style = style1;
  }
  if (steps_to_move != 0) {
    // set direction 
    dir = FORWARD;
    if (steps_to_move < 0) {
      dir = BACKWARD;
    }

    // move motor one step in the right direction
    motor->step(1, dir, style);

    // update steps_to_move1
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

// This function's kinda broken now that there are multiple motors
void updateEncoderPosFake() {
  if (steps_to_move1 != 0) {
    if (steps_to_move1 < 0) {
      encoderPos1 --;
    } else {
      encoderPos1 ++;
    }
    Serial.println(join(Symbol.STREAM, Command.STEP, String(encoderPos1)));
  } else if (encoderPos1 != 0) {
    encoderPos1 = 0;
  }
}

void updateEncoderPos(String motor_index = Motor.ZERO) {
//  if (steps_to_move1 != 0) {
  int encoderSum;
  int prevEncoderSum;
  int deltaEncoderPos = 0;

  if (motor_index == Motor.ZERO) {
    encoderSum = binaryToDecimal(digitalRead(encoderPinA1), digitalRead(encoderPinB1));
    prevEncoderSum = prevEncoderSum1;
  } else if (motor_index = Motor.ONE) {
    encoderSum = binaryToDecimal(digitalRead(encoderPinA2), digitalRead(encoderPinB2));
    prevEncoderSum = prevEncoderSum2;
  }
  if (encoderSum != prevEncoderSum) {
    switch(encoderSum) {
      case 1:
        if (prevEncoderSum == 0) {
          deltaEncoderPos ++;
        } else if (prevEncoderSum == 3) {
          deltaEncoderPos --;
        }
        break;
        
      case 0:
        if (prevEncoderSum == 2) {
          deltaEncoderPos ++;
        } else if (prevEncoderSum == 1) {
          deltaEncoderPos1 --;
        }
        break;
  
      case 2:
        if (prevEncoderSum1 == 3) {
          deltaEncoderPos ++;
        } else if (prevEncoderSum == 0) {
          deltaEncoderPos --;
        }
        break;
  
      case 3:
        if (prevEncoderSum == 1) {
          deltaEncoderPos ++;
        } else if (prevEncoderSum == 2) {
          deltaEncoderPos --;
        }
        break;
    }
    if (motor_index == Motor.ZERO) {
      encoderPos0 += deltaEncoderPos;
      prevEncoderSum0 = encoderSum;
    } else if (motor_index == Motor.ONE) {
      encoderPos1 += deltaEncoderPos;
      prevEncoderSum1 = encoderSum;
    }
//      Serial.println(join(Symbol.STREAM, Command.STEP, String(encoderPos1) + " " + String(steps_to_move1) + " " + String(digitalRead(encoderA1)) + String(digitalRead(encoderB1))));
    Serial.println(join(Symbol.STREAM, motor_index, Command.STEP, String(deltaEncoderPos)));
  }
//  } else if (encoderPos1 != 0) {
//    encoderPos1 = 0;
//  }
}

String join(String symbol, String motor, String command, String data) {
  return symbol + " " motor + " " + command + " " + data;
}

// ----------------Getter Functions----------------

String getID(String motor_index = Motor.ZERO) {
  switch(int(motor_index)) {
    case 0:
      return id0;
      break;
    case 1:
      return id1;
      break;
  }
}

String getVersion() {
  return version_number;
}

// ----------------Setter Functions----------------

String setID(String motor_index = Motor.ZERO, String new_id) {
  int start_index = 0;
  if (motor_index == Motor.ONE) {
    start_index += 511;
    id1 = new_id
  } else if (motor_index == Motor.ZERO) {
    id0 = new_id;
  }
  for (int i = start_index; i < new_id.length(); i++) {
    EEPROM.write(i, new_id[i]);
  }
  EEPROM.write(start_index + new_id.length(), 0);
  
  return readID(motor_index);
}

// The below function supports only relative motion
String setStep(String motor_index = Motor.ZERO, String distance) {
  if (distance.toInt() % 1 != 0) {
    erred = true;
    return distance;
  }

  // set steps to move and add one so that it actually moves the right number of steps
  int steps_to_move = distance.toInt() + (distance.toInt() / abs(distance.toInt()));
  if (motor_index == Motor.ZERO) {
    steps_to_move0 = steps_to_move;
  } else if (motor_index == Motor.ONE) {
    steps_to_move1 = steps_to_move;
  }
  
  return distance;
}

String setKill(String motor_index = Motor.ZERO) {
  motor1->release();
  return Data.NIL;
}

String setStyle(String style) {
  if (style == "single") {
    style1 = SINGLE;
  }
  else if (style == "double") {
    style1 = DOUBLE;
  }
  else if (style == "interleave") {
    style1 = INTERLEAVE;
  }
  else if (style == "microstep") {
    style1 = MICROSTEP;
  }
  else {
    erred = true;
  }
  return style;
}

String setHalt(String motor_index = Motor.ZERO) {
  steps_to_move1 = 0;
  return Data.NIL;
}

String setRate(String motor_index = Motor.Zero, String data) {
  motor[motor_index.toInt()]->setSpeed(data.toInt());
  return data;
}



void serialEvent() {
  if (Serial.available()) {
    String symbol = Serial.readStringUntil(' ');
    String motor = Serial.readStringUntil(' ');
    String command = Serial.readStringUntil(' ');
    String data = Serial.readStringUntil('\n');
    receivedMessage(symbol, motor, command, data);
  }
}

void receivedMessage(String symbol,String motor, String command, String data) {
  // initializing strings for constructing a response
  String respond_symbol = Symbol.ERROR;
  String respond_motor = motor;
  String respond_command = command;
  String respond_data = Data.NIL;

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
      respond_data = setID(motor,data);
    }
    else if (command == Command.STEP) {
      respond_data = setStep(motor,data);
    }
    else if (command == Command.SPEED) {
      respond_data = setRate(motor, data) //This function is already in the motor shield library
      respond_data = data;
    }
    else if (command == Command.KILL) {
      respond_data = setKill();
    } 
    else if (command == Command.STYLE) {
      respond_data = setStyle(data);
    }
    else if (command == Command.HALT) {
      respond_data = setHalt();
    }
    else {
      respond_symbol = Symbol.ERROR;
    }
  }
  
  if (erred == true) {
    respond_symbol = Symbol.ERROR;
  }

  String response = join(respond_symbol, respond_command, respond_data);

  if (steps_to_move1 != 0) {
    queue_response = response;
  } else {
    Serial.println(response);
  }
}

void loop() {
  updateMotorPos(motor[0]);
  updateMotorPos(motor[1]);
  
  updateEncoderPos(motor[0]);
  updateEncoderPos(motor[1]);
  
  if (steps_to_move1 == 0 && queue_response != "") {
    Serial.println(queue_response);
    queue_response = "";
  }
}


