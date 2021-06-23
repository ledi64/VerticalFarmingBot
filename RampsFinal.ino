/*
 * RAMPS 1.4 Shield Arduino for Farming Bot
 * author:      Leon Diel
 * date:        16/03/2021
 * last update: 23/06/2021
 * 
 * This code allows the robot to travel to specific positions (steps).
 * The USB-Serialcommunication between Pi and Uno is not implemented, yet.
 * 
 * New Changes since Version 1.2 (08.06.2021)
 *    - Z and X Axis are implemented
 *    - Added new library "Servo.h"
 *    - Added new variables and constants (Pins) for the servo motors
 *      used to control the gripper
 *    - "Error Protocol" for the Serial Monitor implemented
 * 
 * Before use, please install the following Arduino libraries on your device:
 *    ArduinoThread   <Thread.h>
 * 
 */

#include <string.h>
#include <Thread.h>
#include <Servo.h>

//==================
// Achsen in Zahlen
//    x   1
//    y   2
//    z   3
//==================

//=================
// PIN DEFINITIONS
//=================

// Steppermotors
#define X_STEP  54
#define Y_STEP  60
#define Z_STEP  46

#define E_STEP  26
#define G_STEP  36

// Direction Pins
#define X_DIR  55
#define Y_DIR  61
#define Z_DIR  48

#define E_DIR  28
#define G_DIR  34

// Enabled Pins
#define X_ENABLE  38
#define Y_ENABLE  56
#define Z_ENABLE  62

#define E_ENABLE  24
#define G_ENABLE  30

// Limiter Pins
#define END_MIN_X  3
#define END_MAX_X  2
#define END_MIN_Y  14
#define END_MAX_Y  15
#define END_MIN_Z  18
#define END_MAX_Z  19

// Pins für Magnetschalter zur horizontalen Orientierung
#define FLOOR_0     16
#define FLOOR_1     17
#define FLOOR_2     23
#define FLOOR_3     25

// Servo-Pins
#define SERVO_ROTATE   11
#define SERVO_LEFT     6
#define SERVO_RIGHT    5
#define SERVO_GRAB     4

//========
// Arrays
//========

// booking[floor][position]
unsigned booking[4][8];

// Koordinatensystem
// z Stockwerke
// x Positionen pro Stockwerk
//       system_zx[z][x]
unsigned system_zx[4][6];

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

// Define other constants
const int wait_ms = 250;
const int delaymicro = 250;
const int speed_x = 550;
const int steps = 5000;
const int speed_homing = 450;

int fl0, fl1, fl2, fl3 = 0;
int floor_array[] = {0, 0, 0, 0};

// Position Vars
int current_x_p = 0;
int new_x_p = 0;
int current_z_p = 0;
int new_z_p = 0;
int dif = 0;

// Position Arrays
int curr_position_x[] = {current_x_p, new_x_p};
int curr_position_z[] = {current_z_p, new_z_p};

// Step Counter
int count_steps_x = 0;
int count_steps_z = 0;

// Kommunikationsvariable
char received = ' ';

bool boool = true;

// Threads
Thread LimitThread = Thread();
Thread ComThread = Thread();
Thread MovingThread = Thread();

