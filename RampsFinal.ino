/*
 * RAMPS 1.4 Shield Arduino for Farming Bot
 * author:      Leon Diel
 * created:     03/16/2021
 * last update: 02/10/2022
 *
 * New Changes since Version 1.2 (06/08/2021)
 *    - Z- and X-Axis are implemented
 *    - Added new library "Servo.h"
 *    - Added new variables and constants (Pins) for the servo motors
 *      used to control the gripper
 *    - "Error Protocol" for the Serial Monitor implemented
 *    
 * New Changes since Version 2.0 (11/29/2021)
 *    - Serial Communication implemented
 *    - Updated Error Protocol
 *    - Input Positions with Serial Monitor
 *    - Removed thread- and servo- declarations
 *    
 * New Changes since Version 2.1 (12/19/2021)
 *    - Implemented Y-Axis
 *    - grab() Method implemented
 *    - relocate() method implemented
 *    - Updated moveto() method
 * 
 * New Changes since Version 3.0 (02/09/2022)
 *    - optimized for the serial communication between Pi and Arduino
 *    - serial outputs commented out to prevent overloading the Pi's serial recieve buffer
 *
 * Before use, please install the following Arduino libraries on your device:
 *    [-]
 * 
 * Protocol for relocate()-function
 *    connected to the Rasperry Pi
 * 
 *    moving example:
 *      Pi sends "10T2"
 *      
 *      10 >> first position, which should be moved
 *      
 *	T >> only a Character to seperatre the positions
 *
 *	2 >> position, to which the plant should be relocated
 *      
 *      Translated:
 *      -> Grab plant on position 10 and relocate it to position 2.
 */

#include <string.h>
#include <stdio.h>

//=================
// PIN DEFINITIONS
//=================


// Steppermotors
#define X_STEP  54
#define Y_STEP  60
#define Z_STEP  46

#define E_STEP  26
//#define G_STEP  36

// Direction Pins
#define X_DIR  55 
#define Y_DIR  61
#define Z_DIR  48

#define E_DIR  28
//#define G_DIR  34

// Enabled Pins
#define X_ENABLE  38
#define Y_ENABLE  56
#define Z_ENABLE  62

#define E_ENABLE  24
//#define G_ENABLE  30

// Limiter Pins
#define END_MIN_X  3
#define END_MAX_X  2
#define END_MIN_Y  14
#define END_MAX_Y  15
#define END_MIN_Z  19
#define END_MAX_Z  18

//====================
// CONSTANTS AND VARS
//====================

// Limiter Integer for Digital Input
int limit_min_x = 0;
int limit_max_x = 0;
int limit_min_y = 0;
int limit_max_y = 0;
int limit_min_z = 0;
int limit_max_z = 0;

// Speeds
const int wait_ms = 350;
const int delaymicro = 375;
const int speed_x = 600;
const int speed_y = 600;
const int speed_homing = 400;
const int speed_grab_x = 900;
const int speed_grab_z = 450;

// Position Vars
int current_x_p = 0;
int new_x_p = 0;
int current_y_p = 0;
int new_y_p = 0;
int current_z_p = 0;
int new_z_p = 0;
int dif = 0;

// Position Arrays
int curr_position_x[] = {current_x_p, new_x_p};
int curr_position_y[] = {current_y_p, new_y_p};
int curr_position_z[] = {current_z_p, new_z_p};

// Step Counter
int count_steps_x = 0;
int count_steps_y = 0;
int count_steps_z = 0;

// Communication Variables
const unsigned int MAX_MESSAGE_LENGTH = 12;
static char message[MAX_MESSAGE_LENGTH];
static unsigned int message_pos = 0;
String msg;

// unsigned int received_position = 0;
unsigned int received_pos_x = 0;
unsigned int received_pos_y = 0;
unsigned int received_pos_z = 0;

// Grab Steps
unsigned int grab_x = 175;
unsigned int grab_z = 400;

//=====================================
// Steps List for easier Communitation
//=====================================
                               //  x     y     z        Schritte
