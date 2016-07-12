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
int encoderB = 4;

// encoder position
volatile unsigned int encoderPos = 0;

// I tried to implement these structs like the classes, in protocol.py, but they didn't work, so I ended up hardcoding everything. Feel free to try t make them work if you'd like

struct Symbol {
  String GET = "?";
  String SET = "!";
  String ANSWER = "$";
  String OPEN_STREAM = ">";
  String CLOSE_STREAM = "/";
};

struct Command {
  String ID = "id";
  String STEP = "step";
  String KILL = "kill";
  String SPEED = "speed";
  String VERSION = "version";
};

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
  
  id = rememberID();

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
  Serial.println(join("$", "id", id));
}

void getVersion() {
  Serial.println(join("$", "version", version_number));
}

// ----------------Setter Functions----------------

void setID(String id) {
  clearMem();
  for (int i = 0; i < id.length(); i++) {
    EEPROM.write(i, id[i]);
  }
  Serial.println(join("$", "id", id));
}

void setVersion(String data) { // Does this need to write the version to EEPROM? Why write the ID, and not the version?
  version_number = data;
  Serial.println(join("$", "version", version_number));
}


// The below function supports only relative motion
void setStep(String distance) {
   stream = true;
   Serial.println(join(">", "step", distance));
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
   Serial.println(join(">", "step", distance));
   stream = false;
}

void setKill() {
  motor.release();
  Serial.println(join("$", "kill", "true"));
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
  if (symbol == "?") {
    if (command == "id") {
      getID();
    }
    else if (command == "version") {
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
    
  
  else if (symbol == "!") {
    if (command == "id") {
      setID(data);
    }
    else if (command == "version") {
      setVersion(data);
    }
    else if (command == "step") {
      setStep(data);
    }
    else if (command == "speed") {
      setSpeed(data); //This function is already in the motor shield library
    }
    else if (command == "kill") {
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


