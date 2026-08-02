#general
from machine import SPI,SoftSPI, Pin, ADC,RTC,reset
from time import sleep,sleep_ms,time,localtime
import gc
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
import random
import _thread

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
sound=ADC(Pin(34))
random_seed_src=ADC(Pin(36))#leave this pin unconnected
#NeoPixel config
pixLength=8
pix=neopixel.NeoPixel(Pin(21),pixLength)
pix.fill((0,0,0))
pix.write()
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
ntptime.settime()
rtc=RTC()
tm=time()+rData['offset']
dtmt=localtime(tm)
rtc.datetime((dtmt[0],dtmt[1],dtmt[2],dtmt[7],dtmt[3],dtmt[4],dtmt[5],0))
dsp.clear()
#noise sensor function
quiet_sound_lvl=1127.6624
def callibrate_sound_sensor():
    global quiet_sound_lvl
    data=list()
    for i in range(1000):
        data.append(sound.read_u16())
        sleep_ms(1)
    quiet_sound_lvl=sum(data)/len(data)
def sound_lvl():
    global quiet_sound_lvl
    raw=sound.read_u16()
    processed=abs(raw-quiet_sound_lvl)
    return processed
#Color generator
#soure:https://toptechboy.com/convert-hsv-to-rgb-in-micropython/ (it was modified by my to contain brightnes, saturation and I flipped the color wheel)
def getRGB(deg,sat,brightness):#sat=saturation(0-100)
    deg=360-deg
    if deg>360:
        deg-=360
    elif deg<0:
        deg+=360
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
    if deg>=300 and deg<=360:
        R=1
        G=1-m*(deg-300)
        B=0
    myColor=(math.ceil(((R*sat*255)+(255*(1-sat)))*brightness),math.ceil(((G*sat*255)+(255*(1-sat)))*brightness),math.ceil(((B*sat*255)+(255*(1-sat)))*brightness))
    return myColor
#neopixel modes functions and support functions
runAnimation=False
pixmode=0
#fullpix category functions
def fading(lvl,up,minBright,maxBright,fadetype):
    if up:
        lvl+=0.01
    else:
        lvl-=0.01
    if lvl>=1  and up:
        up=False
    elif lvl<=0 and not up:
        up=True
    if fadetype==1:
        bright=minBright+((maxBright-minBright)*((100**lvl)/100))
    elif fadetype==0:
        bright=minBright+((maxBright-minBright)*lvl)
    return bright,lvl,up

def white(temperature,fadingActive,fminBrightness,fmaxBrightness,fspeed,fadetype,brightness):
    global runAnimation
    if fadingActive:
        bright=fminBrightness
        lvl=0
        up=True
        while runAnimation:
            bright,lvl,up=fading(lvl,up,fminBrightness,fmaxBrightness,fadetype)
            color=(int(255*bright),int((255-temperature/4)*bright),int((255-temperature)*bright))
            pix.fill(color)
            pix.write() 
            sleep_ms(int((500/(fmaxBrightness-fminBrightness))/fspeed))
    else:
        color=(int(255*brightness),int((255-temperature/4)*brightness),int((255-temperature)*brightness))
        pix.fill(color)
        pix.write()
def monocolor(color,fadingActive,fminBright,fmaxBright,fspeed,fadetype,brightness):
    global runAnimation
    if fadingActive:
        bright=fminBright
        up=True
        lvl=0
        while runAnimation:
            bright,lvl,up=fading(lvl,up,fminBright,fmaxBright,fadetype)
            pix.fill(getRGB(color[0],color[1],bright))
            pix.write()
            sleep_ms(int((500/(fmaxBright-fminBright))/fspeed))
    else:
        pix.fill(getRGB(color[0],color[1],brightness))
        pix.write()
def bicolor(color1,color2,fadingActive,fminBright,fmaxBright,fspeed,fadetype,brightness):
    global runAnimation,pixLength
    if fadingActive:
        bright=fminBright
        up=True
        lvl=0
        pixList=[0 for _ in range(pixLength)]
        for i in range(0,pixLength,2):
                pixList[i]=getRGB(color1[0],color1[1],1)
        for i in range(1,pixLength,2):
            pixList[i]=getRGB(color2[0],color2[1],1)
        while runAnimation:
            bright,lvl,up=fading(lvl,up,fminBright,fmaxBright,fadetype)
            for i in range(pixLength):
                pix[i]=(int(pixList[i][0]*bright),int(pixList[i][1]*bright),int(pixList[i][2]*bright))
            pix.write()
            sleep_ms(int((500/(fmaxBright-fminBright))/fspeed))
    else:
        for i in range(0,pixLength,2):
                pix[i]=getRGB(color1[0],color1[1],brightness)
        for i in range(1,pixLength,2):
            pix[i]=getRGB(color2[0],color2[1],brightness)
        pix.write()
