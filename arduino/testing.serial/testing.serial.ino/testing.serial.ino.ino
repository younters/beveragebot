String msg;

void setup() {
  Serial.begin(9600);
}

void loop() {
  readSerialPort();

  if (msg != "") {
    sendData();
  }
  delay(500);
  if(random(0, 20) == 3) {
    Serial.println("randtest");
  }
}

void readSerialPort() {
  msg = "";
  if (Serial.available()) {
    delay(10);
    while (Serial.available() > 0) {
      msg += (char)Serial.read();
    }
    Serial.flush();
  }

}

void sendData() {
  //write data

  Serial.print("received: ");
  Serial.print(msg);
}
