/*
 * Monitoring Arduino
 * 
 * 
 */

// Libraries
#include <OneWire.h>
#include <DallasTemperature.h>
#include <DHT.h>

// Constants
#define DHTTYPE DHT11

// Digital Pins
#define DHT_PIN 3
#define TEMP_TANK 5

// Analog Pins
#define WATER_LEVEL_TANK 0
#define WATER_LEVEL_ZERO 1
#define WATER_LEVEL_ONE 2
#define WATER_LEVEL_TWO 3

#define TDSPIN  A5
#define VREF 5.0 // analog reference voltage(Volt) of the ADC
#define SCOUNT 30 // sum of sample point

int analogBuffer[SCOUNT]; // store the analog value in the array, read from ADC
int analogBufferTemp[SCOUNT];
int analogBufferIndex = 0,copyIndex = 0;
float averageVoltage = 0,tdsValue = 0,temperature = 25;

#define PHPIN A4            //pH meter Analog output to Arduino Analog Input 0
#define Offset 0.33            //deviation compensate
#define samplingInterval 20
#define printInterval 1000
#define ArrayLenth  40    //times of collection
int pHArray[ArrayLenth];   //Store the average value of the sensor feedback
int pHArrayIndex=0;


OneWire oneWire(TEMP_TANK);
DallasTemperature sensors(&oneWire);

DHT dht(DHT_PIN, DHTTYPE);

// Array
float vial_parameters[10] = {0,
                             0,
                             0,
                             0,
                             0,
                             0,
                             0,
                             0,
                             0,
                             0};

//Vars
float temp_air = 0;
float temp_tank = 0;
int waterlevel_tank = 0;
int waterlevel_floor1 = 0;
int waterlevel_floor2 = 0;
float humidity = 0;

void setup()
{
  pinMode(DHT_PIN, INPUT);
  pinMode(TEMP_TANK, INPUT);
  pinMode(WATER_LEVEL_TANK, INPUT);
  pinMode(WATER_LEVEL_ZERO, INPUT);
  pinMode(WATER_LEVEL_ONE, INPUT);
  pinMode(WATER_LEVEL_TWO, INPUT);
  pinMode(PHPIN, INPUT);
  pinMode(TDSPIN, INPUT);

  Serial.begin(115200);
  sensors.begin();
  dht.begin();
}

void loop()
{ 
  // PH
  static unsigned long samplingTime = millis();
  static unsigned long printTime = millis();
  static float pHValue,voltage;
  // TDS
  static unsigned long analogSampleTimepoint = millis();
  
  delay(5000);
  
  humidity = dht.readHumidity();
  temp_air = dht.readTemperature();
  
  sensors.requestTemperatures(); // Send the command to get temperatures
  temp_tank = sensors.getTempCByIndex(0);

  if (temp_tank == (-127.00))
  {
    temp_tank = vial_parameters[1];
  }

  // Water Level
  waterlevel_tank = analogRead(WATER_LEVEL_TANK);
  //waterlevel_floor0 = analogRead(WATER_LEVEL_ZERO);
  waterlevel_floor1 = analogRead(WATER_LEVEL_ONE);
  waterlevel_floor2 = analogRead(WATER_LEVEL_TWO);

  // PH
  if(millis()-samplingTime > samplingInterval)
  {
      pHArray[pHArrayIndex++]=analogRead(PHPIN);
      if(pHArrayIndex==ArrayLenth)pHArrayIndex=0;
      voltage = avergearray(pHArray, ArrayLenth)*5.0/1024;
      pHValue = 3.5*voltage+Offset;
      samplingTime=millis();
  }

  // TDS
  if(millis()-analogSampleTimepoint > 40U) //every 40 milliseconds,read the analog value from the ADC
  {
    analogSampleTimepoint = millis();
    analogBuffer[analogBufferIndex] = analogRead(TDSPIN); //read the analog value and store into the buffer
    analogBufferIndex++;
    if(analogBufferIndex == SCOUNT)analogBufferIndex = 0;
  }
  static unsigned long printTimepoint = millis();
  if(millis()-printTimepoint > 800U)
  {
    printTimepoint = millis();
    for(copyIndex=0;copyIndex<SCOUNT;copyIndex++)
    analogBufferTemp[copyIndex]= analogBuffer[copyIndex];
    averageVoltage = getMedianNum(analogBufferTemp,SCOUNT) * (float)VREF/ 1024.0; // read the analog value more stable by the median filtering algorithm, and convert to voltage value
    float compensationCoefficient=1.0+0.02*(temp_tank-25.0); //temperature compensation formula: fFinalResult(25^C) = fFinalResult(current)/(1.0+0.02*(fTP-25.0));
    float compensationVolatge=averageVoltage/compensationCoefficient; //temperature compensation
    tdsValue=(133.42*compensationVolatge*compensationVolatge*compensationVolatge - 255.86*compensationVolatge*compensationVolatge + 857.39*compensationVolatge)*0.5; //convert voltage value to tds value
    vial_parameters[9] = tdsValue;
  }

  // Write Array with Sensor Data
  vial_parameters[0] = temp_air;
  vial_parameters[1] = temp_tank;
  vial_parameters[2] = waterlevel_tank;
  vial_parameters[3] = waterlevel_floor1;
  vial_parameters[4] = waterlevel_floor2;
  vial_parameters[5] = humidity;
  vial_parameters[7] = voltage;
  vial_parameters[8] = pHValue;
  
  // Print Array to Serial (to the Pi)
  for (int i = 0; i < 10; i++)
  {
    Serial.println(vial_parameters[i]);
    delay(50);
  }
}

int getMedianNum(int bArray[], int iFilterLen)
{
  int bTab[iFilterLen];
  for (byte i = 0; i<iFilterLen; i++)
  bTab[i] = bArray[i];
  int i, j, bTemp;
  for (j = 0; j < iFilterLen - 1; j++)
  {
    for (i = 0; i < iFilterLen - j - 1; i++)
    {
      if (bTab[i] > bTab[i + 1])
      {
        bTemp = bTab[i];
        bTab[i] = bTab[i + 1];
        bTab[i + 1] = bTemp;
      }
    }
  }
  if ((iFilterLen & 1) > 0)
  bTemp = bTab[(iFilterLen - 1) / 2];
  else
  bTemp = (bTab[iFilterLen / 2] + bTab[iFilterLen / 2 - 1]) / 2;
  return bTemp;
}

double avergearray(int* arr, int number)
{
  int i;
  int max,min;
  double avg;
  long amount=0;
  if(number<=0)
  {
    Serial.println("Error number for the array to avraging!/n");
    return 0;
  }
  if(number<5)
  {   //less than 5, calculated directly statistics
    for(i=0;i<number;i++)
    {
      amount+=arr[i];
    }
    avg = amount/number;
    return avg;
  }
  else
  {
    if(arr[0]<arr[1])
    {
      min = arr[0];max=arr[1];
    }
    else
    {
      min=arr[1];max=arr[0];
    }
    for(i=2;i<number;i++)
    {
      if(arr[i]<min)
      {
        amount+=min;        //arr<min
        min=arr[i];
      }
      else 
      {
        if(arr[i]>max)
        {
          amount+=max;    //arr>max
          max=arr[i];
        }
        else
        {
          amount+=arr[i]; //min<=arr<=max
        }
      }//if
    }//for
    avg = (double)amount/(number-2);
  }//if
  return avg;
}