def color_range(color1,color2,fadingActive,fminBright,fmaxBright,fspeed,fadetype,brightness,reverse):
    global pixLength,runAnimation
    satStep=(color2[1]-color1[1])/(pixLength-1)
    if color1[0]<=color2[0]:
        hueStep=(color2[0]-color1[0])/(pixLength-1)
    else:
        color2[0]+=360
        hueStep=(color2[0]-color1[0])/(pixLength-1)
    if fadingActive:
        bright=fminBright
        up=True
        lvl=0
        pixList=[0 for _ in range(pixLength)]
        for i in range(pixLength):
            hue=color1[0]+hueStep*i
            sat=color1[1]+satStep*i
            pixList[i]=getRGB(int(hue),int(sat),1)
        if reverse:
            pixList.reverse()
        while runAnimation:
            bright,lvl,up=fading(lvl,up,fminBright,fmaxBright,fadetype)
            for i in range(pixLength):
                pix[i]=(int(pixList[i][0]*bright),int(pixList[i][1]*bright),int(pixList[i][2]*bright))
            pix.write()
            sleep_ms(int((500/(fmaxBright-fminBright))/fspeed))
    else:
        for i in range(pixLength):
            if reverse:
                a=pixLength-1-i
            else:
                a=i
            hue=color1[0]+hueStep*a
            sat=color1[1]+satStep*a
            pix[i]=getRGB(int(hue),int(sat),brightness)
        pix.write()
def static_rainbow(saturation,fadingActive,fminBright,fmaxBright,fspeed,fadetype,brightness,reverse):
    global runAnimation, pixLength
    hueStep=360/pixLength
    if fadingActive:
        bright=fminBright
        up=True
        lvl=0
        pixList=[getRGB(hueStep*i,saturation,1) for i in range(pixLength)]
        if reverse:
            pixList.reverse()
        while runAnimation:
            bright,lvl,up=fading(lvl,up,fminBright,fmaxBright,fadetype)
            for i in range(pixLength):
                pix[i]=(int(pixList[i][0]*bright),int(pixList[i][1]*bright),int(pixList[i][2]*bright))
            pix.write()
            sleep_ms(int((500/(fmaxBright-fminBright))/fspeed))
    else:
        for i in range(pixLength):
            if reverse:
                a=pixLength-1-i
            else:
                a=i
            hue=hueStep*a
            pix[i]=getRGB(int(hue),int(saturation),brightness)
        pix.write() 
def rainbow_scrolling(speed,saturation,brightness,reverse):
    global runAnimation
    hue=0
    while runAnimation:
        pix.fill(getRGB(hue,saturation,brightness))
        pix.write()
        if reverse:
            hue-=1
            if hue<=0:
                hue+=359
        else:
            hue+=1
            if hue>=360:
                hue-=360
        sleep_ms(int(5000/speed))
#dynamic category
def dynamic_color_range(color1,color2,speed,direction,brightness,reverse):
    global runAnimation, pixLength
    satStep=(color2[1]-color1[1])/(pixLength-1)
    if color1[0]<=color2[0]:
        hueStep=(color2[0]-color1[0])/(pixLength-1)
    else:
        color2[0]+=360
        hueStep=(color2[0]-color1[0])/(pixLength-1)

    if color1[1]>color2[1]:
        lowSat=color2[1]
        highSat=color1[1]
    if color1[1]<color2[1]:
        lowSat=color1[1]
        highSat=color2[1]

    pixList=[0 for _ in range(pixLength)]
    for i in range(pixLength):
        hue=color1[0]+hueStep*i
        sat=color1[1]+satStep*i
        pixList[i]=[hue,sat]
    if direction==1:
        satStep=-satStep
    if reverse:
        pixList.reverse()
    while runAnimation:
        for i in range(pixLength):
            if direction==0:
                pixList[i][0]+=1               
                if pixList[i][0]>color2[0]:
                    pixList[i][0]=color1[0]
            elif direction==1:
                pixList[i][0]-=1
                if pixList[i][0]<color1[0]:
                    pixList[i][0]=color2[0]
            if satStep>0:
                pixList[i][1]+=1
                if pixList[i][1]>highSat:
                    pixList[i][1]=lowSat
            elif satStep<0:
                pixList[i][1]-=1
                if pixList[i][1]<lowSat:
                    pixList[i][1]=highSat
            pix[i]=getRGB(pixList[i][0],pixList[i][1],brightness)
        pix.write()
        sleep((5000/(abs(satStep*(pixLength-1))+hueStep*(pixLength-1)))/speed)
