#include <Servo.h>

const byte servoPin = 3;
const byte analogPin = A0;
const byte randAnalogPin = A2;
const byte buttonPin = 2;

Servo servo;
bool isOn = false;

void setup() {
  servo.attach(servoPin);
  Serial.begin(9600);
  pinMode(buttonPin, INPUT);
  attachInterrupt(digitalPinToInterrupt(buttonPin), onOff, FALLING);
  randomSeed(analogRead(randAnalogPin));
  Serial.println("\n\rPROGRAM STARTS");
}

void loop() {  
  if (isOn) {
    long slowness = readPot();
    Serial.print("slowness = ");
    Serial.print(slowness);
    Serial.print("\n\r");
    openAndClose();
    slownessDelay(slowness);
    randomDelay(slowness);
  }
  delay(100);
}


void slownessDelay(long slowness) {
  delay(5000 + (slowness/10) * 1000);
}

void randomDelay(long slowness) {
  long randNumber = random((int) (slowness + 1));
  Serial.print("ranNumber = ");
  Serial.print(slowness);
  Serial.print("\n\r");
  delay((randNumber/10) * 1000);
}

void onOff(){
  isOn = !isOn;
}

int readPot(){
  int read = analogRead(analogPin);
  long val = ((long) read) * 100 / 1023;
  if (val > 100) {
    val = 100;
  }
  if (val < 0) {
    val = 0;
  }
  return val;
}

void openAndClose(){
  open();
  delay(200);
  close();
}

void open() {
  safe_move(120);
}

void close() {
  safe_move(90);
}

void safe_move(int angle) 
{
  if (angle < 90){
    return;
  }
  if (angle > 160) {
    return;
  }
  servo.write(angle);
}