void setup() {
  // Step and Dir Pins to Output
  pinMode(X_STEP, OUTPUT);
  pinMode(Y_STEP, OUTPUT);
  pinMode(Z_STEP, OUTPUT);
  
  pinMode(X_DIR, OUTPUT);
  pinMode(Y_DIR, OUTPUT);
  pinMode(Z_DIR, OUTPUT);

  pinMode(END_MIN_X, INPUT);
  pinMode(END_MAX_X, INPUT);
  pinMode(END_MIN_Y, INPUT);
  pinMode(END_MAX_Y, INPUT);
  pinMode(END_MIN_Z, INPUT);
  pinMode(END_MAX_Y, INPUT);

  pinMode(FLOOR_0, INPUT);
  pinMode(FLOOR_1, INPUT);
  pinMode(FLOOR_2, INPUT);
  pinMode(FLOOR_3, INPUT);

  pinMode(X_ENABLE,OUTPUT);
  digitalWrite(X_ENABLE,0);
  pinMode(Y_ENABLE,OUTPUT);
  digitalWrite(Y_ENABLE,0);
  pinMode(Z_ENABLE,OUTPUT);
  digitalWrite(Z_ENABLE,0);

  //fl0 = digitalRead(FLOOR_0);
  //fl1 = digitalRead(FLOOR_1);
  //fl2 = digitalRead(FLOOR_2);
  //fl3 = digitalRead(FLOOR_3);

  //floor_array[0] = fl0;
  //floor_array[1] = fl1;
  //floor_array[2] = fl2;
  //floor_array[3] = fl3;

  Serial.begin(9600);

  LimitThread.onRun(limit);
  LimitThread.setInterval(100);
  //ComThread.onRun(communicate);
  //ComThread.setInterval(100);
  MovingThread.onRun(movebot);
  MovingThread.setInterval(100);

  Servo Srotate;
  Servo Sleft;
  Servo Sright;
  Servo Sgrab;

  Srotate.attach(SERVO_ROTATE);
  Sleft.attach(SERVO_LEFT);
  Sright.attach(SERVO_RIGHT);
  Sgrab.attach(SERVO_GRAB);

  home_x();
  home_z();
  //home_gripper();
  
}

void loop()
{
  
  //ComThread.run();
  //LimitThread.run();
  //MovingThread.run();
  
  while (boool == true)
  {
    movebot();  

    

    
    boool = false;
  }
}

void movebot()
{
  Serial.println("Void Movebot...");
  delay(500);
  Serial.println("Z 3000");
  Serial.println("X 1500");
  moveto(1500, 0, 3000);
  delay(1000);
  Serial.println("Z 5000");
  Serial.println("X 2000");
  moveto(2000, 0, 5000);
  delay(1000);
  Serial.println("Z 1500");
  Serial.println("X 1000");
  moveto(1000, 0, 1500);
  delay(1000);
  Serial.println("Z 4000");
  Serial.println("X 1250");
  moveto(1250, 0, 4000);
  delay(1000);
  Serial.println("Z 6000");
  Serial.println("X 500");
  moveto(500, 0, 6000);
  delay(1000);
  Serial.println("Z 5500");
  Serial.println("X 2000");
  moveto(2000, 0, 5500);
  delay(1000);

  home_x();
  home_z();
  
  
}

void moveto(int x, int y, int z)
{
  movezto(z);
  delay(200);
  movexto(x);
}


void movexto(int storey)
{ 
  if (storey > 3000)
  {
    Serial.println("Error 01: Number of Steps too high \nor the position not available, yet.");
    return;
  }
  Serial.print("Moving X Axis to");
  Serial.print(storey);
  Serial.println("...");
        
  new_x_p = storey;
  curr_position_x[1] = new_x_p;
  Serial.println("CurrPos[1]:");
  Serial.println(curr_position_x[1]);
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
    Serial.println("Array 0: ");
    Serial.println(curr_position_x[0]);
    Serial.println("X Position wurde angefahren.");
    Serial.print(count_steps_x);
    Serial.println(" Anzahl Schritte notwendig.");
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
    Serial.println("X Position wurde angefahren.");
    Serial.print(count_steps_x);
    Serial.println(" Anzahl Schritte notwendig.");
  }
  else if ((curr_position_x[1]) == (curr_position_x[0]))
  {
    Serial.println("X Position ist bereits angefahren.");
  }
  else
  {
    Serial.println("Error 02.1: Something failed the 'curr_position_x'-Array. Please check your intype.");
    return;
  }
}