def dynamic_rainbow(saturation,speed,direction,brightness,reverse):
    global runAnimation, pixLength
    pixList=[(360/pixLength)*i for i in range(pixLength)]
    if reverse:
        pixList.reverse()               
    while runAnimation:
        for i in range(pixLength):
            if direction==0:
                pixList[i]+=1
                if pixList[i]>=359:
                    pixList[i]=0    
            elif direction==1:
                pixList[i]-=1
                if pixList[i]<=0:
                    pixList[i]=359
            pix[i]=getRGB(pixList[i],saturation,brightness)
        pix.write()
        sleep_ms(int(5000/speed))
#animation cathegory
def  running_light_full(color,tracewidth,brightness,style,speed):
    global runAnimation, pixLength
    if style==0 or style==2:
        pos=0
        up=True
    elif style==1:
        pos=pixLength-1
        up = False
    while runAnimation:
        pix.fill((0,0,0))
        if up:
            pos+=1
        else:
            pos-=1
        if pos<0 and not up and style==1:
                pos=pixLength-1
        elif pos<=0 and not up and style==2:
            up=True
        elif pos>pixLength-1 and up and style==0:
            pos=0
        elif pos>=pixLength-1 and up and style==2:
            pos=pixLength-1
            up =False
        pix[pos]=getRGB(color[0],color[1],brightness)
        if pos+tracewidth>pixLength-1:
            trace=tracewidth-(pos+tracewidth-pixLength+1)
        else:
            trace=tracewidth
        for i in range(pos+1,pos+trace+1):
            pix[i]=getRGB(color[0],color[1],brightness/(1+i-pos)) 
        if pos-tracewidth<0:
            trace=tracewidth+(pos-tracewidth)
        else:
            trace=tracewidth
        for i in range(pos-1,pos-trace-1,-1):
            pix[i]=getRGB(color[0],color[1],brightness/(1+pos-i))
        pix.write()
        sleep_ms(int(5000/speed))
def running_light_center(color,tracewidth,brightness,style,speed):
    global runAnimation,pixLength
    if pixLength%2==0:
        start1=int(pixLength/2)-1
        start2=int(pixLength/2)
    else:
        start1=int(pixLength/2)
        start2=int(pixLength/2)

    if style==0 or style==2:
        pos1=start1
        pos2=start2
        up2=True
        up1=False
    elif style==1:
        pos2=pixLength-1
        pos1=0
        up2 = False
        up1=True
    while runAnimation:
        pix.fill((0,0,0))
        if up1:
            pos1+=1
        else:
            pos1-=1
        if pos1<0 and not up1 and style==0:
                pos1=start1
        elif pos1<=0 and not up1 and style==2:
            up1=True
        elif pos1>start1 and up1 and style==1:
            pos1=0
        elif pos1>=start1 and up1 and style==2:
            pos1=start1
            up1 =False
        pix[pos1]=getRGB(color[0],color[1],brightness)
        if pos1+tracewidth>start1:
            trace=tracewidth-(pos1+tracewidth-start1)
        else:
            trace=tracewidth
        for i in range(pos1+1,pos1+trace+1):
            pix[i]=getRGB(color[0],color[1],brightness/(1+i-pos1)) 
        if pos1-tracewidth<0:
            trace=tracewidth+(pos1-tracewidth)
        else:
            trace=tracewidth
        for i in range(pos1-1,pos1-trace-1,-1):
            pix[i]=getRGB(color[0],color[1],brightness/(1+pos1-i))


        if up2:
            pos2+=1
        else:
            pos2-=1
        if pos2<start2 and not up2 and style==1:
                pos2=pixLength-1
        elif pos2<=start2 and not up2 and style==2:
            up2=True
        elif pos2>pixLength-1 and up2 and style==0:
            pos2=start2
        elif pos2>=pixLength-1 and up2 and style==2:
            pos2=pixLength-1
            up2 =False
        pix[pos2]=getRGB(color[0],color[1],brightness)
        if pos2+tracewidth>pixLength-1:
            trace=tracewidth-(pos2+tracewidth-pixLength+1)
        else:
            trace=tracewidth
        for i in range(pos2+1,pos2+trace+1):
            pix[i]=getRGB(color[0],color[1],brightness/(1+i-pos2)) 
        if pos2-tracewidth<start2:
            trace=tracewidth-(start2-(pos2-tracewidth))
        else:
            trace=tracewidth
        for i in range(pos2-1,pos2-trace-1,-1):
            pix[i]=getRGB(color[0],color[1],brightness/(1+pos2-i))
        pix.write()
        sleep_ms(int(5000/speed))
