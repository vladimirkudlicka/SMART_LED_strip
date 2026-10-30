# Credits
ili9341 and xtp2046 libraries source: https://github.com/rdagger/micropython-ili9341/tree/master \
HSV2RGB function in pixAnimations source: https://toptechboy.com/convert-hsv-to-rgb-in-micropython/ (This function was modfied by me) \
All the other code was written by me.
# Project description
This is a NeoPixel strip controller with 12 different modes that uses TFT display with touchscreen as a main control element. It also features a brightness potentiometer and a button.
## Basic control
### Button
When you shortly(t<1s) press and release a button you can exit numeric keyboard, color picker or mode picker. You will return back to modes settings. \
When you longly (2s<t<10s) press and then release a button you will turn off a neopixel mode (if it is running), then a turn off animation will be executed and the stip will remain dark.
### Bightness potentiometer
You can adjust the strip brightness by turning the brightness potentiometer. It works on all modes. \ 
The brightness will be adjusted using software, not by limiting the NeoPixel supply voltage.
### Display UI
#### Color picker
#### Numeric keyboard
#### Mode picker
## Modes description and parameters
## Parameters description
## Architecture


