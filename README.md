# VerticalFarmingBot
This is the Code for the Vertical Farming Bot (Cartesian, Bachelor thesis), the Monitoring-Code (Arduino) for the Vertical Farming system and the GUI to control the bot and the parameters of the farm.

The robot code, written in C/C++, is named "RampsFinal.ino" and needs to be uploaded on an Arduino Mega
The monitoring code, written in C/C++ as well, for the sensors is named "Monitoring.ino" and needs to be uploaded on an Arduino Uno
The GUI file is written in Python and is seperated into mutiple code-files. They can be opend on the Raspberry Pi. Before running the GUI, some libraries must first be installed. The documentation can be found in the file "Documentation.pdf" (coming soon).

New Changes since Version 3.0 (02/09/2022)
- optimized for serial communication between Pi and Arduino
- serial outputs commented out to prevent overloading the Pi's serial receive buffer
    
#############################################################################


Hello,
thank you for reading this. You can find the .ino - Sketch for an Arduino Mega.

Before using, make sure to install the following Libraries in the Arduino IDE:
  - //

The Code is always in developement, so stay tuned. A documentation (in German) will follow.

If there are any questions, please do not hesitate to contact me!

Enjoy.

#############################################################################

Hallo,
vielen Dank fürs' Lesen. Im Repository findest du die .ino Datei für einen Arduino Mega.

Bevor du starten kannst, stelle sicher, dass du die folgenden Bibliotheken in der Arduino IDE installiert hast:
  - //

Der Code wird stets weiterentwickelt, also bleibe auf dem Laufenden. Eine Dokumentation folgt.

Bei Fragen, zögere nicht mich zu kontaktieren!

Viel Spaß!
