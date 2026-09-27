#general
from machine import SPI,SoftSPI, Pin, ADC,RTC,reset
from time import sleep,sleep_ms,time,localtime
#dislay
from ili9341 import Display,color565#SRC:https://github.com/rdagger/micropython-ili9341/blob/master/ili9341.py
from xtp2046 import Touch
import framebuf
import math
#WiFi and internet
import SECRETS
import network
import socket
import ntptime
#neopixel
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
dsp.draw_text8x8(20,156, 'starting SMART LED system', color565(255,255,255))
dsp.draw_text8x8(75,300, 'by Vladimir Kudlicka', color565(255,255,255))
#sensors config
sound_sens_pin=34
BrightPot_pin=35
random_seed_src_pin=36#leave this pin unconnected

#NeoPixel config
import pixAnimations
pixLength=8
pix=neopixel.NeoPixel(Pin(21),pixLength)
pixAnimations.init_pixAnimations(pix,pixLength,BrightPot_pin,random_seed_src_pin,sound_sens_pin)
sleep(2)
#connecting to WiFi
dsp.fill_hrect(19,151,220,20,0)
dsp.draw_text8x8(39,156,'Connecting to WiFi',color565(255,255,255))
wifi=network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SECRETS.SSID,SECRETS.PWD)
n=0
while not wifi.isconnected() and n<20:
    sleep(1)
    n+=1
dsp.fill_hrect(19,151,220,20,0)
dsp.fill_hrect(74,299,165,10,0)
if wifi.isconnected():
    dsp.draw_text8x8(21,143,'Connected succesfully!',color565(255,255,255))
    IP=wifi.ifconfig()[0] 
    dsp.draw_text8x8(20,161,'IP: '+IP,color565(255,255,255))
    print(IP)
else:
    dsp.draw_text8x8(39,143,'Connection failed.',color565(255,255,255))
    dsp.draw_text8x8(71,161,'Reseting...',color565(255,255,255))
    sleep(5)
    reset()
#time setup
import urequests
response=urequests.get('http://ip-api.com/json/?fields=timezone,offset')
rData=response.json()
response.close()
del urequests
import ntptime
ntptime.settime()
del ntptime
rtc=RTC()
tm=time()+rData['offset']
dtmt=localtime(tm)
rtc.datetime((dtmt[0],dtmt[1],dtmt[2],dtmt[7],dtmt[3],dtmt[4],dtmt[5],0))
dsp.clear()
#color picker displaying + touchscreen reaction
colorPickerData=[False,0]#active flag, pixColors list index
pixColors=[[0,0],[0,0]]
selected_color=[0,0]
def color_picker_UI():
    dsp.clear()
    dspLED.off()
    pix.fill((0,0,0))
    pix.write()
    r=100
    X=120
    Y=160
    nr=10
    cw=bytearray((r+1)*(r+1)*2)
    fb=framebuf.FrameBuffer(cw,101,101,framebuf.RGB565)
    for y in range(0,2*r):
        for x in range(0,2*r):
            dy=-r+y
            dx=-r+x
            
            dst=(dx**2+dy**2)**0.5
            if dst<=r:
                deg=math.atan2(dy,dx)*(180/math.pi)
                deg=360-deg#changing direction
                deg+=90#rotating color wheel
                R,G,B=pixAnimations.getRGB(deg,dst,1)
                    #dsp.draw_pixel(X+dx,Y-dy,color565(R,G,B))
                c=color565(R,G,B)
                c = ((c & 0xFF) << 8) | (c >> 8)
                fb.pixel(x,y ,c)
    dsp.block(X,Y-r,X+r,Y,cw)
    fb.fill(0)
    dspLED.on()
    dsp.draw_rectangle(150,270,90,50,color565(255,255,255))
    dsp.draw_text8x8(164,291, 'Confirm', color565(255,255,255))
    cw=0
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
            deg=360-deg#changing direction
            deg+=90#rotating color wheel
            if deg>360:
                deg-=360
            elif deg<0:
                deg+=360
            R,G,B=pixAnimations.getRGB(deg,dst,1)
            dsp.fill_hrect(0,0,240,25,color565(R,G,B))
            pix.fill((int(R*pixAnimations.getBrightness(1)),int(G*pixAnimations.getBrightness(1)),int(B*pixAnimations.getBrightness(1))))
            pix.write()
            selected_color=[deg,dst]
    elif x>=150 and y>=270:
        colorPickerData[0]=False
        pixColors[colorPickerData[1]]=selected_color
        dsp.clear()
        display_settings()
