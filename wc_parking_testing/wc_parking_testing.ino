#include <SPI.h>
#include <MFRC522.h>
 
#define SS_PIN 10
#define RST_PIN 9
MFRC522 mfrc522(SS_PIN, RST_PIN);  




//FIRST parking slot (ultrasonic and RFID)
int trigPin = A0;
int echoPin = A1;
int detectionLED = 2;
long distance;
int var = 0;
int varr = 0;



////////////////////////////////////
//SECOND parking slot(button-DEMO)//
////////////////////////////////////
const int buttonPin = 3;     // the number of the pushbutton pin
const int ledPin =  4;      // the number of the LED pin
int buttonState = 0;
int secondslot=0;



/////////////////////
//Open New Basement//
/////////////////////
const int ledBasement = 5;
int openbasemnt=0;




///////////////////////////////////////
//Detection of Vehicle Parked in Slot//
///////////////////////////////////////
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
  if(distance < 10)
  {
    while(varr<3){
    Serial.print("Ultrasonic Sensor: ");
    Serial.println("1");
    digitalWrite(detectionLED,HIGH);
    //Serial.println("Object detected!");
    delay(1000);
    varr ++;
     if(varr==3)
      {Serial.println("Parked"); varr=0; var=1; break;}
    }
     digitalWrite(detectionLED,LOW);
  }
  else
  {
    digitalWrite(detectionLED,LOW);
  }
}



////////////////////////////////////////////////////////////////////////
//Detection of Vehicle Leaved the Slot or Vechile missing after parked//
////////////////////////////////////////////////////////////////////////
void ultrasonicSensor2()
{
  long duration;
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH);
  distance = (duration/2) / 29.1;
  if(distance < 10)
  {
    while(var==1){
    Serial.print("Ultrasonic Sensor: ");
    Serial.println("1");
    digitalWrite(detectionLED,HIGH);
    //Serial.println("Object detected!");
    delay(1000);
    varr ++;
     if(varr==3)
      {Serial.println("Leaved"); varr=0; var=0; break;}
    }
     digitalWrite(detectionLED,LOW);
  }

  else
  {
    {Serial.println("Vechile not detected (ERROR) Pls check!!"); varr=0; var=1;}
    digitalWrite(detectionLED,LOW);
  }
}



///////////////////////////////////////////
//The Main code of the FRIST Parking Slot//
///////////////////////////////////////////
void Parking_Slot(){
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
  
  
 if (content.substring(1) == "E3 4B B3 18" && var==1)
 {
    Serial.println("Authorized access");
    
    ultrasonicSensor2();
   
    Serial.println(".....");
    Serial.println();
    content.substring(1) = " ";
    delay(3000);
 }

  else if (content.substring(1) == "E3 4B B3 18") //change here the UID of the card/cards that you want to give access
  {
    Serial.println("Authorized access");
    
    ultrasonicSensor();
   
    Serial.println(".....");
    Serial.println();
    content.substring(1) = " ";
    delay(3000);
  }
 
 else   {
    Serial.println(" Access denied");
    Serial.println(".....");
    Serial.println();
    delay(3000);
  }
  
}



///////////////////////////////////
//SECOND parking Slot Button DEMO//
///////////////////////////////////
void Second_Parking_Slot()
{
  // read the state of the pushbutton value:
  buttonState = digitalRead(buttonPin);

  // check if the pushbutton is pressed. If it is, the buttonState is HIGH:
  
  if (buttonState == HIGH && secondslot==1) 
  {
    // turn LED on:
    digitalWrite(ledPin, HIGH);
    Serial.println("Demo second parking slot");
    Serial.println("Ultrasonic Sensor: 1");
    Serial.println("Ultrasonic Sensor: 1");
    Serial.println("Ultrasonic Sensor: 1");
    Serial.println("Ultrasonic Sensor: 1");
    Serial.println("Ultrasonic Sensor: 1");
    Serial.println("Leaved");
    Serial.println(".....");
    Serial.println();
    //digitalWrite(ledPin, HIGH);
    secondslot=0;
    delay(3000);
  }

  
  else if (buttonState == HIGH) 
  {
    // turn LED on:
    digitalWrite(ledPin, HIGH);
    Serial.println("Demo second parking slot");
    Serial.println("Ultrasonic Sensor: 1");
    Serial.println("Ultrasonic Sensor: 1");
    Serial.println("Ultrasonic Sensor: 1");
    Serial.println("Ultrasonic Sensor: 1");
    Serial.println("Ultrasonic Sensor: 1");
    Serial.println("Parked");
    Serial.println(".....");
    //digitalWrite(ledPin, HIGH);
    Serial.println();
    secondslot=1;
    delay(3000);
  }

  
  
  else {
    // turn LED off:
    digitalWrite(ledPin, LOW);
  }
}


////////////////
//New Basement//
///////////////
void OpenNewBasement()
{

  if(openbasemnt==1)
  {digitalWrite(ledBasement, HIGH);}

  else
  {digitalWrite(ledBasement, LOW);}
  
}




////////////////////////////////////////////////////////////////////
void setup() {
  // put your setup code here, to run once:
  
  //setup RFID
  SPI.begin();      // Initiate  SPI bus
  mfrc522.PCD_Init();   // Initiate MFRC522
  Serial.println("Approximate your card to the reader...");
  Serial.println();

  //setup ultrasonic
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(2, OUTPUT);

  //setup button
  pinMode(ledPin, OUTPUT);
  pinMode(buttonPin, INPUT);

  //setup basement
  pinMode(ledBasement, OUTPUT);

  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
   //ultrasonicSensor();
   Parking_Slot();
   Second_Parking_Slot();
   OpenNewBasement();
  
}