#stars  mode
def stars(speed,stars_count,max_brightness):
    global runAnimation,pixLength
    max_brightness=int(max_brightness*100)
    random.seed(random_seed_src.read_u16())
    if random.randint(0,5)==2:
        sat=100
    else:
        sat=random.randint(50,99)
    max_bright=round((max_brightness/2)+((max_brightness/2)*random.random()))
    pos=random.randint(0,pixLength-1)
    posList=[pos]
    starList=[[pos,random.randint(0,359),sat,max_bright,0,True]]#index,Hue,saturation,max_brigthness,current brightnes,up
    pix.fill((0,0,0))
    while runAnimation:
        if len(starList)<stars_count:
            if random.randint(0,stars_count-(stars_count-len(starList)))==1:
                if random.randint(0,5)==2:
                    sat=100
                else:
                    sat=random.randint(50,99)
                pos=random.randint(0,pixLength-1)
                while pos in posList:
                    pos=random.randint(0,pixLength-1)
                posList.append(pos)
                max_bright=round((max_brightness/2)+((max_brightness/2)*random.random()))    
                star=[pos,random.randint(0,359),sat,max_bright,0,True]
                starList.append(star)
        starList2=[]
        for i in range(len(starList)):
            if starList[i][5]:
                starList[i][4]+=1
            else:
                starList[i][4]-=1
            if starList[i][4]>=starList[i][3] and starList[i][5]:
                starList[i][5]=False
            if starList[i][4]<=0 and not starList[i][5]:
                posList.pop(posList.index(starList[i][0]))
                pix[starList[i][0]]=(0,0,0)
                sleep_ms(1)
            else:
                pix[starList[i][0]]=getRGB(starList[i][1],starList[i][2],starList[i][4]/100)
                sleep_ms(1)
                starList2.append(starList[i])    
        starList=starList2.copy() 
        print(starList)
        print(posList)   
        pix.write()
        sleep_ms(int(500/speed))
#soundbar cathegory
def soundbar_monocolor(color,max_soundval,orientation,max_brightness):
    global runAnimation, pixLength 
    if orientation==2:
        if pixLength%2==0:
            start1=int(pixLength/2)-1
            start2=int(pixLength/2)
            pixLength2=start1+1
        else:
            start1=int(pixLength/2)
            start2=int(pixLength/2)
            pixLength2=start1+1
        sound_lvl_step=max_soundval/pixLength2
        while runAnimation:
            pix.fill((0,0,0))
            sound_val=sound_lvl()
            length=sound_val//sound_lvl_step
            bright=max_brightness*0.1+0.9*max_brightness*sound_val%sound_lvl_step
            if length>pixLength2:
                length=pixLength2
            if length==0:
                i=start2-1
            for i in range(start2,start2+length):
                pix[i]=getRGB(color[0],color[1],max_brightness)
            if i+1<pixLength:
                pix[i+1]=getRGB(color[0],color[1],bright)
            if length==0:
                i=start1+1
            for i in range(start1,start1-length,-1):
                pix[i]=getRGB(color[0],color[1],max_brightness)
            if i-1>=0:
                pix[i-1]=getRGB(color[0],color[1],bright)
            pix.write()
            sleep_ms(5)
    else:
        sound_lvl_step=max_soundval/pixLength
        while runAnimation:
            pix.fill((0,0,0))
            sound_val=sound_lvl()
            length=sound_val//sound_lvl_step
            bright=max_brightness*0.1+0.9*max_brightness*sound_val%sound_lvl_step
            if length>pixLength:
                length=pixLength
            if length==0:
                if orientation==0:
                    a=-1
                    i=-1
                else:
                    a=pixLength
                    i=-1
            for i in range(0,length):
                if orientation==0:
                    a=i
                else:
                    a=pixLength-1-i
                pix[a]=getRGB(color[0],color[1],max_brightness)
            if orientation==0:
                if a+1<pixLength:
                    pix[a+1]=getRGB(color[0],color[1],bright)
            else:
                if a-1>=0:
                    pix[a-1]=getRGB(color[0],color[1],bright)
            pix.write()
            sleep_ms(5)
