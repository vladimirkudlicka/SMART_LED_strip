from machine import SPI,SoftSPI, Pin, ADC,RTC
from ili9341 import Display,color565#SRC:https://github.com/rdagger/micropython-ili9341/blob/master/ili9341.py
from xtp2046 import Touch
import framebuf
import math
import SECRETS
import network
import ntptime
import socket
import neopixel
from time import sleep,sleep_ms
import neopixel
#display init
dspSPI=SPI(2,baudrate=40000000)#sck=Pin(18),miso=Pin(19),mosi=Pin(23)
dsp=Display(dspSPI,cs=Pin(5),rst=Pin(22),dc=Pin(17),rotation=270)
dspLED=Pin(16,Pin.OUT)
dspLED.on()
dsp.clear(0)
#touch Handling
def touched(x,y):
    y=330-y
    global touch
    touch[0]=True
    touch[1]=x
    touch[2]=y
#touchscreen init
touchSPI=SPI(1,baudrate=1000000)
touchscreen=Touch(touchSPI, cs=Pin(26), int_pin=Pin(27),int_handler=touched)
touch=[False,0,0]
#initiation sequence
dsp.draw_text8x8(20,160, 'starting SMART LED system', color565(255,255,255))
dsp.draw_text8x8(75,300, 'by Vladimir Kudlicka', color565(255,255,255))
#sensors config
sound=ADC(Pin(34))
#NeoPixel config
pixLenght=8
pix=neopixel.NeoPixel(Pin(21),pixLenght)
sleep(2)
#connecting
#Color generator
def getRGB(deg,sat,brightness):#sat=saturation(0-100)
    sat=sat/100
    m=1/60
    if deg>=0 and deg<60:
        R=1
        G=0
        B=m*deg
    if deg>=60 and deg<120:
        R=1-m*(deg-60)
        G=0
        B=1
    if deg>=120 and deg<180:
        R=0
        G=m*(deg-120)
        B=1
    if deg>=180 and deg<240:
        R=0
        G=1
        B=1-m*(deg-180)
    if deg>=240 and deg<300:
        R=m*(deg-240)
        G=1
        B=0
    if deg>=300 and deg<360:
        R=1
        G=1-m*(deg-300)
        B=0
    myColor=(int(((R*sat*255)+(255*(1-sat)))*brightness),int(((G*sat*255)+(255*(1-sat)))*brightness),int(((B*sat*255)+(255*(1-sat)))*brightness))
    return myColor
#neopixel modes functions and other
runAnimation=False
pixModesFunctions=[]
def white(temperature,fadingActive,fminBrightness,fmaxBrightness,fspeed,brightness):
    global runAnimation
    if fadingActive:
        bright=fminBrightness
        up=True
        while runAnimation:
            color=(int(255*bright),int((255-temperature/4)*bright),int((255-temperature)*bright))
            pix.fill(color)
            pix.write()
            if up:
                bright+=0.01
            else:
                bright-=0.01
            if bright>=fmaxBrightness and up:
                up=False
            elif bright<=fminBrightness and not up:
                up=True
            sleep_ms(int(5000/fspeed))


    else:
        color=(int(255*brightness),int((255-temperature/4)*brightness),int((255-temperature)*brightness))
        pix.fill(color)
        pix.write()

#color picker displaying + touchscreen reaction
colorPickerData=[False,0]#active flag, pixColors list index
pixColors=[[0,0],[0,0]]
selected_color=[0,0]
def color_picker_UI():
    dsp.clear()
    dspLED.off()
    r=100
    X=120
    Y=160
    cw=bytearray((2*r+1)*(r+1)*2)
    fb=framebuf.FrameBuffer(cw,101,201,framebuf.RGB565)
    for x in range(0,r+1):
        for y in range(0,2*r+1):
            dy=r-y
            dx=x
            dst=(dx**2+dy**2)**0.5
            if dst<=r:
                deg=math.atan2(dy,dx)*(180/math.pi)
                deg-=90
                if deg<0:
                    deg+=360
                R,G,B=getRGB(deg,dst,1)
                    #dsp.draw_pixel(X+dx,Y-dy,color565(R,G,B))
                c=color565(R,G,B)
                c = ((c & 0xFF) << 8) | (c >> 8)
                fb.pixel(dx,r-dy ,c)
    dsp.block(X,Y-r,X+r,Y+r,cw)
    fb.fill(0)
    for x in range(0,r+1):
        for y in range(0,2*r+1):
            dy=r-y
            dx=x-r
            dst=(dx**2+dy**2)**0.5
            if dst<=r:
                deg=math.atan2(dy,dx)*(180/math.pi)
                deg-=90
                if deg<0:
                    deg+=360
                R,G,B=getRGB(deg,dst,1)
                c=color565(R,G,B)
                c = ((c & 0xFF) << 8) | (c >> 8)
                fb.pixel(x,r-dy ,c)
    dsp.block(X-r,Y-r,X,Y+r,cw)
    dspLED.on()
    dsp.draw_rectangle(150,270,90,50,color565(255,255,255))
    dsp.draw_text8x8(164,291, 'Confirm', color565(255,255,255))
