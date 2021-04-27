//#include <Stepper.h> 

#include <AccelStepper.h>
#include <L298NX2.h>
/* 
NEMA23
0.9 step angle (400)
black piece
0.38 amps (0.152 v)

NEMA17
1.8 step angle (200) in practice 400 for work
0.4 amps (0.16 v)
dark red a4988
*/

// Step then Dir
AccelStepper stepperIce(AccelStepper::FULL2WIRE, 4, 5);
AccelStepper stepperTray(AccelStepper::FULL2WIRE, 2, 3);


// Pump 1
const unsigned int EN_A = 10;
const unsigned int IN1_A = 36;
const unsigned int IN2_A = 37;
// Pump 2
const unsigned int IN1_B = 38;
const unsigned int IN2_B = 39;
const unsigned int EN_B = 11;
// Pump 3
const unsigned int EN_C = 9;
const unsigned int IN1_C = 40;
const unsigned int IN2_C = 41;
// Pump 4
const unsigned int IN1_D = 42;
const unsigned int IN2_D = 43;
const unsigned int EN_D = 10;

// Initialize both motors
L298NX2 motors1(EN_A, IN1_A, IN2_A, EN_B, IN1_B, IN2_B);
L298NX2 motors2(EN_C, IN1_C, IN2_C, EN_D, IN1_D, IN2_B);

// Define relay
const int relayPin = 22;

const byte numChars = 32;
char receivedChars[numChars]; // an array to store the received data

boolean newData = false;

int src0Time = 0;
int pump0Time = 0;
int pump1Time = 0;
int pump2Time = 0;
int pump3Time = 0;


void setup() {
  // initialize the serial port:
  //delay(1000*5);
  Serial.begin(115200);

  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, LOW);

  stepperIce.setMaxSpeed(200.0);
  stepperIce.setAcceleration(100.0);
  stepperIce.setCurrentPosition(0);

  stepperTray.setMaxSpeed(200.0);
  stepperTray.setAcceleration(50.0);
  stepperTray.setCurrentPosition(0);
  //stepperTray.setMinPulseWidth(300);

  motors1.setSpeedA(255);
  motors1.setSpeedB(255);
  motors2.setSpeedA(255);
  motors2.setSpeedB(255);
  
  //Serial.println(stepperIce.currentPosition());
}

void loop() {

  //if (stepperIce.distanceToGo() == 0)
	//stepperIce.moveTo(-stepperIce.currentPosition());
  stepperIce.run();
  stepperTray.run();
  
  /*// step one revolution  in one direction:
  Serial.println("clockwise");
  myStepper.step(stepsPerRevolution);
  delay(500);

  // step one revolution in the other direction:
  Serial.println("counterclockwise");
  myStepper.step(-stepsPerRevolution);
  delay(500);*/
  
  //Serial.println(stepperIce.speed());
  
  //rotateTray(360);
  //delay(3000);
  recvWithStartEndMarkers();
  parseData();

  motors1.runForA(pump0Time, L298N::FORWARD);
  motors1.runForB(pump1Time, L298N::FORWARD);
  motors2.runForA(pump2Time, L298N::FORWARD);
  motors2.runForB(pump3Time, L298N::FORWARD);

  if(src0Time > millis()) {
    // open the valve
    digitalWrite(relayPin, HIGH);
  } else {
    // close valve
    digitalWrite(relayPin, LOW);
  }


  //showNewData();
}

void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;

 // if (Serial.available() > 0) {
    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
}

void showNewData() {
    if (newData == true) {
        Serial.print("Received Command: ");
        Serial.println(receivedChars);
        newData = false;
    }
}

void parseData() {
  if(!newData) return;
  newData = false;
  char* command = receivedChars;
  char* separator = strchr(command, '|');
  if (separator != 0)
  {
     // Actually split the string in 2: replace ':' with 0
      *separator = 0;
      String name = String(command);
      ++separator;
      float value = atof(separator);
      //Serial.println("moving " + name + " with value of " + String(value));
      // Do something with servoId and position
          
      if(name == "tray") {
          Serial.println("Moving Tray a" + String(value));
          rotateTray(value);
      }
      else if(name == "ice") {
          Serial.println("Ice dispense s" + String(value));
          pourIce(value);
      }
      else if(name == "src0") {
          src0Time = millis() + int(value * 1000);
          Serial.println("SRC 0, " + String(value));
      }
      else if(name == "tap0") {
          motors1.resetA();
          pump0Time = int(value * 1000);
          Serial.println("Tap 0, " + String(value));
      }
      else if(name == "tap1") {
          motors1.resetB();
          pump1Time = int(value * 1000);
          Serial.println("Tap 1, " + String(value));
      }
      else if(name == "tap2") {
          motors2.resetA();
          pump2Time = int(value * 1000);
          Serial.println("Tap 2, " + String(value));
      }
      else if(name == "tap3") {
          motors2.resetB();
          pump3Time = int(value * 1000);
          Serial.println("Tap 3, " + String(value));
      }        
      
  }
}




void pourIce(int period) { // pour ice for x seconds. runs a little long b/c acceleration
  // convert time to positions
  int pos = stepperIce.targetPosition() - stepperIce.maxSpeed() * period;
  //Serial.println(pos);
  Serial.println("pouring ice");
  
  stepperIce.moveTo(pos);
}

void rotateTray(int angle) {
  float pos = stepperTray.targetPosition() + angle / 0.9 * 4;
  Serial.println(pos);
  stepperTray.moveTo(pos);
  //stepperTray.runToPosition();
}


