/*
Author  : Andrea Lombardo
Site    : https://www.lombardoandrea.com
Source  : https://github.com/AndreaLombardo/L298N/
Here you can see how to work in a common configuration. 
Speed range go from 0 to 255, default is 100.
Use setSpeed(speed) to change.
Sometimes at lower speed motors seems not running.
It's normal, may depends by motor and power supply.
Wiring schema in file "L298N - Schema_with_EN_pin.png"
*/

// Include the library

// Pin definition
const unsigned int IN1 = 10;
const unsigned int IN2 = 11;
const unsigned int EN = 9;

// Create one motor instance

void setup()
{
  // Used to display information
  Serial.begin(9600);
  pinMode(IN2, OUTPUT); //IN2
  pinMode(IN1, OUTPUT); //IN1
  pinMode(EN, OUTPUT); //Enable Pin

  // Wait for Serial Monitor to be opened
  while (!Serial)
  {
    //do nothing
  }

}

void loop()
{
  digitalWrite(IN2, HIGH);
  digitalWrite(IN1, LOW);
  analogWrite(EN, 255);


  printSomeInfo();

  delay(30);
}

/*
Print some informations in Serial Monitor
*/
void printSomeInfo()
{
  //Serial.println("Motor is moving =");
  //Serial.println(analogRead(0));
}