void movezto(int storey)
{
  if (storey > 7587)
  {
    Serial.println("Error 01: Number of Steps too high \nor the position not available, yet.");
    return;
  }
  
  Serial.print("Moving Z Axis to");
  Serial.print(storey);
  Serial.println("...");
        
  new_z_p = storey;
  curr_position_z[1] = new_z_p;
  Serial.println("CurrPos[1]:");
  Serial.println(curr_position_z[1]);
  current_z_p = curr_position_z[0];

  if ((curr_position_z[1]) > (curr_position_z[0]))
  {
    dif = (curr_position_z[1] - curr_position_z[0]);
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
    Serial.println("Array 0: ");
    Serial.println(curr_position_z[0]);
    Serial.println("Z Position wurde angefahren.");
    Serial.print(count_steps_z);
    Serial.println(" Anzahl Schritte notwendig.");
  }
  else if ((curr_position_z[1]) < (curr_position_z[0]))
  {
    dif = (curr_position_z[0] - curr_position_z[1]);
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
    Serial.println("Z Position wurde angefahren.");
    Serial.print(count_steps_z);
    Serial.println(" Anzahl Schritte notwendig.");
  }
  else if ((curr_position_z[1]) == (curr_position_z[0]))
  {
    Serial.println("Z Position ist bereits angefahren.");
  }
  else
  {
    Serial.println("Error 02.3: Something failed the 'curr_position_z'-Array. Please check your intype.");
    return;
  }
}

void grab_position()
{
  
}


void home_x()
{
  digitalWrite(X_DIR, HIGH);
  Serial.println("Homing X...");
  
  limit_min_x = digitalRead(END_MIN_X);
  while (limit_min_x == 1)
  {
    limit_min_x = digitalRead(END_MIN_X);

    digitalWrite(X_STEP, HIGH);
    delayMicroseconds(speed_homing);
    
    digitalWrite(X_STEP, LOW);
    delayMicroseconds(speed_homing);
  }
  curr_position_x[0] = 0;
  curr_position_x[1] = 0;
  Serial.println("X-Homed.");
  //digitalWrite(X_ENABLE, 1);
  delay(500);
}

void home_z()
{
  //digitalWrite(Y_ENABLE,0);
  //digitalWrite(Z_ENABLE,0);
  digitalWrite(Z_DIR, HIGH);
  digitalWrite(Y_DIR, LOW);
  Serial.println("Homing Z...");

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
  delay(500);
}

void home_rotate_servo()
{
  
}

void home_gripper()
{
  Serial.println("Homing Gripper...");
  
  home_rotate_servo();

  Serial.println("Gripper homed.");
}

void xtest()
{
  digitalWrite(X_DIR, LOW);
  
  for (int i = 0; i < 1000; i++)
  {

    digitalWrite(X_STEP, HIGH);
    delayMicroseconds(speed_homing);
    
    digitalWrite(X_STEP, LOW);
    delayMicroseconds(speed_homing);
  }
  digitalWrite(X_DIR, HIGH);
  
  for (int i = 0; i < 1000; i++)
  {

    digitalWrite(X_STEP, HIGH);
    delayMicroseconds(speed_homing);
    
    digitalWrite(X_STEP, LOW);
    delayMicroseconds(speed_homing);
  }
}

void limit()
{
  limit_min_z = digitalRead(END_MIN_Z);
  limit_max_z = digitalRead(END_MAX_Z);
  limit_min_x = digitalRead(END_MIN_X);
  limit_max_x = digitalRead(END_MAX_X);

  if (limit_min_z == 0)
  {
    digitalWrite(Z_DIR, HIGH);
    digitalWrite(Y_DIR, LOW);

    home_z();
  }
  if (limit_max_z == 0)
  {
    digitalWrite(Z_DIR, LOW);
    digitalWrite(Y_DIR, HIGH);
  }
  if (limit_min_x == 0)
  {
    digitalWrite(X_DIR, HIGH);
  }
  if (limit_max_x == 0)
  {
    digitalWrite(X_DIR, LOW);

    home_x();
  }
}
