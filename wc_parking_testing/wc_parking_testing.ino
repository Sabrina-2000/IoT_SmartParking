int trigPin = A0;
int echoPin = A1;
int detectionLED = 2;
long distance;

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
    digitalWrite(detectionLED,HIGH);
    //Serial.println("Object detected!");
    delay(2000);
  }
  else
  {
    digitalWrite(detectionLED,LOW);
  }
}

void setup() {
  // put your setup code here, to run once:
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(2, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
   ultrasonicSensor();

}
