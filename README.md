# Credits
ili9341 and xtp2046 libraries source: https://github.com/rdagger/micropython-ili9341/tree/master \
HSV2RGB function in pixAnimations source: https://toptechboy.com/convert-hsv-to-rgb-in-micropython/ (This function was modfied by me) \
All the other code was written by me. \
AI was only used in the debugging process to catch mistakes, however after diagnostics it **was not used to fix the mistake** (generate working code). It was used to generate debug scripts. **No part of the debug scripts is used in the main code.**
# Project description
This is a NeoPixel strip controller with 12 different modes that uses TFT display with touchscreen as a main control element. It also features a brightness potentiometer and a button. \
I created it as a decoration for my room.
## Basic control
### Button
When you shortly(t<1s) press and release a button you can exit numeric keyboard, color picker or mode picker. You will return back to modes settings. \
When you longly (2s<t<10s) press and then release a button you will turn off a neopixel mode (if it is running), then a turn off animation will be executed and the stip will remain dark.
### Bightness potentiometer
You can adjust the strip brightness by turning the brightness potentiometer. It works on all modes. \
The brightness will be adjusted using software, not by limiting the NeoPixel supply voltage.
### Display UI
The main display UI (mode settings) is used to adjust mode parameters and run the modes. \
*(In future it is planned also to contain Alarm Clock settings and PIR sensor settings. This features are not implemeted yet.)* \
Elements of the main display UI (mode settings): \
  -Date and time (top of the display). It displays local time *(more about time synchronization it the system design section)*, date, and weekday. \
  -Box with current mode. After clicking on the box you will enter the mode picker. \
  -Parameter lines, which consist of parameter name and a box with parameter value. After clicking on the box you will enter numeric keyboard if it is a numeric parameter, or it will change to the next value in case of non numeric parameter ( e.g. True -> False, linear->exponential). \
  -Color boxes, which are boxes filled with their current color and text describing which color is it (1st or 2nd). After clicking on one of the boxes you will enter the color picker. \
  Images: \
<img width="306" height="408" alt="20261031_175559" src="https://github.com/user-attachments/assets/801b67d0-921b-45ac-9b29-fa207ae425af" /> <img width="306" height="408" alt="20261031_175428" src="https://github.com/user-attachments/assets/d6db9fff-172f-4bf4-ba4f-35149beb2a6e" />

#### Color picker
It is display UI used for selecting UI. \
Elements of the color picker: \
-Selected color shower, the selected color will be displayed as a box on the top of the display. Also the whole led strip will light up with the selected color. The brightness of the led strip can be changed by the brightness potentiometer and it will no affect the selected color. (Brightness isn't stored as a color parameter) \
-Color wheel. It is basiccally the color pallete you can choose from. By clicking on it you can select the color. \
-Confirm button/box. It is located in bottom right corner after clicking on it it will save the color and the display will switch back to modes settings. \
The system uses hue and  saturation to store and manipulate with the color. \
The color picker UI takes a lot of time to render (approx. 20s), this is because the color wheel is not stored as an image, instead is is computed using trigonometry. To save RAM and prevent the system from collapsing it is computed and then uploaded to the display in blocks, and that is the reason why it takes so long. \
Images: \
<img width="306" height="408" alt="20261031_181654" src="https://github.com/user-attachments/assets/c3139403-b48a-4923-8c09-ac211d9a231a" />
<img width="306" height="408" alt="20261031_181658" src="https://github.com/user-attachments/assets/a67ee67c-1c68-442f-81e4-69233622b52f" />
#### Numeric keyboard
It is a dislay UI used to select numeric parameter values. \
Elements of the numeric keyboard: \
-Current number box. It is blank at start, after that is is used to display the currently selected number. If you are trying to confirm an invalid number the invalid number will be deleted and the accepted range will be displayed in this box. Curent number box does not react to touch. \
-Digits boxed are boxes containing a digit, they create the keypad. After clicking the box the digit will be added to the end of the current number. \
-C button, is a box containing the letter C. After clicking it the last digit of the  number will be deleted. \
-OK button, is a box containing letters OK. After clicking it the current number will be verified if it is valid, if it is, the value of a parameter will be updated and the display will be switched back to modes settings if it is not, the current number will be deleted and an error message specifying the corrent range will be displayed in the current number box, the display will remain in the numeric keyboard UI. \
Images: \
<img width="306" height="408" alt="20261031_183616" src="https://github.com/user-attachments/assets/7fd9781b-4354-4fdc-899c-39d782597c3e" />
<img width="306" height="408" alt="20261031_183608" src="https://github.com/user-attachments/assets/e741f87c-2078-4426-9f5f-253334c7f1dc" />
#### Mode picker
## Modes description and parameters
## Parameters description
## System design


