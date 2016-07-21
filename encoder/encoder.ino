
int pinA = 2;
int pinB = 3;

volatile unsigned int pos = 0;
int prevVal = 0;

void setup() {

  pinMode(pinA, INPUT);
  digitalWrite(pinA, HIGH);

  pinMode(pinB, INPUT);
  digitalWrite(pinB, HIGH);
  
  prevVal = binaryToDecimal(digitalRead(pinA), digitalRead(pinB));

//  attachInterrupt(digitalPinToInterrupt(pinA), doEncoder, CHANGE);
//  attachInterrupt(digitalPinToInterrupt(pinB), doEncoder, CHANGE);
  Serial.begin(9600);
  Serial.println("start");
}

void loop() {
//  delay(500);
//  Serial.println(String(digitalRead(pinA)) + " " + String(digitalRead(pinB)));
}

int binaryToDecimal(int a, int b) {
//  Serial.println(String(a) + " " + String(b) + " -> " + String((a*2) + (b*1)));
  return (a*2 + b*1);
}

void doEncoder() {
  int val = binaryToDecimal(digitalRead(pinA), digitalRead(pinB));

//  Serial.println(String(val) + " > " + String(prevVal));
  
  switch(val) {
    case 1:
      if (prevVal == 3) {
        pos ++;
      } else {
        pos --;
      }
      break;
      
    case 0:
      if (prevVal == 1) {
        pos ++;
      } else {
        pos --;
      }
      break;

    case 2:
      if (prevVal == 0) {
        pos ++;
      } else {
        pos --;
      }
      break;

    case 3:
      if (prevVal == 2) {
        pos ++;
      } else {
        pos --;
      }
      break;
  }

//  Serial.println(String(digitalRead(pinA)) + " " + String(digitalRead(pinB)));
  Serial.println(pos);

  prevVal = val;
}

