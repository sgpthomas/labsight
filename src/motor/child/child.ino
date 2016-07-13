#include <EEPROM.h>
#include <AFMotor.h>

// identity
String id = "";

// variables
int LED = 13;

// version number
String version_number = "0.1";

// is streaming?
bool stream = false;

// encoder pins
int encoderA = 2;
int encoderB = 3;

// encoder position and previous encoder pin sum
volatile unsigned int encoderPos = 0;
int prevEncoderSum = 0;

// I tried to implement these structs like the classes, in protocol.py, but they didn't work, so I ended up hardcoding everything. Feel free to try t make them work if you'd like

struct sym {
  String GET = "?";
  String SET = "!";
  String ANSWER = "$";
  String OPEN_STREAM = ">";
  String CLOSE_STREAM = "/";
};

sym Symbol; // This and the other one below it is a bit hacky, but who cares

struct com {
  String ID = "id";
  String STEP = "step";
  String KILL = "kill";
  String SPEED = "speed";
  String VERSION = "version";
};

com Command;

String rememberID() {
  char value;
  int address = 0;
  String id = "";
  while (true) { // loop
    value = EEPROM.read(address);
    
    if (value != 0) { // value is not null
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
  digitalWrite(encoderA, HIGH);

  pinMode(encoderB, INPUT);
  digitalWrite(encoderB, HIGH);

  // attach interrupt to keep track of position
  attachInterrupt(digitalPinToInterrupt(encoderA), updateEncoderPos, CHANGE);
  attachInterrupt(digitalPinToInterrupt(encoderB), updateEncoderPos, CHANGE);

  // initalize prevEncoderSum
  prevEncoderSum = binaryToDecimal(digitalRead(encoderA), digitalRead(encoderB));
  
  id = rememberID();

int binaryToDecimal(int a, int b) {
  return (a*2 + b*1);
}

void updateEncoderPos() {
  int encoderSum = binaryToDecimal(digitalRead(encoderA), digitalRead(encoderB));

  switch(encoderSum) {
    case 1:
      if (prevEncoderSum == 3) {
        encoderPos ++;
      } else {
        encoderPos --;
      }
      break;
      
    case 0:
      if (prevEncoderSum == 1) {
        encoderPos ++;
      } else {
        encoderPos --;
      }
      break;

    case 2:
      if (prevEncoderSum == 0) {
        encoderPos ++;
      } else {
        encoderPos --;
      }
      break;

    case 3:
      if (prevEncoderSum == 2) {
        encoderPos ++;
      } else {
        encoderPos --;
      }
      break;
  }

  Serial.println(encoderPos);
}

  // Set up the motor shield object
  Adafruit_MotorShield AFMS = Adafruit_MotorShield();

  // Set up stepper motor object
  Adafruit_StepperMotor *motor = AFMS.getStepper(Steps_per_revolution, Motor_Shield_Port);
  // Those 2 arguments need to be set to something
  // Also, the asterisk means this variable is just a pointer. I don't why it's worth doing that, but it's what the library reference did.
}

String join(String symbol, String command, String data) {
  return symbol + " " + command + " " + data;
}

// ----------------Getter Functions----------------

void getID() {
  Serial.println(join(Symbol.SET, Command.ID, id));
}

void getVersion() {
  Serial.println(join(Symbol.SET, Command.VERSION, version_number));
}

// ----------------Setter Functions----------------

void setID(String id) {
  clearMem();
  for (int i = 0; i < id.length(); i++) {
    EEPROM.write(i, id[i]);
  }
  Serial.println(join(Symbol.ANSWER, Command.ID, id));
}

void setVersion(String data) { // Does this need to write the version to EEPROM? Why write the ID, and not the version?
  version_number = data;
  Serial.println(join(Symbol.SET, Command.VERSION, version_number));
}


// The below function supports only relative motion
void setStep(String distance) {
   stream = true;
   Serial.println(join(Symbol.OPEN_STREAM, Command.STEP, distance));
   if (distance.toInt() > 0) {
     uint8_t direction = FORWARD;
   }
   else if (distance < 0) {
     uint8_t direction = BACKWARD;
   }
   else {
    return;
   }
   for (int i = 0; i < distance.toInt(); i++) {
     motor.step(1, direction);
     Serial.println(i);
     //delay(200);
   }
   Serial.println(join(Symbol.CLOSE_STREAM, Command.STEP, distance));
   stream = false;
}

void setKill() {
  motor.release();
  Serial.println(join(Symbol.SET, Command.KILL, "_")); //There's got to be something better to put into the data slot than "_"
}

void clearMem() {
  for (int i = 0 ; i < EEPROM.length() ; i++) {
    EEPROM.write(i, 0);
  }  
}

void updateEncoderPos() {
}

void serialEvent() {
  if (Serial.available() && !stream) {
    String symbol = Serial.readStringUntil(' ');
    String command = Serial.readStringUntil(' ');
    String data = Serial.readStringUntil('\n');
    receivedMessage(symbol, command, data);
    // digitalWrite(LED, HIGH);
    // delay(500);
    // digitalWrite(LED, LOW);
  }
}

void receivedMessage(String symbol, String command, String data) {  
  if (symbol == Symbol.GET) {
    if (command == Command.ID) {
      getID();
    }
    else if (command == Command.VERSION) {
      getVersion();
    }
//      All of these cases below are probably unnecessary, as the controller can do it for the Arduino:
//      (Also, I know switch cases won't work here, just imagine they're if statements)
//      case "step":
//        getStep();
//        break;
//      case "speed":
//        getSpeed();
//        break;
//      case "kill":
//        getKill(); // I don't know if it's possible to implemetn this function, or worth doing when the controller can do it anyway
//        break;
     else {
        // Send some error message about an incoherent command. This can be defined as a function as well
    }
  }
    
  
  else if (symbol == Symbol.SET) {
    if (command == Command.ID) {
      setID(data);
    }
    else if (command == Command.VERSION) {
      setVersion(data);
    }
    else if (command == Command.STEP) {
      setStep(data);
    }
    else if (command == Command.SPEED) {
      setSpeed(data); //This function is already in the motor shield library
    }
    else if (command == Command.KILL) {
        setKill();
    }
    else {
      // Send some error message about an incoherent command
    }
  }
}
int address = 0;
byte value;
boolean l = true;

void loop() {

}


