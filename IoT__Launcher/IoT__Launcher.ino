#include <Servo.h>
#include <LiquidCrystal_I2C.h>
 
Servo servo;
int trigPin = A0;
int echoPin = A1;

LiquidCrystal_I2C lcd(0x27,20,4);
unsigned int pinStatus = 0;
long distance;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  lcd.init();
  lcd.init();
  lcd.backlight();
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  servo.attach(2);
  servo.write(0);

}

void ultrasonicSensor()
{
  long duration;
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH);
  distance = (duration/2) / 29.1;
  if(distance < 5)
  {
    Serial.print("Ultrasonic Sensor: ");
    Serial.println("1");
    delay(2000);
  }
}

void reciever()
{
  if(Serial.available() > 0)
  {
    pinStatus = Serial.parseInt();
    switch (pinStatus)
    {
      case 1:
        servo.write(90);
        distance = 0;
        break;
      case 2:
        servo.write(0);
        break;
      default:
        break;
    }
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  ultrasonicSensor();
  reciever();
}