#numeric keyboard
def validate_num(pixParamIndex,value):
    global pixLength
    OK=False
    EMSG=''
    if pixParamIndex== 1:
        if 0<=value<=100:
            OK= True
        else:
            EMSG='0-100'
    elif pixParamIndex== 2:
        if 0<value<=500:
            OK=True
        else:
            EMSG='1-500'
    elif pixParamIndex== 3:
        if  0<=value<=255:
            OK=True
        else:
            EMSG='0-255'
    elif pixParamIndex== 5:
        if 0<=value<=100:
            OK=True
        else:
            EMSG='0-100'
    elif pixParamIndex==7:
        if 0<=value<=(pixLength//4):
            OK=True
        else:
            EMSG='0-'+str(pixLength//4)
    elif pixParamIndex==9:
        if 0<value<=pixLength:
            OK=True
        else:
            EMSG='1-'+str(pixLength)
    elif pixParamIndex==10:
        if 10<=value<=65535:
            OK=True
        else:
            EMSG='10-65535'
    EMSG='must be in range ' + EMSG
    return OK,EMSG   
selected_num=''
numKeyData=[False,0]#active flag, pixData list index
pixParams=[0,0,1,0,0,0,0,0,0,0,0,0,0,0]
numKeyLayout=[['1','2','3'],['4','5','6'],['7','8','9'],['C','0','OK']]
def numKey_UI():
    global numKeyLayout,numkey_emsg
    numkey_emsg=False
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
    global selected_num, numKeyData,pixParams,numKeyLayout,numkey_emsg
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
        #print(key)
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
            elif numkey_emsg:
                numkey_emsg=False
                dsp.fill_hrect(2,2,236,41,0)
        elif key=='OK':
            if len(selected_num)>0:
                OK,emsg=validate_num(numKeyData[1],int(selected_num))
                if OK:
                    numKeyData[0]=False
                    pixParams[numKeyData[1]]=int(selected_num)
                    dsp.clear()
                    selected_num=''
                    display_settings()
                else:
                    numkey_emsg=True
                    selected_num=''
                    dsp.fill_hrect(2,2,236,41,0)
                    l=len(emsg)
                    dsp.draw_text8x8(int((240-l*8-l+1)/2),18,emsg,color565(255,255,255))
        else:
            selected_num=selected_num+key
            dsp.fill_hrect(2,2,236,41,0)
            l=len(selected_num)
            dsp.draw_text8x8(int((240-l*8-l+1)/2),18,selected_num,color565(255,255,255))
#screen mode picker
screenMode=0
screenModePickerActive=False
screenModeNames=['white','monocolor','bicolor','color range','static rainbow','rainbow scrolling','dynamic color range','dynamic rainbow','running light-full','running light-center','stars','soundbar-monocolor','soundbar-color range','alarm settings','PIR settings']
def screenMode_picker_UI():
    global screenMode, screenModeNames
    dsp.clear()
    space=(320-(len(screenModeNames)*8))/(len(screenModeNames)+1)
    for i in range(len(screenModeNames)):
        if i<=5:
            c=color565(255,255,0)
        elif i<=7:
            c=color565(0,255,0)
        elif i<=9:
            c=color565(0,0,255)
        elif i==10:
            c=color565(255,0,255)
        elif i<=12:
            c=color565(0,255,255)
        elif i==13:
            c=color565(100,255,0)
        elif i==14:
            c=color565(100,0,255)
        l=len(screenModeNames[i])
        dsp.draw_text8x8(int((240-(l*8)-l+1)/2),int(space+(space+8)*i),screenModeNames[i],c)
        if i!=14:
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
    display_settings()
#settings displaying function
def display_param_line(x0,y0,paramName,paramValue):
    whitec=color565(255,255,255)
    dsp.draw_text8x8(x0,y0+6,paramName,whitec)
    dsp.draw_rectangle(180,y0,55,20,whitec)  
    dsp.draw_text8x8(int(180+((60-len(paramValue)*9)/2)-1),y0+6,paramValue,whitec)
def setting_color_squares(y):
    global pixColors
    R,G,B=pixAnimations.getRGB(pixColors[0][0],pixColors[0][1],1)
    dsp.fill_hrect(0,y,120,100,color565(R,G,B))
    dsp.draw_text8x8(29,y+46,'COLOR 1',0,color565(R,G,B))
    R,G,B=pixAnimations.getRGB(pixColors[1][0],pixColors[1][1],1)
    dsp.fill_hrect(120,y,120,100,color565(R,G,B))
    dsp.draw_text8x8(150,y+46,'COLOR 2',0,color565(R,G,B))
    dsp.draw_vline(119,y,100,0)
def display_settings():
    global screenMode,screenModeNames,pixParams
    whitec=color565(255,255,255)
    #datetime info
    dtm=rtc.datetime()
    weekdays=['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    dsp.clear()
    dsp.fill_hrect(0,0,240,8,0)
    dsp.draw_text8x8(0,0,f'{dtm[4]}:{dtm[5]} {weekdays[dtm[3]]} {dtm[2]}/{dtm[1]}',whitec)
    dsp.draw_rectangle(0,10,240,12,whitec)
    a=screenModeNames[screenMode]
    dsp.draw_text8x8(int((240-len(a)*(9)-1)/2),12,a,whitec)
    #modes 1-4
    boolnames={'0':'OFF','1':'ON'}
    if screenMode<5:
        fading_on=str(pixParams[0])
        fminBrightness=str(pixParams[1])
        fadetypes={'0':'linear','1':'exp.'}
        fadetype=str(pixParams[3])
        fspeed=str(pixParams[2])
        
        dsp.draw_text8x8(0,25,'Fading settings:',whitec)

        display_param_line(5,35,'Fading active:',boolnames[fading_on])
        display_param_line(5,60,'Fade type:',fadetypes[fadetype])
        display_param_line(5,85,'Min. Brightness 0-100:',fminBrightness)
        display_param_line(5,110,'Fading speed:',fspeed)

    if screenMode==0:
        display_param_line(0,135,'Temperature:',str(pixParams[4]))
    if screenMode==1:
        R,G,B=pixAnimations.getRGB(pixColors[0][0],pixColors[0][1],1)
        dsp.fill_hrect(0,180,240,100,color565(R,G,B))
        dsp.draw_text8x8(98,226,'COLOR',0,color565(R,G,B))
    if screenMode==2 or screenMode==3:
        setting_color_squares(180)
    if screenMode==3 or screenMode==4:
        display_param_line(0,135,'Reverse:',str(bool(pixParams[13])))
    if screenMode==4:
        display_param_line(0,160,'Saturation:',str(pixParams[5]))
    #mode 5
    if screenMode==5:
        display_param_line(0,30,'Speed:',str(pixParams[2]))
        display_param_line(0,65,'Saturation:',str(pixParams[5]))
        display_param_line(0,100,'Reverse:',str(bool(pixParams[13])))
    if screenMode==6 or screenMode==7:
        direction_names={0:'FD',1:'BG'}
        display_param_line(0,30,'Speed:',str(pixParams[2]))
        display_param_line(0,55,'Direction',direction_names[pixParams[6]])
        display_param_line(0,80,'Reverse:',str(bool(pixParams[13])))
    if screenMode==6:
        display_param_line(0,105,'Saturation',str(pixParams[5]))
    if screenMode==7:
        setting_color_squares()
    if screenMode<=11:
        dsp.draw_rectangle(0,300,240,20,whitec)
        dsp.draw_text8x8(84,306,'Run mode',whitec)
#settings touch processing
def settings_touch_0_4(x,y):
    global screenMode,colorPickerData,numKeyData,screenMode,screenModePickerActive,pixParams
    boolnames={'0':'OFF','1':'ON'}   
    if y>=35 and y<=130:
        ia=0
        fadetypes={'0':'linear','1':'exp.'}
        for i in range(1,5):
            if y<i*25+32.5:
                ia=i
                break
        if ia==1:
            pixParams[0]=int(not bool(pixParams[0]))
            dsp.fill_hrect(0,35,240,20,0)
            display_param_line(5,35,'Fading active:',boolnames[str(pixParams[0])])
        if ia==2:
            pixParams[3]=int(not bool(pixParams[3]))
            dsp.fill_hrect(0,60,240,20,0)
            display_param_line(5,60,'Fade type:',fadetypes[str(pixParams[3])])
        if ia==3:
            numKeyData=[True,1]
            numKey_UI()
        if ia==4:
            numKeyData=[True,2]
            numKey_UI()
    elif (screenMode==1 or screenMode==2 or screenMode==3) and (y>=180 and y<=280):
        if screenMode==1:
            colorPickerData=[True,0]
        else:
            if x<=120:
                colorPickerData=[True,0]
            else:
                colorPickerData=[True,1]
        color_picker_UI()
    elif (screenMode==3 or screenMode==4) and (y>132.5 and y<157.5):
        pixParams[13]=int(not bool(pixParams[13]))
        dsp.fill_hrect(0,135,240,20,0)
        display_param_line(0,135,'Reverse:',str(bool(pixParams[13])))
    elif screenMode==4 and y>157.5 and y<182.5:
        numKeyData=[True,5]
        numKey_UI()
    elif screenMode==0 and y>132.5 and y<157.5:
        numKeyData=[True,4]
        numKey_UI()
def settings_touch_5_7(x,y):
    global screenMode,colorPickerData,numKeyData,screenMode,screenModePickerActive,pixParams
    if screenMode==5:
        if 25<=y and y<=57.5:
            numKeyData=[True,2]
            numKey_UI()
        elif 57.5<y and y<=92.5:
            numKeyData=[True,5]
            numKey_UI()
        elif 92.5<=y and y<=127.5:
            pixParams[13]=int(not bool(pixParams[13]))
            dsp.fill_hrect(0,100,240,20,0)
            display_param_line(0,100,'Reverse:',str(bool(pixParams[13])))
def settings_touch(x,y):
    global screenMode,screenModePickerActive
    if y<=22:
        screenMode_picker_UI()
        screenModePickerActive=True
    else:
        if screenMode<=4:
            settings_touch_0_4(x,y)
        elif screenMode<=7:
            settings_touch_5_7(x,y)
pixAnimations.runAnimation=True
import _thread
_thread.start_new_thread(pixAnimations.stars,(100,4))
display_settings()
lm=rtc.datetime()[5]
while True: 
    dtm=rtc.datetime()
    if lm!=dtm[5] and not(screenModePickerActive or numKeyData[0] or colorPickerData[0]):
        lm=dtm[5]
        weekdays=['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
        dsp.fill_hrect(0,0,240,8,0)
        dsp.draw_text8x8(0,0,f'{dtm[4]}:{dtm[5]} {weekdays[dtm[3]]} {dtm[2]}/{dtm[1]}',color565(255,255,255))
    if touch[0]:
        touch[0]=False
        if colorPickerData[0]:
            color_picker_touch(touch[1],touch[2])
        elif numKeyData[0]:
            numKey_touch(touch[1],touch[2])
        elif screenModePickerActive:
            screenMode_picker_touch(touch[1],touch[2])
        else:
            settings_touch(touch[1],touch[2])
    sleep(0.1)