const long STEP_TO_POS[24][3] = { {75, 2075, 2780},     // 0 - Stockwerk 1, Pos 1
                                  {75, 1180, 2715},     // 1 - Stockwerk 1, Pos 2
                                  {1025, 2040, 2775},   // 2 - ...
                                  {1050, 1185, 2675},   // 3
                                  {1970, 2060, 2710},   // 4
                                  {1980, 1170, 2655},   // 5
                                  {90, 2100, 5325},     // 6 - Stockwerk 2, Pos 1
                                  {90, 1200, 5275},     // 7 - Stockwerk 2, Pos 2
                                  {1025, 2090, 5315},   // 8
                                  {1050, 1220, 5250},   // 9
                                  {1990, 2080, 5300},   // 10
                                  {2000, 1200, 5215},   // 11
                                  {90, 2410, 7025},     // 12
                                  {90, 1910, 6990},     // 13
                                  {90, 1435, 6950},     // 14
                                  {90, 970, 6950},      // 15
                                  {1075, 2405, 6995},   // 16
                                  {1075, 1905, 6965},   // 17
                                  {1075, 1430, 6925},   // 18
                                  {1075, 965, 6915},    // 19
                                  {2050, 2410, 7000},   // 20
                                  {2050, 1915, 6960},   // 21
                                  {2075, 1430, 6910},   // 22
                                  {2050, 965, 6875}};   // 23


void setup() {
  
  Serial.begin(9600);
  Serial.println("Setup system ...");
  
  // Step and Dir Pins to Output
  pinMode(X_STEP, OUTPUT);
  pinMode(Y_STEP, OUTPUT);
  pinMode(Z_STEP, OUTPUT);
  pinMode(E_STEP, OUTPUT);
  pinMode(X_DIR, OUTPUT);
  pinMode(Y_DIR, OUTPUT);
  pinMode(Z_DIR, OUTPUT);
  pinMode(E_DIR, OUTPUT);

  pinMode(END_MIN_X, INPUT);
  pinMode(END_MAX_X, INPUT);
  pinMode(END_MIN_Y, INPUT);
  pinMode(END_MAX_Y, INPUT);
  pinMode(END_MIN_Z, INPUT);
  pinMode(END_MAX_Y, INPUT);

  pinMode(X_ENABLE,OUTPUT);
  digitalWrite(X_ENABLE,0);
  pinMode(Y_ENABLE,OUTPUT);
  digitalWrite(Y_ENABLE,0);
  pinMode(Z_ENABLE,OUTPUT);
  digitalWrite(Z_ENABLE,0);
  pinMode(E_ENABLE, OUTPUT);
  digitalWrite(E_ENABLE,0);

  delay(100);
  
  //home_protection_y_undo();
  
  home_y();
  home_x();
  home_z();

  Serial.println("\n   >> Setup completed.");
  //Serial.println("Waiting for instructions...");
  
}

void loop()
{
  //checkSerialData();
  relocate();
  //positioning();   
}

void positioning()
{
  int x = 0;
  int y = 0;
  int z = 0;
  
  Serial.print("Please type X Steps: ");
  while (!Serial.available()) {}
  delay(500);
  x = getSerialData();
  
  delay(500);
  Serial.println(x);

  Serial.print("Please type Y Steps: ");
  while (!Serial.available()) {}
  delay(500);
  y = getSerialData();
  
  delay(500);
  Serial.println(y);

  Serial.print("Please type Z Steps: ");
  while (!Serial.available()) {}
  delay(500);
  z = getSerialData();

  delay(500);
  Serial.println(z);
 
  Serial.println("Your position will be approached...");
  moveto(x, y, z);

  Serial.println("\n================================");
  Serial.println(" Position successfully reached!");
  Serial.println("================================\n");
}

void moveto(int x, int y, int z)
{
  home_y();
  delay(250);
  movezto(z);
  delay(250);
  movexto(x);
  delay(250);
  moveyto(y);
  delay(250);
  //grab(x, y, z);
}

