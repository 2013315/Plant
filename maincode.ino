//temp + humidity sensor
#include <dht.h>
#define dhtReadings 8
#define DHTTYPE DHT11
dht DHT;

//LDR

int LDR = A5;

//soil moisture sensor 

int soilSensor = A0;

//water depth sensor

int trig = 12;
int echo = 13;
long duration = 0;
int distance = 0;

String pi = "";

//pump

int pump = 4; 

void setup(){
  Serial.begin(9600); 
  pinMode(LDR, INPUT);
  pinMode(soilSensor, INPUT);
  pinMode(trig, OUTPUT);
  pinMode(echo, INPUT);
  pinMode(pump, OUTPUT);
  digitalWrite(pump,LOW);
}

void loop(){
  digitalWrite(pump, LOW);
  if (Serial.available() > 0){
    digitalWrite(pump, LOW);
    String pi = Serial.readStringUntil('\n');
  if (pi == "data"){
    digitalWrite(pump, LOW);
    //temp humidity
    int readData = DHT.read11(dhtReadings);
    
    float t = DHT.temperature;
    float h = DHT.humidity;
    Serial.println(t);
    Serial.println(h);
    
    //light intensity
  
    int LDRReading = analogRead(LDR);

    Serial.println(LDRReading);
 
    //soil moisture 

    int soil = analogRead(soilSensor);

    Serial.println(soil);

   //water depth

   //average for water level as water is a liquid and averages gives a better idea of water level
   int averageLevel = 0;
  
   for (int x = 0; x < 5; x++){
     digitalWrite(trig, HIGH);
     delayMicroseconds(10);
     digitalWrite(trig, LOW);
     duration = pulseIn(echo, HIGH);
     distance = duration*0.0343/2;
     digitalWrite(echo,LOW);
     averageLevel += distance;
   }

   averageLevel = averageLevel/5;
   Serial.println(averageLevel);
  }
  if (pi == "pump"){
    Serial.println("received");
    digitalWrite(pump, HIGH);
    int soil = analogRead(soilSensor);
    while (soil < 650){
      soil = analogRead(soilSensor); 
    }
    digitalWrite(pump, LOW);
    Serial.println("completed");
   }
 }
}
