//FOR 2 ADC
#include <ADC.h>
#include "Teensy31FastADC.h"

//FOR TEMPERATURE/HUMIDITY SENSOR
#include <dht11.h>
#define DHT11PIN 12
static dht11 DHT11;


// Teensy 3.1 has the LED on pin 13
#define LEDPIN 13

void setup() {

  pinMode(LEDPIN, OUTPUT);
  pinMode(A2, INPUT); 
  pinMode(A3, INPUT); 
  pinMode(A10, INPUT); 
  pinMode(A11, INPUT);
  highSpeed8bitADCSetup();

  Serial.begin(9600);
  //BLINK LED, WE ARE ALIVE
  digitalWrite(LEDPIN,1);
  delay(2000);
  digitalWrite(LEDPIN,0);
}


#define SAMPLES 2048
#define BUFFERSIZE 2048

const int channelA2 = ADC::channel2sc1aADC0[2];
const int channelA3 = ADC::channel2sc1aADC1[3];
const int channelA11 = ADC::channel2sc1aADC0[11];
const int channelA10 = ADC::channel2sc1aADC1[10];

byte THRESHOLD = 160;
byte value1;
byte value2;
byte value3;
byte value4;

byte buffer1[BUFFERSIZE];
byte buffer2[BUFFERSIZE];
byte buffer3[BUFFERSIZE];
byte buffer4[BUFFERSIZE];

int samples;
long startTime;
long stopTime;
long totalTime;
int event;

int i;
int k;


void loop() {
  startTime = micros();
     //START SAMPLING
     //Strange init in this for, but the compiler seems to optimize this code better, so we get faster sampling
  for(i=0,k=0,samples=SAMPLES,event=0;i<samples;i++) {
    //TAKE THE READINGS
    highSpeed8bitAnalogReadMacro(channelA2,channelA3,value1,value2);
    //SHOULD ADJUST THIS 2nd READING
    highSpeed8bitAnalogReadMacro(channelA11, channelA10,value3,value4);
    
    //value2 = value3 = value4 = 0;
    
    buffer1[k] = value1;
    buffer2[k] = value2;
    buffer3[k] = value3;
    buffer4[k] = value4;
    
    //CHECK FOR EVENTS
    if (value1 > THRESHOLD && !event) {
      event = k;
      //THERE IS AN EVENT, ARE WE REACHING THE END? IF SO TAKE MORE SAMPLES
      if (i > SAMPLES-1024) samples = SAMPLES+1024;
      //SHOULD AJUST TIME LOST IN THIS LOGIC TOO
    }
    
    if (++k == BUFFERSIZE) k = 0; 
  }
  stopTime = micros();
  
  //WAS AN EVENT BEEN DETECTED?
  if (event != 0) {
    //printInfo();
    printSamplesHex(); 
      printInfo();
  }
 
  //DID WE RECEIVE COMMANDS?
  if (Serial.available()) parseSerial();

}


void parseSerial() {
  char c = Serial.read();

  switch (c) {
  case 'p': 
    printInfo();
    break;
  case 's': 
    printSamples();
    break;
  case '+': 
    THRESHOLD += 5;
    break;             
  case '-': 
    THRESHOLD -= 5;
    break;             
  default:  
    break;
  }
}


void printSamples() {


  Serial.print("BUFFSIZE: ");
  Serial.print(BUFFERSIZE,DEC);
  Serial.print(" Event: ");
  Serial.println(event);
  Serial.print("clear all; clc; x1=[");
  serialWriteDec(buffer1,BUFFERSIZE);
  Serial.println("];");
  Serial.print("x2=[");
  serialWriteDec(buffer2,BUFFERSIZE);
  Serial.println("];");
  Serial.print("x3=[");
  serialWriteDec(buffer3,BUFFERSIZE);
  Serial.println("];");
  Serial.print("x4=[");
  serialWriteDec(buffer4,BUFFERSIZE);
  Serial.println("];");
  Serial.println("plot(x1,'b-'); hold on; plot(x2,'g-'); hold on; plot(x3,'r-'); hold on; plot(x4,'k-'); hold off;");
  Serial.flush();
  
}

void printSamplesHex() {

//  Serial.println("START");
  //  Serial.print("BUFFSIZE: ");
//  Serial.print(BUFFERSIZE,DEC);
  serialWriteHex(buffer1,BUFFERSIZE);  
  serialWriteHex(buffer2,BUFFERSIZE);
  serialWriteHex(buffer3,BUFFERSIZE);
  serialWriteHex(buffer4,BUFFERSIZE);
  //Serial.flush();  
}


//This should be optimized. Writing raw binary data seems to fail a lot of times
//and I ended up loosing bytes. Maybe some form of flow-control should be used.
void serialWriteDec(byte *buffer,int siz) {
  int kk;
  for (kk=0;kk<siz;kk++) {
    Serial.print(buffer[kk],DEC);    
    buffer[kk] = 0;
    Serial.print(" ");
  }
}

void serialWriteHex(byte *buffer,int siz) {
  int kk;
  for (kk=0;kk<siz;kk++) {
    Serial.print(buffer[kk],HEX);    
    buffer[kk] = 0;
    Serial.print(" ");
  }
  Serial.println();
}

double getSpeedOfSound(double T, double RH)
{
  return 331.4 + 0.6*T + 0.0124*RH;
}



void printInfo() {
  totalTime = stopTime-startTime;
  double samplesPerSec = i*1000.0/totalTime;
  
  //Take a temperature/humidity reading
  //The DHT11 should be connected with a resistor for less errors in readings,
  // but works without it if you take some readings untils you got an ok one.

  while(DHT11.read(DHT11PIN) != DHTLIB_OK);
  
  double speed_of_sound = getSpeedOfSound( (double) DHT11.temperature, (double) DHT11.humidity);
  
  Serial.print("I ");
  Serial.println(event);
  Serial.print("T ");   
  //Serial.println(event);
  Serial.println(totalTime);
  Serial.print("S ");
  Serial.println(samplesPerSec,7);
  Serial.print("V ");
  Serial.println(speed_of_sound,7);
  
  Serial.println("END");
  //Serial.print(" Samples: ");
  //Serial.print(i,DEC);
  //Serial.print(" Samples/Sec: ");
  
  //Serial.print(samplesPerSec,7);
  
//  Serial.print(" Temp: ");
//  Serial.print((float)DHT11.temperature,2);
//  Serial.print(" Hum: ");
//  Serial.print((float)DHT11.humidity,2);
  //Serial.print(" Threshold: ");
  //Serial.println(THRESHOLD,DEC);
  Serial.flush();
}


void printInfoDebug() {
  totalTime = stopTime - startTime;
  double samplesPerSec = i*1000000.0/totalTime;
  
  //Take a temperature/humidity reading
  //The DHT11 should be connected with a resistor for less errors in readings,
  // but works without it if you take some readings untils you got an ok one.

  while(DHT11.read(DHT11PIN) != DHTLIB_OK);

  Serial.print("T: ");
  Serial.print(totalTime);
  Serial.print(" Samples: ");
  Serial.print(i,DEC);
  Serial.print(" Samples/Sec: ");
  Serial.print(samplesPerSec,7);
  Serial.print(" Temp: ");
  Serial.print((float)DHT11.temperature,2);
  Serial.print(" Hum: ");
  Serial.print((float)DHT11.humidity,2);
  Serial.print(" Threshold: ");
  Serial.println(THRESHOLD,DEC);
  Serial.flush();
}





