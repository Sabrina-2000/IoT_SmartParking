#include <Servo.h>
#include <MFRC522.h>
#include <SPI.h>

Servo servo;
int SS_PIN = 10;
int RST_PIN = 9;
MFRC522 mfrc522(SS_PIN, RST_PIN); 
int trigPin = A0;
int echoPin = A1;
int trigPin2 = A2;
int echoPin2 = A3;
int lockLed = 3;
int button = 4;
int lockLed2 = 5;
int basementLed = 6;

unsigned int pinStatus = 0;
long distance;
int secondslot;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(trigPin2, OUTPUT);
  pinMode(echoPin2, INPUT);
  pinMode(lockLed, OUTPUT);
  pinMode(lockLed2, OUTPUT);
  pinMode(basementLed, OUTPUT);
  pinMode(button, INPUT_PULLUP);
  servo.attach(2);
  servo.write(0);
  SPI.begin();
  mfrc522.PCD_Init();
  digitalWrite(lockLed, LOW);
  digitalWrite(lockLed2, LOW);
  digitalWrite(basementLed, LOW);
  Serial.println("Approximate your card to the reader...");
}

void RFID()
{
  // Look for new cards
  if ( ! mfrc522.PICC_IsNewCardPresent()) 
  {
    return;
  }
  // Select one of the cards
  if ( ! mfrc522.PICC_ReadCardSerial()) 
  {
    return;
  }
  //Show UID on serial monitor
  Serial.print("UID tag :");
  String content= "";
  byte letter;
  for (byte i = 0; i < mfrc522.uid.size; i++) 
  {
     Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " ");
     Serial.print(mfrc522.uid.uidByte[i], HEX);
     content.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " "));
     content.concat(String(mfrc522.uid.uidByte[i], HEX));
  }
  Serial.println();
  Serial.print("Message : ");
  content.toUpperCase();
  if (content.substring(1) == "8A DA 0A 3F") //change here the UID of the card/cards that you want to give access
  {
    //parking lock dropped down, when RFID tag is valid
    Serial.println("Authorized access");
    Serial.println();
    digitalWrite(lockLed, HIGH); 
    delay(3000);
    SlotSensor();
  }
 
 else   {
    Serial.println(" Access denied");
    delay(3000);
  }
}

void SlotSensor()
{
  long duration;
  digitalWrite(trigPin2, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin2, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin2, LOW);
  duration = pulseIn(echoPin2, HIGH);
  distance = (duration/2) / 29.1;
  Serial.print("Distance: ");
  Serial.println(distance);
  if(distance < 10 && distance > 3)
  {
    //car is parked, parking lock rise
    Serial.print("Slot Sensor: ");
    Serial.println("1");
    delay(3000);
    digitalWrite(lockLed, LOW);
  }
  else if(distance <= 3)
  {
    //ultrasonic sensor is cover by something, parking lock rise 
    Serial.println("Vechile not detected (ERROR) Pls check!!");
    digitalWrite(lockLed, LOW);
  }
  else if(distance >= 10 && distance <= 20)
  {
    //car leave, parking lock rise
    Serial.println("Leave");
    delay(3000);
    digitalWrite(lockLed, LOW);
  }
  else
  {
    //car is not parked, parking lock rise
    Serial.println("Car is not parked");
    digitalWrite(lockLed, LOW);
  }
}

void SlotSensor2()
{
  if(digitalRead(button) == LOW && secondslot == 1)
  {
    digitalWrite(lockLed2, HIGH);
    Serial.println("Slot Sensor2: leave");
    delay(3000);
    digitalWrite(lockLed2, LOW);
    secondslot = 0;
  }

  else if(digitalRead(button) == LOW)
  {
    digitalWrite(lockLed2, HIGH);
    Serial.println("Slot Sensor2: parked");
    delay(3000);
    digitalWrite(lockLed2, LOW);
    secondslot = 1;
  }
  
}

void DoorSensor()
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
    Serial.print("Door Sensor: ");
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
        servo.write(90); //open gate
        distance = 0;
        break;
      case 2:
        servo.write(0); //close gate
        break;
      case 3:
        digitalWrite(basementLed, HIGH); //open basement 2
        break;
      case 4:
        digitalWrite(basementLed, LOW);//close basement 2
        break;
      default:
        break;
    }
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  DoorSensor();
  reciever();
  RFID();
  SlotSensor2();
}
