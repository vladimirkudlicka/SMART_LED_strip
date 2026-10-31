
https://github.com/user-attachments/assets/451d4137-06df-42a3-a8c1-64a2d4a974d6

https://github.com/user-attachments/assets/3270fa61-b3d4-4a4b-9e82-4c4ba58e1e24
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
  -Run mode box, it is a box at the bottom of the screen containing the text Run mode. After clicking on it, the neopixel mode which settings are displayed will be run. \
  Images: \
<img width="306" height="408" alt="20261031_175559" src="https://github.com/user-attachments/assets/801b67d0-921b-45ac-9b29-fa207ae425af" /> <img width="306" height="408" alt="20261031_175428" src="https://github.com/user-attachments/assets/d6db9fff-172f-4bf4-ba4f-35149beb2a6e" />

#### Color picker
It is display UI used for selecting UI. \
Elements of the color picker: \
-Selected color shower, the selected color will be displayed as a box on the top of the display. Also the whole led strip will light up with the selected color. The brightness of the led strip can be changed by the brightness potentiometer and it will no affect the selected color. (Brightness isn't stored as a color parameter) \
-Color wheel. It is basiccally the color pallete you can choose from. By clicking on it you can select the color. \
-Confirm button/box. It is located in bottom right corner after clicking on it it will save the color and the display will switch back to modes settings. \
The system uses hue and  saturation to store and manipulate with the color. \
Before this UI is loaded the running neopixel mode is terminated and the strip is turned off, so that it can be used to show color preview. After returning back to the modes settings you will have to manually 
re-run neopixel mode, since the strip will be turned off. \
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
It is a display UI used for selecting which mode's setting are you going to modify. \
By selecting the mode you will not run the neopixel mode. You can only select which mode's parameters are you changing. You can only run modes using the Run mode button in the mode settings. \
This UI consists of a list of settings tabs names/mode names. By clicking on one mode/settings tab name you will enter its settings. \
Image: \
<img width="306" height="408" alt="20261031_185819 (1)" src="https://github.com/user-attachments/assets/3a1484a0-af12-4776-9d7c-7499a3443e2a" /> \
*You can see that there are 2 settings tabs that are not neopixel modes: alarm setting and PIR settings. These are setting tabs for future features that are not implemented yet.*
## Modes description
### White
The NeoPixel strip  is filled with white color, which temperature you can adjust. You can optionaly turn on fading (periodic change of brighntness). \
Parameters: fading active; fading type; minimal brightness; (fading) speed; temperature \
Image:\
<img width="408" height="306" alt="20261031_191740" src="https://github.com/user-attachments/assets/deb19832-00ec-42be-a907-d5748f9e2cb3" />
### Monocolor 
The NeoPixel strip is filled with one color, you can select. You can optionaly turn on fading (periodic change of brighntness). \
Parameters: fading active; fading type; minimal brightness; (fading) speed; color(1)
Images: \
<img width="408" height="306" alt="20261031_191843" src="https://github.com/user-attachments/assets/56bba2b3-9704-4b44-ae75-04fa65108935" />
### Bicolor
The NeoPixel strip is filled with alternating 2 colors, color1 and color2. (even pixel numbers -> color1, odd pixel numbers -> color2) You can optionaly turn on fading (periodic change of brighntness).\
Parameters: fading active; fading type; minimal brightness; (fading) speed; color1; color2
Images: \
<img width="408" height="306" alt="20261031_19202" src="https://github.com/user-attachments/assets/c5f36225-3023-492e-b675-63877ca25923" />
### Color range
The NeoPixel strip displays a static color gradient from color1 to color2.The pixel color changes gradualy along the strip length. You can optionaly turn on fading (periodic change of brighntness).\
Parameters: fading active; fading type; minimal brightness; (fading) speed; color1; color2;reverse
Images: \
<img width="408" height="306" alt="20261031_193313" src="https://github.com/user-attachments/assets/24719b4d-587a-471d-aa35-37a69d7b0dfa" />
<img width="408" height="306" alt="20261031_193235" src="https://github.com/user-attachments/assets/d1f7fa3e-9221-4637-bd31-2c8c737090dc" />
### Static rainbow
The NeoPixel strip displays a static color gradient of the whole color spectrum.The pixel color changes gradualy along the strip length from red through green, to blue and back to red. You can optionaly turn on fading (periodic change of brighntness).\
Parameters: fading active; fading type; minimal brightness; (fading) speed; reverse; saturation
Images: \
<img width="408" height="306" alt="20261031_193839" src="https://github.com/user-attachments/assets/5445bfc4-93b5-4a65-b102-39648928781f" />
<img width="408" height="306" alt="20261031_193819" src="https://github.com/user-attachments/assets/4be44d0d-a0ea-4f0b-8d7d-f1de9368358e" />
### Rainbow scrolling
The NeoPixel strip is filled with a color that gradualy changes and it goes through the whole color spectrum. \
Parameters: speed; saturation; reverse \
Video: \
https://github.com/user-attachments/assets/183dcf6d-ea0a-4f41-9295-07365bde01a7
### Dynamic color range
The NeoPixel strip displays a color gradient from color 1 to color 2, that gradualy changes its position on the strip over time. \
Parameters: speed; direction; reverse; color1; color2 \
Image and video: \
Uploading 20261031_200406 (2).mp4…  \
<img width="306" height="408" alt="20261031_200327 (2)" src="https://github.com/user-attachments/assets/b7e85ca3-4bcb-4961-af08-52dfebb7b86a" />
### Dynamic rainbow
The NeoPixel strip displays a color gradient of the whole color spectrum, that gradualy changes its position on the strip over time. \
Parameters: speed; direction; reverse; saturation \
Video: \
https://github.com/user-attachments/assets/8683c5e3-eeae-4af0-b9e4-4365a7df2057
### Running light-full
Only one pixel, or a group of pixel is lit up in a selected color. This group of pixels changes its led indexes, the lit up pixels move on the strip, creating an effect as if  the light was 'running' along the NeoPixel strip. \
In this mode the light is 'running' along the whole strip \
Parameters: speed; style; trace width; \
Video: \
https://github.com/user-attachments/assets/28ec2a46-6252-45c5-8485-85ba84fa09d4
### Running light-center 
Only one pixel, or a group of pixel is lit up in a selected color. This group of pixels changes its led indexes, the lit up pixels move on the strip, creating an effect as if  the light was 'running' along the NeoPixel strip. \
In this mode the light is 'running' in along 2 separate sectors. (Halves of the strip) \
Parameters: speed; style; trace width; \
Video: \
https://github.com/user-attachments/assets/bd483321-c55b-4fa9-a4e5-22a1f25121ea
### Stars
A selected amount of pixels with random color gradualy appear on random places on the strip. They appear and disappearat different times. Their brightness gradually increases and then discreases. This creates an affect as if stars with different colors were created and then destroyed. \
Parameters: speed; number of stars \
Video: \
https://github.com/user-attachments/assets/4c371b9b-5c3a-4340-8ff7-183c0c43e3fc
### Soundbar-monocolor
Depending on the sound intensity measured by the sound sensor (you can see it on photos and videos) a calculated amount of pixels lights up in a selected color. The brightness of the of the last lit up pixel also changes according to the sound intensity to make it more continuouos. \
Parameters: orientation; max sound value; reverse; color \
Video: \
https://github.com/user-attachments/assets/9da0489d-f077-424d-85cb-164218529b64
### Soundbar-color range
Depending on the sound intensity measured by the sound sensor (you can see it on photos and videos) a calculated amount of pixels lights up to display a part of a color gradient from color1 to color2. The brightness of the of the last lit up pixel also changes according to the sound intensity to make it more continuouos. \
Parameters: orientation; max sound value; reverse; color1; color2 \
Video: \
https://github.com/user-attachments/assets/5dade8ec-800d-4238-ace8-fb812a9bef33
## Parameters description
### Fading on
Determines if fading (periodic change of brightness) will be active. \
Video of how does fading look like: \
https://github.com/user-attachments/assets/b10a56e8-8120-4af6-9d38-f05e15bc119d
### Fading minimal brightness
The minimal brightness value during fading. Brightness won't change lower than this value during fading. \
The maximal brightness value during fading can be adjusted using the brightness potentiometer. 
### Speed
Determines how fast does the animation run. How quickly does it change. \
Animation timestep is calculated as t=(x/speed), where x is a value in miliseconds and is specific for each mode.
### Temperature
How close to yellow is the white color.
### Saturation
Determines how far from white is the color. If you have 100% saturation you have only the color and as you lower it it becomes more white, eventualy at saturation 0% it is simply white. \
<img width="225" height="135" alt="image" src="https://github.com/user-attachments/assets/02d17198-ac5d-4b33-9301-08852025bc0d" /> \
*https://www.virtualartacademy.com/wp-content/uploads/2018/12/hue-saturation-value.png*
### Direction
The direction where the color gradient is shifting along the NeoPixel strip. \
It can have 2 values: Forward (FD) or backwards (BG) \
Videos: \
Forward: Uploading 20261031_215625.mp4… \
Backwards: Uploading 20261031_215650.mp4…
### Tracewidth
The amount of pixels except the main pixel that are 'running' on the strip. \
(The other pixels brightness is halved that many times as how much you are away from the main pixel.)
### Number of stars
The amount of pixels that are turned on at the same time during the stars mode.
### Max sound value
It is the sound level value that the sound sensor must read in order to light up the whole NeoPixel strip during the soundbar mode.
###
## System design
## Youtube videos note