def soundbar_color_range(color1,color2,max_soundval,orientation,max_brightness,reversed):
    global runAnimation,pixLength
    if color2[0]<color1[0]:
            color2[0]+=360 
    if orientation==2:
        if pixLength%2==0:
            start1=int(pixLength/2)-1
            start2=int(pixLength/2)
            pixLength2=start1+1
        else:
            start1=int(pixLength/2)
            start2=int(pixLength/2)
            pixLength2=start1+1
        sound_lvl_step=max_soundval/pixLength2
        satStep=(color2[1]-color1[1])/(pixLength2-1)
        hueStep=(color2[0]-color1[0])/(pixLength2-1)
        while runAnimation:
            pix.fill((0,0,0))
            sound_val=sound_lvl()
            length=sound_val//sound_lvl_step
            bright=max_brightness*0.1+0.9*max_brightness*sound_val%sound_lvl_step
            if length>pixLength2:
                length=pixLength2
            if length==0:
                i=start2-1
            for i in range(start2,start2+length):
                if reversed:
                    hue=color2[0]-hueStep*(i-start2)
                    sat=color2[1]-satStep*(i-start2)
                else:
                    hue=color1[0]+hueStep*(i-start2)
                    sat=color1[1]+satStep*(i-start2)
                pix[i]=getRGB(hue,sat,max_brightness)
            if i+1<pixLength:
                if reversed:
                    hue=color2[0]-hueStep*(i-start2+1)
                    sat=color2[1]-satStep*(i-start2+1)
                else:
                    hue=color1[0]+hueStep*(i-start2+1)
                    sat=color1[1]+satStep*(i-start2+1)
                pix[i+1]=getRGB(hue,sat,bright)
            if length==0:
                i=start1+1  
            for i in range(start1,start1-length,-1):
                if reversed:
                    hue=color2[0]-hueStep*(start1-i)
                    sat=color2[1]-satStep*(start1-i)
                else:
                    hue=color1[0]+hueStep*(start1-i)
                    sat=color1[1]+satStep*(start1-i)
                pix[i]=getRGB(hue,sat,max_brightness)
            if i-1>=0:
                if reversed:
                    hue=color2[0]-hueStep*(start1-i+1)
                    sat=color2[1]-satStep*(start1-i+1)
                else:
                    hue=color1[0]+hueStep*(start1-i+1)
                    sat=color1[1]+satStep*(start1-i+1)
                pix[i-1]=getRGB(hue,sat,bright)
            pix.write()
            sleep_ms(5)
    else:
        sound_lvl_step=max_soundval/pixLength
        satStep=(color2[1]-color1[1])/(pixLength-1)
        hueStep=(color2[0]-color1[0])/(pixLength-1)
        while runAnimation:
            pix.fill((0,0,0))
            sound_val=sound_lvl()
            length=sound_val//sound_lvl_step
            bright=max_brightness*0.1+0.9*max_brightness*sound_val%sound_lvl_step
            if length>pixLength:
                length=pixLength
            if length==0:
                if orientation==0:
                    a=-1
                    i=-1
                else:
                    a=pixLength
                    i=-1
            for i in range(0,length):
                if orientation==0:
                    a=i
                else:
                    a=pixLength-1-i
                if reversed:
                    hue=color2[0]-hueStep*i
                    sat=color2[1]-satStep*i
                else:
                    hue=color1[0]+hueStep*i
                    sat=color1[1]+satStep*i
                pix[a]=getRGB(hue,sat,max_brightness)
            if orientation==0:
                if a+1<pixLength:
                    if reversed:
                        hue=color2[0]-hueStep*(i+1)
                        sat=color2[1]-satStep*(i+1)
                    else:
                        hue=color1[0]+hueStep*(i+1)
                        sat=color1[1]+satStep*(i+1)
                    pix[a+1]=getRGB(hue,sat,bright)
            else:
                if a-1>=0:
                    if reversed:
                        hue=color2[0]-hueStep*(i+1)
                        sat=color2[1]-satStep*(i+1)
                    else:
                        hue=color1[0]+hueStep*(i+1)
                        sat=color1[1]+satStep*(i+1)
                    pix[a-1]=getRGB(hue,sat,bright)
            pix.write()
            sleep_ms(5)

