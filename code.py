#include <AltSoftSerial.h>
#include <TinyGPS++.h>
#include<Wire.h>
#include <math.h>
#include <SoftwareSerial.h>

const String EMERGENCY_PHONE = "‪+916302766762‬";
#define rxPin 2
#define txPin 3

SoftwareSerial sim800(rxPin, txPin);
AltSoftSerial neogps;
TinyGPSPlus gps;

String sms_status, sender_number, received_date, msg;
String latitude = "17.5999157", longitude = "78.4834919"; // CMREC Campus coordinates
#define BUZZER 5
#define BUTTON 6
#define xPin A0
#define yPin A1
#define zPin A2

byte updateflag;
int xaxis = 0, yaxis = 0, zaxis = 0;
int deltx = 0, delty = 0, deltz = 0;
int vibration = 2;
int devibrate = 75;
int magnitude = 0;
int sensitivity = 20;

unsigned long time1;
unsigned long impact_time;
unsigned long alert_delay = 30000;
boolean impact_detected = false;

void setup()
{
  Serial.begin(9600);
  sim800.begin(9600);
  neogps.begin(9600);
  pinMode(BUZZER, OUTPUT);
  pinMode(BUTTON, INPUT_PULLUP);

  sms_status = "";
  sender_number = "";
  received_date = "";
  msg = "";
  sim800.println("AT");
  delay(1000);
  sim800.println("ATE1");
  delay(1000);
  sim800.println("AT+CPIN?");
  delay(1000);
  sim800.println("AT+CMGF=1");
  delay(1000);
  sim800.println("AT+CNMI=1,1,0,0,0");
  delay(1000);
  time1 = micros();
  xaxis = analogRead(xPin);
  yaxis = analogRead(yPin);
  zaxis = analogRead(zPin);
}

void loop()
{
  if (micros() - time1 > 4999) Impact();
  if (updateflag > 0)
  {
    updateflag = 0;
    Serial.println("Impact detected!!");
    Serial.print("Magnitude:");
    Serial.println(magnitude);

    Serial.print("Latitude: "); Serial.println(latitude);
    Serial.print("Longitude: "); Serial.println(longitude);
    Serial.print("Location Link: "); Serial.println("https://g.co/kgs/wZUDpRB");

    digitalWrite(BUZZER, HIGH);
    delay(10000); // Buzzer on for 10 seconds
    digitalWrite(BUZZER, LOW);
    
    makeCall();
    sendAlert();
  }

  if (digitalRead(BUTTON) == LOW) {
    delay(200);
    digitalWrite(BUZZER, LOW);
    impact_detected = false;
  }
}

void Impact()
{
  time1 = micros();
  int oldx = xaxis;
  int oldy = yaxis;
  int oldz = zaxis;

  xaxis = analogRead(xPin);
  yaxis = analogRead(yPin);
  zaxis = analogRead(zPin);

  deltx = xaxis - oldx;
  delty = yaxis - oldy;
  deltz = zaxis - oldz;

  magnitude = sqrt(sq(deltx) + sq(delty) + sq(deltz));
  if (magnitude >= sensitivity) // impact detected
  {
    updateflag = 1;
  }
  else
  {
    magnitude = 0;
  }
}

void sendAlert()
{
  String sms_data;
  sms_data = "Emergency Alert!!\r";
  sms_data += "Location: https://g.co/kgs/wZUDpRB"; // Google Maps link for CMREC
  sendSms(sms_data);
}

void makeCall()
{
  Serial.println("calling....");
  sim800.println("ATD" + EMERGENCY_PHONE + ";");
  delay(20000);
  sim800.println("ATH");
  delay(1000);
}

void sendSms(String text)
{
  sim800.print("AT+CMGF=1\r");
  delay(1000);
  sim800.print("AT+CMGS=\"" + EMERGENCY_PHONE + "\"\r");
  delay(1000);
  sim800.print(text);
  delay(100);
  sim800.write(0x1A);
  delay(1000);
  Serial.println("SMS Sent Successfully.");
}