def color_picker_touch(x,y):
    global selected_color, colorPickerData,pixColors
    r=100
    X=120
    Y=160
    if x>=X-r and x<=X+r and y>=Y-r and y<=Y+r:
        dy=Y-y
        dx=x-X
        dst=(dx**2+dy**2)**0.5
        if dst<=100:
            deg=math.atan2(dy,dx)*(180/math.pi)
            deg-=90
            if deg<0:
                deg+=360
            R,G,B=getRGB(deg,dst,1)
        dsp.fill_hrect(0,0,240,25,color565(R,G,B))
        selected_color=[deg,dst]
    elif x>=150 and y>=270:
        colorPickerData[0]=False
        pixColors[colorPickerData[1]]=selected_color
        dsp.clear()
#numeric keyboard
selected_num=''
numKeyData=[False,0]#active flag, pixData list index
pixParams=[0,0,0,0,0]
numKeyLayout=[['1','2','3'],['4','5','6'],['7','8','9'],['C','0','OK']]
def numKey_UI():
    global numKeyLayout
    dsp.clear()
    dsp.draw_rectangle(0,0,240,45,color565(255,255,255))
    for c in range(0,3):
        for r in range(0,4):
            dsp.draw_rectangle(int(c*83.333),50+r*70,73,60,color565(255,255,255))
            if r==3 and c==2:
                dsp.draw_text8x8(194,286,'OK',color565(255,255,255))
            else:
                dsp.draw_text8x8(int(c*83.333)+32,50+r*70+26,numKeyLayout[r][c],color565(255,255,255))
def numKey_touch(x,y):
    global selected_num, numKeyData,pixParams,numKeyLayout
    if y>45:
        for r in range(3,-1,-1):
           if y>50+r*70:
               ra=r
               break
        for c in range(2,-1,-1):
            if x>int(c*83.333):
                ca=c
                break
        key=numKeyLayout[ra][ca]
        print(key)
        if key=='C':
            if len(selected_num)>0:
                if len(selected_num)>1:  
                    selected_num=selected_num[:-1]
                    dsp.fill_hrect(2,2,236,41,0)
                    l=len(selected_num)
                    dsp.draw_text8x8(int((240-l*8-l+1)/2),18,selected_num,color565(255,255,255))
                else:
                    selected_num=''
                    dsp.fill_hrect(2,2,236,41,0)
        elif key=='OK':
            if len(selected_num)>0:
                numKeyData[0]=False
                pixParams[numKeyData[1]]=int(selected_num)
                dsp.clear()
        else:
            selected_num=selected_num+key
            dsp.fill_hrect(2,2,236,41,0)
            l=len(selected_num)
            dsp.draw_text8x8(int((240-l*8-l+1)/2),18,selected_num,color565(255,255,255))
#screen mode picker
screenMode=0
screenModePickerActive=False
screenModeNames=['white','monocolor','bicolor','color range','static rainbow','dynamic color range','dynamic rainbow','running light-full','running light-center','stars','soundbar-monocolor','soundbar-color range','alarm settings','PIR settings']
def screenMode_picker_UI():
    global screenMode, screenModeNames
    dsp.clear()
    space=(320-(len(screenModeNames)*8))/(len(screenModeNames)+1)
    for i in range(len(screenModeNames)):
        if i<=4:
            c=color565(255,255,0)
        elif i<=6:
            c=color565(0,255,0)
        elif i<=8:
            c=color565(0,0,255)
        elif i==9:
            c=color565(255,0,255)
        elif i<=11:
            c=color565(0,255,255)
        elif i==12:
            c=color565(100,255,0)
        elif i==13:
            c=color565(100,0,255)
        l=len(screenModeNames[i])
        dsp.draw_text8x8(int((240-(l*8)-l+1)/2),int(space+(space+8)*i),screenModeNames[i],c)
        if i!=13:
            dsp.draw_hline(0,int(space+(space+8)*i+space/2+8),240,color565(255,255,255))
def screenMode_picker_touch(x,y):
    global screenMode,screenModePickerActive,screenModeNames
    for i in range(len(screenModeNames)-1,-1,-1):
        space=(320-(len(screenModeNames)*8))/(len(screenModeNames)+1)
        if y>((space+8)*i+space/2):
            break
    print(i)
    screenMode=i
    screenModePickerActive=False
screenMode_picker_UI()
screenModePickerActive=True
runAnimation=True
white(0,True,0.05,0.5,100,1)
while True:    
    if touch[0]:
        touch[0]=False
        print(touch[1],touch[2],'Sound lvl:',sound.read_u16() )
        if colorPickerData[0]:
            color_picker_touch(touch[1],touch[2])
            print(pixColors)
        elif numKeyData[0]:
            numKey_touch(touch[1],touch[2])
        elif screenModePickerActive:
            screenMode_picker_touch(touch[1],touch[2])
    sleep(0.1)