void relocate()
{
//  Serial.println("Please enter the command using the following syntax: ");
//  Serial.println("   old position number + ',' + new position number");
//  Serial.println("\n   Example: from 2 to 12 >> syntax: 2,12\n");
//  Serial.println("Available positions: 6 - 11");
//  Serial.print("Now enter the command: ");
  
  while (!Serial.available()) {}
  delay(250);

  while (Serial.available() > 0)
  {
//    char utf_waste1 = Serial.read();
//    char utf_waste2 = Serial.read();
    unsigned int grab_val = Serial.parseInt();
    char grab_char = Serial.read();
    unsigned int relocate_val = Serial.parseInt();
//    char utf_waste3 = Serial.read();

    delay(250);
    
    Serial.println(grab_val);
    Serial.println(relocate_val);

    delay(200);

    if (Serial.read() == '\n')
    {
      
      //Full message received...
//      Serial.println("Command was read successfully.\n");
//      Serial.print("Moving plant from position ");
//      Serial.print(grab_val);
//      Serial.print(" to position ");
//      Serial.print(relocate_val);
//      Serial.println(" ...");

      //delay(200);

//      Serial.println(STEP_TO_POS[grab_val][0]);
//      Serial.println(STEP_TO_POS[grab_val][1]);
//      Serial.println(STEP_TO_POS[grab_val][2]);
      
      //delay(100);
      
//      Serial.println(STEP_TO_POS[relocate_val][0]);
//      Serial.println(STEP_TO_POS[relocate_val][1]);
//      Serial.println(STEP_TO_POS[relocate_val][2]);
//      
      delay(100);
      
      moveto(STEP_TO_POS[grab_val][0], STEP_TO_POS[grab_val][1], STEP_TO_POS[grab_val][2]);
      delay(100);
      grab();
      delay(50);
      home_x();
      delay(50);
      moveto(STEP_TO_POS[relocate_val][0], STEP_TO_POS[relocate_val][1], (STEP_TO_POS[relocate_val][2] + 400));
      delay(200);
      place();
      delay(200);
//      Serial.print("Plant successfully relocated from position ");
//      Serial.print(grab_val);
//      Serial.print(" to position ");
//      Serial.print(relocate_val);
//      Serial.println(".");
//      Serial.println("Please check the system for possible damage before continue.");
      
    }
    else
    {
      Serial.println("Something failed. Please try again!");
      break;
    }
  }
  delay(250);
  home_y();
  home_x();
  Serial.println("Success");
  return;
}

void grab()
{
  /*
   * Steps:
   *  - x-axis um x Schritte nach rechts
   *  - grab_x auf current_x_p addieren
   *  - z-axis um z Schritte nach oben
   *  - grab_z auf currentz_p addieren
   *  - x-axis um x Schritte nach links
   *  - grab_x von current_x_p subtrahieren
   *  - home y
   */

  // x-axis um x Schritte nach rechts
  digitalWrite(X_DIR, LOW);
    
  for (int i = 0; i < grab_x; i++)
  {
    digitalWrite(X_STEP, HIGH);
    delayMicroseconds(speed_grab_x);

    digitalWrite(X_STEP, LOW);
    delayMicroseconds(speed_grab_x);
  }
  current_x_p = current_x_p + grab_x;
  delay(250);
  
  // z-axis um z Schritte nach oben
  digitalWrite(Z_DIR, HIGH);
  digitalWrite(Y_DIR, LOW);

  for (int i = 0; i < grab_z; i++)
  {
    digitalWrite(Z_STEP, HIGH);
    delayMicroseconds(speed_grab_z);

    digitalWrite(Z_STEP, LOW);
    delayMicroseconds(speed_grab_z);

    digitalWrite(Y_STEP, HIGH);
    delayMicroseconds(speed_grab_z);

    digitalWrite(Y_STEP, LOW);
    delayMicroseconds(speed_grab_z);
  }
  current_z_p = current_z_p + grab_z;
  delay(250);

  // x-axis um x Schritte nach links
  digitalWrite(X_DIR, HIGH);
    
  for (int i = 0; i < grab_x; i++)
  {
    digitalWrite(X_STEP, HIGH);
    delayMicroseconds(speed_grab_x);

    digitalWrite(X_STEP, LOW);
    delayMicroseconds(speed_grab_x);
  }
  current_x_p = current_x_p - grab_x;
  delay(250);

  home_y();

  // z-axis um z Schritte nach unten
  digitalWrite(Z_DIR, LOW);
  digitalWrite(Y_DIR, HIGH);

  for (int i = 0; i < grab_z; i++)
  {
    digitalWrite(Z_STEP, HIGH);
    delayMicroseconds(speed_grab_z);

    digitalWrite(Z_STEP, LOW);
    delayMicroseconds(speed_grab_z);

    digitalWrite(Y_STEP, HIGH);
    delayMicroseconds(speed_grab_z);

    digitalWrite(Y_STEP, LOW);
    delayMicroseconds(speed_grab_z);
  }
  current_z_p = current_z_p - grab_z;

  delay(250);
  //Serial.println("Succesfully approached and grabbed.");
}