pixModesFunctions=[white,monocolor,bicolor,color_range,static_rainbow,rainbow_scrolling,dynamic_color_range,dynamic_rainbow,running_light_full,running_light_center,stars,soundbar_monocolor,soundbar_color_range]      
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
    cw=bytearray((2*r+1)*(r+1)*2)
    fb=framebuf.FrameBuffer(cw,101,201,framebuf.RGB565)
    for x in range(0,r+1):
        for y in range(0,2*r+1):
            dy=r-y
            dx=x
            dst=(dx**2+dy**2)**0.5
            if dst<=r:
                deg=math.atan2(dy,dx)*(180/math.pi)
                deg=360-deg#changing direction
                deg+=90#rotating color wheel
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
                deg=360-deg#changing direction
                deg+=90#rotating color wheel
                R,G,B=getRGB(deg,dst,1)
                c=color565(R,G,B)
                c = ((c & 0xFF) << 8) | (c >> 8)
                fb.pixel(x,r-dy ,c)
    dsp.block(X-r,Y-r,X,Y+r,cw)
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
            R,G,B=getRGB(deg,dst,1)
            dsp.fill_hrect(0,0,240,25,color565(R,G,B))
            pix.fill((R,G,B))
            pix.write()
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
#settings displaying function
def display_settings():
    global screenMode,screenModeNames
    whitec=color565(255,255,255)
    dtm=rtc.datetime()
    weekdays=['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    dsp.clear()
    dsp.fill_hrect(0,0,240,8,0)
    dsp.draw_text8x8(0,0,f'{dtm[4]}:{dtm[5]} {weekdays[dtm[3]]} {dtm[2]}/{dtm[1]}',whitec)
    dsp.draw_rectangle(0,10,240,12,whitec)
    a=screenModeNames[screenMode]
    dsp.draw_text8x8(int((240-len(a)*9+1)/2),12,a,whitec)
    dsp.draw_text8x8(0,24,'Brightness:',whitec)
    dsp.draw_hline(10,40,220,whitec)
    dsp.fill_circle(int(pixParams[0]*220),40,5,whitec)
    if screenMode<=11:
        dsp.draw_rectangle(0,300,240,20,whitec)
        dsp.draw_text8x8(84,306,'Run mode',whitec)
#settings touch processing
def settings_touch(x,y):
    global screenMode,colorPickerData,numKeyData,screenMode,screenModePickerActive
    if y>=10 and y<=22:
        screenMode_picker_UI()
        screenModePickerActive=True
    elif y>=35 and y<=45 and x>=10 and x <=230:
        pixParams[0]=(x-10)/220
        print(pixParams[0])
        display_settings()
display_settings()
lm=rtc.datetime()[5]
while True:
    dtm=rtc.datetime()
    if lm!=dtm[5]:
        lm=dtm[5]
        weekdays=['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
        dsp.fill_hrect(0,0,240,8,0)
        dsp.draw_text8x8(0,0,f'{dtm[4]}:{dtm[5]} {weekdays[dtm[3]]} {dtm[2]}/{dtm[1]}',color565(255,255,255))
    if touch[0]:
        touch[0]=False
        #print(touch[1],touch[2],'Sound lvl:',sound.read_u16() )
        if colorPickerData[0]:
            color_picker_touch(touch[1],touch[2])
            print(pixColors)
        elif numKeyData[0]:
            numKey_touch(touch[1],touch[2])
        elif screenModePickerActive:
            screenMode_picker_touch(touch[1],touch[2])
        else:
            settings_touch(touch[1],touch[2])
    sleep(0.1)