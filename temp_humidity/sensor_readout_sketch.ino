    /////////////////////////////////////////////////////////////////
   //     ESP32 & Xiaomi Bluetooth  sensor   Oct. 2020  v1.01     //
  //       Get the latest version of the code here:              //
 //           http://educ8s.tv/esp32-xiaomi-hack                //
/////////////////////////////////////////////////////////////////


// IMPORTANT
// You need to install this library as well else it won't work
// https://github.com/fguiet/ESP32_BLE_Arduino


// #include "SPI.h"
// #include "Adafruit_GFX.h"      //https://github.com/adafruit/Adafruit-GFX-Library
// #include "Adafruit_ILI9341.h"  //https://github.com/adafruit/Adafruit_ILI9341

#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"
#include "esp_system.h"
#include <sstream>

#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>

#define SCAN_TIME  10 // seconds
#define LED_PIN 2

BLEScan *pBLEScan;

void IRAM_ATTR resetModule(){
    ets_printf("reboot\n");
    esp_restart();
}

bool verbose = 0;
         
float current_humidity = -100;
float current_temperature = -100;
float current_battery = -100;

String command;


// Adafruit_ILI9341 tft = Adafruit_ILI9341(TFT_CS, TFT_DC, TFT_RST);

class MyAdvertisedDeviceCallbacks : public BLEAdvertisedDeviceCallbacks {
    void onResult(BLEAdvertisedDevice advertisedDevice){
      if (verbose){
      Serial.printf("Discovered device: %s\n", advertisedDevice.toString().c_str());
      }
if (advertisedDevice.haveName() && advertisedDevice.haveServiceData() && advertisedDevice.getName().find("ATC_") != std::string::npos) {
    if (verbose) {
    Serial.printf("Matched device: %s\n", advertisedDevice.getName().c_str());
        }
            int serviceDataCount = advertisedDevice.getServiceDataCount();
            std::string strServiceData = advertisedDevice.getServiceData(0);

            uint8_t cServiceData[100];
            char charServiceData[100];

            strServiceData.copy((char *)cServiceData, strServiceData.length(), 0);
            

            for (int i=0;i<strServiceData.length();i++) {
                sprintf(&charServiceData[i*2], "%02x", cServiceData[i]);
            }

            std::stringstream ss;
            ss << "fe95" << charServiceData;
  
            char eventLog[256];
            unsigned long value, value2;
            char charValue[5] = {0,};
            char charValue2[5] = {0,};


          if (strServiceData.length() >= 13) {

            if (verbose) {
                Serial.print("Raw Service Data: ");
                for (int i = 0; i < strServiceData.length(); i++) {
                    Serial.printf("%02X ", cServiceData[i]);
                }
                Serial.println();
              }

            int16_t temp_raw = ((int16_t)cServiceData[6] << 8) | cServiceData[7];
            current_temperature = (float)temp_raw / 10.0f;
            current_humidity  = (float)cServiceData[8];
            current_battery   = (float)cServiceData[9];

            // Blink LED on a new reading
            digitalWrite(LED_PIN, HIGH);
            delay(100);
            digitalWrite(LED_PIN, LOW);

            if (verbose) {
                Serial.printf("ATC format detected\n");
                Serial.printf("TEMP: %.1f °C, HUM: %.1f %%, BATT: %.0f %%\n",
                              current_temperature,
                              current_humidity,
                              current_battery);
                            }
                      }
                  }
              }
          };

void setup() {
  
  pinMode(LED_PIN, OUTPUT);
  Serial.begin(9600);
  Serial.setTimeout(20);
  Serial.println("ESP32 XIAOMI Readout started");
 
  initBluetooth();

}

void loop() {

    BLEScan* pBLEScan = BLEDevice::getScan(); //create new scan
    pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
    pBLEScan->setActiveScan(true); //active scan uses more power, but get results faster
    BLEScanResults foundDevices = pBLEScan->start(SCAN_TIME);
    
    int count = foundDevices.getCount();
    if (verbose){
      printf("Found device count : %d\n", count);
    }
    
    
    if (Serial.available()) {
      // Serial.printf("Start \n");
      command = Serial.readStringUntil('\n');
      command.trim();
      if (command.equals("data")) {
        if (current_temperature > -99.9 && current_battery > -99.9){
    Serial.printf("%1.2f,%1.2f,%1.0f\n", current_temperature, current_humidity, current_battery);
  }
      }
      else if (command.equals("ver")) {
          verbose = !verbose;
          Serial.printf("verbose statue change to %d \n", verbose);
      }
      else{Serial.printf("Bad command.\n"); }
      // Serial.printf("End \n");
    }
}

int readCommand()
{
  char lastchar = ' ';
  int  i = 0;
  
  while (lastchar != '#')
  {
    if (Serial.available()>0)
    {
      lastchar = Serial.read();
      Serial.println(lastchar, DEC);
      if (lastchar == '#') 
      {
         command[i] = '\0'; 
      } 
      else command[i++] = lastchar;
    }
    Serial.println(command);
  }
}


void initBluetooth()
{
    BLEDevice::init("");
    pBLEScan = BLEDevice::getScan(); //create new scan
    pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
    pBLEScan->setActiveScan(true); //active scan uses more power, but get results faster
    pBLEScan->setInterval(0x50);
    pBLEScan->setWindow(0x30);
}


String convertFloatToString(float f)
{
  String s = String(f,1);
  return s;
}