void place()
{
  /*
   * Steps:
   *  - x-axis um x Schritte nach rechts
   *  - grab_x auf current_x_p addieren
   *  - z-axis um z Schritte nach unten
   *  - grab_z von currentz_p subtrahieren
   *  - x-axis um x Schritte nach links
   *  - grab_x von current_x_p subtrahieren
   *  - home y
   */
  
  // x-axis um x Schritte nach rechts
  digitalWrite(X_DIR, LOW);
    
  for (int i = 0; i < (grab_x+50); i++)
  {
    digitalWrite(X_STEP, HIGH);
    delayMicroseconds(speed_grab_x);

    digitalWrite(X_STEP, LOW);
    delayMicroseconds(speed_grab_x);
  }
  current_x_p = current_x_p + (grab_x+50);
  delay(250);
  
  // z-axis um z Schritte nach unten
  digitalWrite(Z_DIR, LOW);
  digitalWrite(Y_DIR, HIGH);

  for (int i = 0; i < (grab_z-25); i++)
  {
    digitalWrite(Z_STEP, HIGH);
    delayMicroseconds(speed_grab_z);

    digitalWrite(Z_STEP, LOW);
    delayMicroseconds(speed_grab_z);

    digitalWrite(Y_STEP, HIGH);
    delayMicroseconds(speed_grab_z);

    digitalWrite(Y_STEP, LOW);
    delayMicroseconds(speed_grab_z);
  }
  current_z_p = current_z_p + (grab_z - 25);
  delay(250);

  // x-axis um x Schritte nach links
  digitalWrite(X_DIR, HIGH);
    
  for (int i = 0; i < (grab_x+75); i++)
  {
    digitalWrite(X_STEP, HIGH);
    delayMicroseconds(speed_grab_x);

    digitalWrite(X_STEP, LOW);
    delayMicroseconds(speed_grab_x);
  }
  current_x_p = current_x_p - grab_x - 75;
  delay(250);

  home_y();
  home_x();
  home_z();
  //Serial.print("Done.");
}

void checkSerialData()
{
  Serial.print("\nEnter your instruction: ");
  while (!Serial.available()) {}
  delay(500);
  while (Serial.available() > 0)
  {
    static char message[MAX_MESSAGE_LENGTH];
    static unsigned int message_pos = 0;

    char inByte = Serial.read();

    if ( inByte != '\n' && (message_pos < MAX_MESSAGE_LENGTH - 1) )
    {
      message[message_pos] = inByte;
      message_pos++;
    }
    //Full message received...
    else
    {
      message[message_pos] = '\0';
      message_pos = 0;
      msg = message;
      Serial.println(msg);
    }
  }
  if (msg == "pos")
  {
    positioning();
  }
  else if (msg == "homex")
  {
    home_x();
  }
  else if (msg == "homey")
  {
    home_y();
  }
  else if (msg == "homez")
  {
    home_z();
  }
  else if (msg == "home")
  {
    home_y();
    delay(200);
    home_x();
    delay(200);
    home_z();
  }
  else if (msg == "grab")
  {
    grab(); 
  }
  else if (msg == "relocate")
  {
    relocate();
  }
  else if (msg == "place")
  {
    place();
  }
  else if (msg == "secy")
  {
    home_protection_y();
  }
  else if (msg == "undo_sec")
  {
    home_protection_y_undo();
  }
  else if (msg == "help")
  {
    Serial.println("Here is a list of commands...\n");
    Serial.println("  - grab :      Grab the current position. Before use, use 'pos'.");
    Serial.println("  - help :      A list of all possible instructions.");
    Serial.println("  - home :      Home all axis.");
    Serial.println("  - homex :     Home x axis (and y).");
    Serial.println("  - homey :     Home y axis.");
    Serial.println("  - homez :     Home x axis (and y).");
    Serial.println("  - place :     Place the grabbed plant to the manual navigated position. Before use, use 'pos'.");
    Serial.println("  - pos :       Approache a position.");
    Serial.println("  - relocate :  Relocate the grabbed plant; before use, use 'pos'.");
    Serial.println("  - secy :      Secure y - axis.");
    Serial.println("  - undo_sec :  Undo secure y - axis.");
  }
  else
  {
    Serial.println("Error 01: Unknown input. Check the intype or type 'help' for a list of all commands.");
  }
  delay(500);
}

unsigned int getSerialData()
{
  while (Serial.available() > 0)
  {
    static char message[MAX_MESSAGE_LENGTH];
    static unsigned int message_pos = 0;

    char inByte = Serial.read();

    if ( inByte != '\n' && (message_pos < MAX_MESSAGE_LENGTH - 1) )
    {
      if (inByte == "")
      {
        message[message_pos] = inByte;
        message[(message_pos + 1)] = '\0';
        message_pos = 0;
        int coordinate = -1;
        
        return coordinate;
      }
      else
      {
        message[message_pos] = inByte;
        message_pos++;
      }
    }
    //Full message received...
    else
    {
      int coordinate = 0;
      message[message_pos] = '\0';
      coordinate = atoi(message);

      message_pos = 0;
      return coordinate;
    }
  }
}

void moveyto(int storey)
{ 
  if (storey > 2500)
  {
    Serial.println("Error 03: Number of steps for 'Y' too high \nor the position is not available, yet.");
    return;
  }
  else if (storey < 2500)
  {
//    Serial.print("Moving Y Axis to ");
//    Serial.print(storey);
//    Serial.println("...");
    
    digitalWrite(E_DIR, HIGH);
    count_steps_y = 0;
    
    for (int i = 0; i < storey; i++)
    {
      digitalWrite(E_STEP, HIGH);
      delayMicroseconds(speed_y);
      
      digitalWrite(E_STEP, LOW);
      delayMicroseconds(speed_y);
      
      count_steps_y++;
    }
    //Serial.println("Y position successfully reached.");
    //Serial.print(count_steps_y);
    //Serial.println(" steps needed.");
  }
  else
  {
    Serial.println("Error 03.1: Something failed. Please check your intype.");
    return;
  }
}

void movexto(int storey)
{ 
  if (storey > 2900)
  {
    Serial.println("Error 02: Number of steps for 'X' too high \nor the position is not available, yet.");
    return;
  }
//  Serial.print("Moving X Axis to ");
//  Serial.print(storey);
//  Serial.println("...");
        
  new_x_p = storey;
  curr_position_x[1] = new_x_p;
  //Serial.println("CurrPos[1]:");
  //Serial.println(curr_position_x[1]);
  current_x_p = curr_position_x[0];

  if ((curr_position_x[1]) > (curr_position_x[0]))
  {
    dif = (curr_position_x[1] - curr_position_x[0]);
    digitalWrite(X_DIR, LOW);
    count_steps_x = 0;
    
    for (int i = 0; i < dif; i++)
    {
      digitalWrite(X_STEP, HIGH);
      delayMicroseconds(speed_x);

      digitalWrite(X_STEP, LOW);
      delayMicroseconds(speed_x);
      
      count_steps_x++;
    }
    curr_position_x[0] = curr_position_x[1];
    //Serial.println("Array 0: ");
    //Serial.println(curr_position_x[0]);
    //Serial.println("X position successfully reached.");
    //Serial.print(count_steps_x);
    //Serial.println(" steps needed.");
  }
  else if ((curr_position_x[1]) < (curr_position_x[0]))
  {
    dif = (curr_position_x[0] - curr_position_x[1]);
    digitalWrite(X_DIR, HIGH);
    count_steps_x = 0;
    
    for (int i = 0; i < dif; i++)
    {
      digitalWrite(X_STEP, HIGH);
      delayMicroseconds(speed_x);

      digitalWrite(X_STEP, LOW);
      delayMicroseconds(speed_x);

      count_steps_x++;
    }
    curr_position_x[0] = curr_position_x[1];
    //Serial.println("X position successfully reached.");
    //Serial.print(count_steps_x);
    //Serial.println(" steps needed.");
  }
  else if ((curr_position_x[1]) == (curr_position_x[0]))
  {
    //Serial.println("X position already reached!");
  }
  else if ((curr_position_x[1]) == (-1))
  {
    //Serial.println("X position already reached!");
  }
  else
  {
    Serial.println("Error 02.1: Something failed the 'curr_position_x'-Array. Please check your intype.");
    return;
  }
}

void movezto(int storey)
{
  if (storey > 7800)
  {
    Serial.println("Error 04: Number of steps for 'Z' too high \nor the position is not available, yet.");
    return;
  }
  
//  Serial.print("Moving Z Axis to ");
//  Serial.print(storey);
//  Serial.println("...");
        
  new_z_p = storey;
  curr_position_z[1] = new_z_p;
  //Serial.println("CurrPos[1]:");
  //Serial.println(curr_position_z[1]);
  current_z_p = curr_position_z[0];

  if ((curr_position_z[1]) > (curr_position_z[0]))
  {
    dif = (curr_position_z[1] - curr_position_z[0]);
    digitalWrite(Z_DIR, HIGH);
    digitalWrite(Y_DIR, LOW);
    count_steps_z = 0;
    
    for (int i = 0; i < dif; i++)
    {
      digitalWrite(Z_STEP, HIGH);
      delayMicroseconds(delaymicro);

      digitalWrite(Z_STEP, LOW);
      delayMicroseconds(delaymicro);

      digitalWrite(Y_STEP, HIGH);
      delayMicroseconds(delaymicro);

      digitalWrite(Y_STEP, LOW);
      delayMicroseconds(delaymicro);
      count_steps_z++;
    }
    curr_position_z[0] = curr_position_z[1];
    //Serial.println("Array 0: ");
    //Serial.println(curr_position_z[0]);
    //Serial.println("Z position successfully reached.");
    //Serial.print(count_steps_z);
    //Serial.println(" steps needed.");
  }
  else if ((curr_position_z[1]) < (curr_position_z[0]))
  {
    dif = (curr_position_z[0] - curr_position_z[1]);
    digitalWrite(Z_DIR, LOW);
    digitalWrite(Y_DIR, HIGH);
    count_steps_z = 0;
    
    for (int i = 0; i < dif; i++)
    {
      digitalWrite(Z_STEP, HIGH);
      delayMicroseconds(delaymicro);

      digitalWrite(Z_STEP, LOW);
      delayMicroseconds(delaymicro);

      digitalWrite(Y_STEP, HIGH);
      delayMicroseconds(delaymicro);

      digitalWrite(Y_STEP, LOW);
      delayMicroseconds(delaymicro);
      count_steps_z++;
    }
    curr_position_z[0] = curr_position_z[1];
    //Serial.println("Z position successfully reached.");
    //Serial.print(count_steps_z);
    //Serial.println(" steps needed.");
  }
//  else if ((curr_position_z[1]) == (curr_position_z[0]))
//  {
//    //Serial.println("Z position already reached!");
//  }
//  else if ((curr_position_z[1]) == (-1))
//  {
//    //Serial.println("Z position already reached!");
//  }
  else
  {
    Serial.println("Error 04.3: Something failed the 'curr_position_z'-Array. Please check your intype.");
    return;
  }
}

void home_x()
{
  home_y();
  
  digitalWrite(X_DIR, HIGH);
  //Serial.println("Homing X...");
  
  limit_min_x = digitalRead(END_MIN_X);
  while (limit_min_x == 1)
  {
    limit_min_x = digitalRead(END_MIN_X);

    digitalWrite(X_STEP, HIGH);
    delayMicroseconds(speed_x);
    
    digitalWrite(X_STEP, LOW);
    delayMicroseconds(speed_x);
  }
  curr_position_x[0] = 0;
  curr_position_x[1] = 0;
  Serial.println("X-Homed.");
  //digitalWrite(X_ENABLE, 1);
  delay(100);
}

void home_y()
{
  // LOW >> Back, HIGH >> Forth
  digitalWrite(E_DIR, LOW);
  //Serial.println("Homing Y...");
  
  limit_min_y = digitalRead(END_MIN_Y);
  while (limit_min_y == 1)
  {
    limit_min_y = digitalRead(END_MIN_Y);

    digitalWrite(E_STEP, HIGH);
    delayMicroseconds(speed_y);
    
    digitalWrite(E_STEP, LOW);
    delayMicroseconds(speed_y);
  }
  curr_position_y[0] = 0;
  curr_position_y[1] = 0;
  Serial.println("Y-Homed.");
  delay(100);
}

void home_z()
{
  home_y();
  
  digitalWrite(Z_DIR, LOW);
  digitalWrite(Y_DIR, HIGH);
  //Serial.println("Homing Z...");

  limit_min_z = digitalRead(END_MIN_Z);
  while (limit_min_z == 1)
  {
    limit_min_z = digitalRead(END_MIN_Z);

    digitalWrite(Z_STEP, HIGH);
    delayMicroseconds(speed_homing);
    
    digitalWrite(Z_STEP, LOW);
    delayMicroseconds(speed_homing);
    
    digitalWrite(Y_STEP, HIGH);
    delayMicroseconds(speed_homing);
    
    digitalWrite(Y_STEP, LOW);
    delayMicroseconds(speed_homing);
  }
  curr_position_z[0] = 0;
  curr_position_z[1] = 0;
  Serial.println("Z-Homed.");
  //digitalWrite(Y_ENABLE,1);
  //digitalWrite(Z_ENABLE,1);
  delay(100);
}

void home_protection_y()
{  
  digitalWrite(Z_DIR, HIGH);
  digitalWrite(Y_DIR, LOW);
  Serial.println("Protection of the y axis...");

  for (int i = 0; i < 200; i++)
  {
    digitalWrite(Z_STEP, HIGH);
    delayMicroseconds(500);
    
    digitalWrite(Z_STEP, LOW);
    delayMicroseconds(500);
    
    digitalWrite(Y_STEP, HIGH);
    delayMicroseconds(500);
    
    digitalWrite(Y_STEP, LOW);
    delayMicroseconds(500);
  }
  curr_position_z[0] = 200;
  curr_position_z[1] = 200;
  Serial.println("Z-height reached.");

  delay(100);
  
  // LOW >> Back, HIGH >> Forth
  digitalWrite(E_DIR, HIGH);
  Serial.println("Protecting y-axis...");
  
  for (int i = 0; i < 2500; i++)
  {
    digitalWrite(E_STEP, HIGH);
    delayMicroseconds(700);
    
    digitalWrite(E_STEP, LOW);
    delayMicroseconds(700);
  }
  curr_position_y[0] = 2500;
  curr_position_y[1] = 2500;
  Serial.println("Y-axis protected.");
  delay(100);
}

void home_protection_y_undo()
{  
  digitalWrite(Z_DIR, HIGH);
  digitalWrite(Y_DIR, LOW);
  Serial.println("Undo protection of the y axis...");

  for (int i = 0; i < 400; i++)
  {
    digitalWrite(Z_STEP, HIGH);
    delayMicroseconds(500);
    
    digitalWrite(Z_STEP, LOW);
    delayMicroseconds(500);
    
    digitalWrite(Y_STEP, HIGH);
    delayMicroseconds(500);
    
    digitalWrite(Y_STEP, LOW);
    delayMicroseconds(500);
  }
  curr_position_z[0] = 600;
  curr_position_z[1] = 600;
  Serial.println("Z-height reached.");

  delay(100);
  
  // LOW >> Back, HIGH >> Forth
  home_y();
  home_z();
  Serial.println("Successfully undo protection.");
  delay(100);
}
